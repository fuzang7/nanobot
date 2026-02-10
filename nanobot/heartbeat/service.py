"""Heartbeat service - periodic agent wake-up to check for tasks."""

import asyncio
from pathlib import Path
from typing import Any, Callable, Coroutine

from loguru import logger

# Default interval: 30 minutes
DEFAULT_HEARTBEAT_INTERVAL_S = 30 * 60

# The prompt sent to agent during heartbeat
HEARTBEAT_PROMPT = """Read HEARTBEAT.md in your workspace (if it exists).
Follow any instructions or tasks listed there.
If nothing needs attention, reply with just: HEARTBEAT_OK"""

# Token that indicates "nothing to do"
HEARTBEAT_OK_TOKEN = "HEARTBEAT_OK"


def _is_heartbeat_empty(content: str | None) -> bool:
    """Check if HEARTBEAT.md has no actionable content."""
    if not content:
        return True
    
    # Lines to skip: empty, headers, HTML comments, empty checkboxes
    skip_patterns = {"- [ ]", "* [ ]", "- [x]", "* [x]"}
    
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("<!--") or line in skip_patterns:
            continue
        return False  # Found actionable content
    
    return True


class HeartbeatService:
    """
    Periodic heartbeat service that wakes the agent to check for tasks.
    
    The agent reads HEARTBEAT.md from the workspace and executes any
    tasks listed there. If nothing needs attention, it replies HEARTBEAT_OK.
    """
    
    def __init__(
        self,
        workspace: Path,
        on_heartbeat: Callable[..., Coroutine[Any, Any, str]] | None = None,
        interval_s: int = DEFAULT_HEARTBEAT_INTERVAL_S,
        enabled: bool = True,
        proactive_enabled: bool = False,
        proactive_channel: str = "qq",
        proactive_chat_id: str = "",
    ):
        self.workspace = workspace
        self.on_heartbeat = on_heartbeat
        self.interval_s = interval_s
        self.enabled = enabled
        self.proactive_enabled = proactive_enabled
        self.proactive_channel = proactive_channel
        self.proactive_chat_id = proactive_chat_id
        self._running = False
        self._task: asyncio.Task | None = None
    
    @property
    def heartbeat_file(self) -> Path:
        return self.workspace / "HEARTBEAT.md"
    
    def _read_heartbeat_file(self) -> str | None:
        """Read HEARTBEAT.md content."""
        if self.heartbeat_file.exists():
            try:
                return self.heartbeat_file.read_text()
            except Exception:
                return None
        return None
    
    async def start(self) -> None:
        """Start the heartbeat service."""
        if not self.enabled:
            logger.info("Heartbeat disabled")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"Heartbeat started (every {self.interval_s}s)")
    
    def stop(self) -> None:
        """Stop the heartbeat service."""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
    
    async def _run_loop(self) -> None:
        """Main heartbeat loop."""
        while self._running:
            try:
                await asyncio.sleep(self.interval_s)
                if self._running:
                    await self._tick()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    async def _tick(self) -> None:
        """Execute a single heartbeat tick."""
        # Proactive check: Zero-token check for TODO.md tasks
        todo_path = self.workspace / "TODO.md"

        # Check file existence & content WITHOUT invoking LLM
        if todo_path.exists():
            try:
                content = todo_path.read_text(encoding="utf-8")
            except Exception:
                content = ""

            # Look for unchecked boxes "- [ ]"
            if "- [ ]" in content:
                # Only if tasks exist, wake up the agent
                if self.proactive_enabled and self.proactive_chat_id and self.on_heartbeat:
                    prompt = (
                        f"SYSTEM_WAKEUP: Pending tasks detected in TODO.md:\n\n{content}\n\n"
                        "Instruction: Check these tasks. If action is required, execute it. "
                        "If a task is completed, use 'complete_task' tool to mark it [x]."
                    )
                    logger.info("Proactive heartbeat: pending tasks in TODO.md")

                    try:
                        # Try to call with channel and chat_id parameters (new signature)
                        response = await self.on_heartbeat(prompt, self.proactive_channel, self.proactive_chat_id)
                        logger.info(f"Proactive heartbeat completed: {response[:100] if response else 'no response'}")
                    except TypeError:
                        # Fallback to original signature for compatibility (prompt only)
                        response = await self.on_heartbeat(prompt)
                        logger.info(f"Proactive heartbeat completed (legacy): {response[:100] if response else 'no response'}")

        # Original heartbeat: check HEARTBEAT.md
        content = self._read_heartbeat_file()

        # Skip if HEARTBEAT.md is empty or doesn't exist
        if _is_heartbeat_empty(content):
            logger.debug("Heartbeat: no tasks (HEARTBEAT.md empty)")
            return

        logger.info("Heartbeat: checking for tasks...")

        if self.on_heartbeat:
            try:
                response = await self.on_heartbeat(HEARTBEAT_PROMPT)

                # Check if agent said "nothing to do"
                if HEARTBEAT_OK_TOKEN.replace("_", "") in response.upper().replace("_", ""):
                    logger.info("Heartbeat: OK (no action needed)")
                else:
                    logger.info(f"Heartbeat: completed task")

            except Exception as e:
                logger.error(f"Heartbeat execution failed: {e}")
    
    async def trigger_now(self) -> str | None:
        """Manually trigger a heartbeat."""
        if self.on_heartbeat:
            # Try to call with the original signature first (for backward compatibility)
            try:
                return await self.on_heartbeat(HEARTBEAT_PROMPT)
            except TypeError:
                # If that fails, try with the new signature but with default channel/chat_id
                return await self.on_heartbeat(HEARTBEAT_PROMPT, "cli", "trigger")
        return None
