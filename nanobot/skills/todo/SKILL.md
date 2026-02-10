---
name: todo
description: Manage tasks in a TODO.md file
author: nanobot
version: 1.0.0
created: 2026-02-10
updated: 2026-02-10
tags:
  - productivity
  - task-management
  - organization
requires: []
---

# Todo Skill

This skill enables the agent to manage tasks in a `TODO.md` file located in the workspace root. It provides functionality to add, list, and complete tasks.

## Tools

The agent can use three separate tools for todo management:

### 1. `add_task` - Add a new task
```json
{
  "task": "Write documentation for the new feature",
  "priority": "HIGH"
}
```

Valid priority values: `LOW`, `NORMAL`, `HIGH` (default: `NORMAL`)

### 2. `list_tasks` - List tasks
```json
{
  "only_pending": true
}
```

Set `only_pending` to `false` to show all tasks (including completed ones).

### 3. `complete_task` - Mark a task as completed
```json
{
  "task_content": "Write documentation for the new feature"
}
```

Note: The `task_content` parameter should contain a substring that matches the task description in the TODO.md file.

## File Format

Tasks are stored in `workspace/TODO.md` in the following format:
```
# TODO

- [ ] [HIGH] Write documentation for the new feature
- [ ] [NORMAL] Review pull request #42
- [x] [HIGH] Fix critical bug in login system
```

- `[ ]` indicates pending tasks
- `[x]` indicates completed tasks
- `[PRIORITY]` indicates task priority (LOW, NORMAL, HIGH)

## Examples

### Adding a task
User: "Please add 'update dependencies' to the todo list with high priority"
Agent uses `add_task` tool:
```json
{
  "task": "update dependencies",
  "priority": "HIGH"
}
```

### Listing pending tasks
User: "What tasks do I have pending?"
Agent uses `list_tasks` tool:
```json
{
  "only_pending": true
}
```

### Completing a task
User: "Mark 'update dependencies' as completed"
Agent uses `complete_task` tool:
```json
{
  "task_content": "update dependencies"
}
```

## Notes

- The TODO.md file is created automatically when adding the first task
- Task matching for completion is substring-based (case-sensitive)
- This tool helps save tokens by providing a lightweight task management system
- Tasks are persisted in the workspace for future reference