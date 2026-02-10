"""Todo tools for managing tasks in a TODO.md file."""

import os
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool


class TodoAddTaskTool(Tool):
    """Tool to add a task to TODO.md file."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.todo_file_path = workspace_path / "TODO.md"

    @property
    def name(self) -> str:
        return "add_task"

    @property
    def description(self) -> str:
        return "Add a task to TODO.md file in workspace root."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Task description",
                    "minLength": 1
                },
                "priority": {
                    "type": "string",
                    "description": "Task priority: 'LOW', 'NORMAL', 'HIGH' (default: 'NORMAL')",
                    "enum": ["LOW", "NORMAL", "HIGH"],
                    "default": "NORMAL"
                }
            },
            "required": ["task"]
        }

    async def execute(self, task: str, priority: str = "NORMAL", **kwargs: Any) -> str:
        """Add a new task to TODO.md."""
        try:
            # Ensure TODO.md exists
            if not self.todo_file_path.exists():
                self.todo_file_path.write_text("# TODO\n\n", encoding="utf-8")

            # Append task
            with open(self.todo_file_path, "a", encoding="utf-8") as f:
                f.write(f"- [ ] [{priority}] {task}\n")

            return f"Task added: '{task}' with priority {priority}"
        except Exception as e:
            return f"Error adding task: {str(e)}"


class TodoListTasksTool(Tool):
    """Tool to list tasks from TODO.md file."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.todo_file_path = workspace_path / "TODO.md"

    @property
    def name(self) -> str:
        return "list_tasks"

    @property
    def description(self) -> str:
        return "List tasks from TODO.md file in workspace root."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "only_pending": {
                    "type": "boolean",
                    "description": "Show only pending tasks (default: true)",
                    "default": True
                }
            }
        }

    async def execute(self, only_pending: bool = True, **kwargs: Any) -> str:
        """List tasks from TODO.md."""
        try:
            if not self.todo_file_path.exists():
                return "No TODO.md file found. No tasks to list."

            content = self.todo_file_path.read_text(encoding="utf-8")
            lines = content.splitlines()

            if only_pending:
                # Filter for lines containing "- [ ]"
                pending_lines = [line for line in lines if "- [ ]" in line]
                if not pending_lines:
                    return "No pending tasks found."
                return "Pending tasks:\n" + "\n".join(pending_lines)
            else:
                # Return all lines
                if not lines:
                    return "TODO.md is empty."
                return "All tasks:\n" + "\n".join(lines)
        except Exception as e:
            return f"Error listing tasks: {str(e)}"


class TodoCompleteTaskTool(Tool):
    """Tool to mark a task as completed in TODO.md file."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.todo_file_path = workspace_path / "TODO.md"

    @property
    def name(self) -> str:
        return "complete_task"

    @property
    def description(self) -> str:
        return "Mark a task as completed in TODO.md file."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_content": {
                    "type": "string",
                    "description": "Task content or substring to match",
                    "minLength": 1
                }
            },
            "required": ["task_content"]
        }

    async def execute(self, task_content: str, **kwargs: Any) -> str:
        """Mark a task as completed in TODO.md."""
        try:
            if not self.todo_file_path.exists():
                return "Error: TODO.md file not found."

            content = self.todo_file_path.read_text(encoding="utf-8")
            lines = content.splitlines()

            # Find the line matching the task content
            found = False
            for i, line in enumerate(lines):
                if task_content in line and "- [ ]" in line:
                    # Replace "- [ ]" with "- [x]"
                    lines[i] = line.replace("- [ ]", "- [x]")
                    found = True
                    break

            if not found:
                return f"Error: Task containing '{task_content}' not found in TODO.md"

            # Write back the modified content
            self.todo_file_path.write_text("\n".join(lines), encoding="utf-8")
            return f"Task marked as completed: '{task_content}'"
        except Exception as e:
            return f"Error completing task: {str(e)}"