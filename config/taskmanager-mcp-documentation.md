# TaskManager MCP Documentation

## Overview
The TaskManager MCP provides comprehensive task management capabilities for project workflow orchestration, task decomposition, and approval workflows.

## Server Configuration
```json
"taskmanager": {
  "command": "uvx",
  "args": ["mcp-taskmanager"]
}
```

## Available Tools

### 1. request_planning
**Description:** Register a new user request and plan its associated tasks.
**Usage:** Initial project planning and task breakdown

### 2. get_next_task
**Description:** Given a 'requestId', return the next pending task (not done yet).
**Usage:** Workflow progression and task queue management

### 3. mark_task_done
**Description:** Mark a given task as done after you've completed it.
**Usage:** Task completion tracking

### 4. approve_task_completion
**Description:** Once the assistant has marked a task as done using 'mark_task_done', this tool finalizes the completion.
**Usage:** Quality assurance and approval workflows

### 5. approve_request_completion
**Description:** After all tasks are done and approved, this tool finalizes the entire request.
**Usage:** Project completion and closure

### 6. open_task_details
**Description:** Get details of a specific task by 'taskId'. This is for inspecting task information.
**Usage:** Task inspection and detailed review

### 7. list_requests
**Description:** List all requests with their basic information and summary of tasks.
**Usage:** Project overview and status monitoring

### 8. add_tasks_to_request
**Description:** Add new tasks to an existing request. This allows extending a request with additional tasks.
**Usage:** Dynamic project scope expansion

### 9. update_task
**Description:** Update an existing task's title and/or description. Only uncompleted tasks can be updated.
**Usage:** Task refinement and scope adjustment

### 10. delete_task
**Description:** Delete a specific task from a request. Only uncompleted tasks can be deleted.
**Usage:** Task removal and scope reduction

## Best Practices

1. **Workflow Orchestration**: Use for multi-step workflows and complex project planning
2. **Task Decomposition**: Break down large projects into manageable tasks
3. **Approval Workflows**: Implement quality gates with approval mechanisms
4. **Progress Tracking**: Monitor project status and completion rates
5. **Dynamic Planning**: Adjust project scope with add/update/delete operations

## Integration Patterns

- **With Sequential Thinking**: Complex analysis feeds into structured task planning
- **With Persistent Knowledge Graph**: Task completions update long-term project intelligence
- **With Memory MCP**: Session context maintains task workflow continuity
- **With Puppeteer**: Automated testing tasks and validation workflows

## Priority Level
**#4 Priority** in the MCP hierarchy - Workflow orchestration under Knowledge Graph supervision