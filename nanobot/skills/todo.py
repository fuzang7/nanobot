"""Todo skill module for managing tasks in TODO.md file.

This module provides a programmatic interface to the todo functionality.
Note: The actual TodoTools are implemented in `nanobot.agent.tools.todo`.
This module serves as a skill wrapper and example usage.
"""

import asyncio
from pathlib import Path
from typing import Optional

from nanobot.agent.tools.todo import TodoAddTaskTool, TodoListTasksTool, TodoCompleteTaskTool


async def add_task(workspace_path: Path, task: str, priority: str = "NORMAL") -> str:
    """Add a task to TODO.md file.

    Args:
        workspace_path: Path to workspace directory
        task: Task description
        priority: Priority level (LOW, NORMAL, HIGH)

    Returns:
        Status message
    """
    tool = TodoAddTaskTool(workspace_path)
    return await tool.execute(task=task, priority=priority)


async def list_tasks(workspace_path: Path, only_pending: bool = True) -> str:
    """List tasks from TODO.md file.

    Args:
        workspace_path: Path to workspace directory
        only_pending: If True, show only pending tasks

    Returns:
        Tasks as formatted string
    """
    tool = TodoListTasksTool(workspace_path)
    return await tool.execute(only_pending=only_pending)


async def complete_task(workspace_path: Path, task_content: str) -> str:
    """Mark a task as completed in TODO.md file.

    Args:
        workspace_path: Path to workspace directory
        task_content: Task content or substring to match

    Returns:
        Status message
    """
    tool = TodoCompleteTaskTool(workspace_path)
    return await tool.execute(task_content=task_content)


class TodoManager:
    """Manager class for todo operations."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path

    async def add(self, task: str, priority: str = "NORMAL") -> str:
        """Add a task."""
        tool = TodoAddTaskTool(self.workspace_path)
        return await tool.execute(task=task, priority=priority)

    async def list(self, only_pending: bool = True) -> str:
        """List tasks."""
        tool = TodoListTasksTool(self.workspace_path)
        return await tool.execute(only_pending=only_pending)

    async def complete(self, task_content: str) -> str:
        """Complete a task."""
        tool = TodoCompleteTaskTool(self.workspace_path)
        return await tool.execute(task_content=task_content)

    def get_todo_path(self) -> Path:
        """Get path to TODO.md file."""
        return self.workspace_path / "TODO.md"


# Example usage
if __name__ == "__main__":
    async def example():
        workspace = Path.cwd()  # Replace with actual workspace path

        # Create manager
        manager = TodoManager(workspace)

        # Add some tasks
        print(await manager.add("Review project documentation", "HIGH"))
        print(await manager.add("Update test cases", "NORMAL"))
        print(await manager.add("Fix minor UI issues", "LOW"))

        # List pending tasks
        print("\n" + await manager.list(only_pending=True))

        # Complete a task
        print(await manager.complete("Review project documentation"))

        # List all tasks (including completed)
        print("\n" + await manager.list(only_pending=False))

    asyncio.run(example())