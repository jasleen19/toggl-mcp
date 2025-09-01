# Toggl MCP Tools Documentation

This document provides comprehensive documentation for all available tools in the Toggl MCP server, including all parameters with their types and whether they are required or optional.

## Tool Categories

## User & Workspace Management

### `toggl_get_user`

**Description:** Get current Toggl user information

**Parameters:**
_This tool requires no parameters._

### `toggl_list_workspaces`

**Description:** List all available Toggl workspaces

**Parameters:**
_This tool requires no parameters._

### `toggl_list_organizations`

**Description:** List user's organizations

**Parameters:**
_This tool requires no parameters._

## Project Management

### `toggl_list_projects`

**Description:** List all projects in a workspace

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace_id` | int | ❌ No | Workspace ID (uses default if not provided) |

### `toggl_create_project`

**Description:** Create a new project in a workspace

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | str | ✅ Yes | Project name |
| `workspace_id` | int | ❌ No | Workspace ID (uses default if not provided) |
| `client_id` | int | ❌ No | Client ID (optional) |
| `color` | str | ❌ No | Project color in hex format (optional) |
| `is_private` | bool | ❌ No | Whether the project is private (optional) |

## Time Entry Management

### `toggl_list_time_entries`

**Description:** List time entries within a date range

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | str | ❌ No | Start date (ISO 8601 format, defaults to 7 days ago) |
| `end_date` | str | ❌ No | End date (ISO 8601 format, defaults to today) |

### `toggl_create_time_entry`

**Description:** Create a completed time entry with specific start and stop times

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | str | ✅ Yes | Time entry description |
| `start` | str | ✅ Yes | Start time (ISO 8601 format, e.g., "2025-08-27T17:00:00Z") |
| `stop` | str | ✅ Yes | Stop time (ISO 8601 format, e.g., "2025-08-27T19:00:00Z") |
| `workspace_id` | int | ❌ No | Workspace ID (uses default if not provided) |
| `project_id` | int | ❌ No | Project ID (optional) |
| `task_id` | int | ❌ No | Task ID for the project (optional) |
| `tags` | array<str> | ❌ No | List of tag names (optional) |
| `tag_ids` | array<int> | ❌ No | List of tag IDs (optional) |
| `billable` | bool | ❌ No | Whether the time entry is billable (optional) |
| `duronly` | bool | ❌ No | Whether to save only duration, no start/stop times (optional) |
| `created_with` | str | ❌ No | Source of the time entry (default: "toggl-mcp") |

## Timer Controls

### `toggl_get_current_timer`

**Description:** Get the currently running time entry

**Parameters:**
_This tool requires no parameters._

### `toggl_start_timer`

**Description:** Start a new time entry (timer)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | str | ✅ Yes | Time entry description |
| `workspace_id` | int | ❌ No | Workspace ID (uses default if not provided) |
| `project_id` | int | ❌ No | Project ID (optional) |
| `task_id` | int | ❌ No | Task ID for the project (optional) |
| `tags` | array<str> | ❌ No | List of tag names (optional) |
| `tag_ids` | array<int> | ❌ No | List of tag IDs (optional) |
| `billable` | bool | ❌ No | Whether the time entry is billable (optional) |
| `created_with` | str | ❌ No | Source of the time entry (default: "toggl-mcp") |

### `toggl_stop_timer`

**Description:** Stop a running time entry

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `time_entry_id` | int | ✅ Yes | Time entry ID to stop |
| `workspace_id` | int | ❌ No | Workspace ID (uses default if not provided) |

## Tag Management

### `toggl_list_tags`

**Description:** List all tags in a workspace

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace_id` | int | ❌ No | Workspace ID (uses default if not provided) |

### `toggl_create_tag`

**Description:** Create a new tag in a workspace

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | str | ✅ Yes | Tag name |
| `workspace_id` | int | ❌ No | Workspace ID (uses default if not provided) |

## Client Management

### `toggl_list_clients`

**Description:** List all clients in a workspace

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace_id` | int | ❌ No | Workspace ID (uses default if not provided) |

### `toggl_create_client`

**Description:** Create a new client in a workspace

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | str | ✅ Yes | Client name |
| `workspace_id` | int | ❌ No | Workspace ID (uses default if not provided) |

## Task Management

### `toggl_list_project_tasks`

**Description:** List tasks for a project (only if tasks are enabled)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | int | ✅ Yes | Project ID |
| `workspace_id` | int | ❌ No | Workspace ID (uses default if not provided) |

### `toggl_create_project_task`

**Description:** Create a task for a project

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | int | ✅ Yes | Project ID |
| `name` | str | ✅ Yes | Task name |
| `workspace_id` | int | ❌ No | Workspace ID (uses default if not provided) |

## Usage Examples

### Starting a Timer
```json
{
  "tool": "toggl_start_timer",
  "arguments": {
    "description": "Working on API documentation",
    "project_id": 12345,
    "task_id": 67890,
    "tags": ["documentation", "api"],
    "billable": true
  }
}
```

### Creating a Time Entry
```json
{
  "tool": "toggl_create_time_entry",
  "arguments": {
    "description": "Code review",
    "start": "2025-01-03T09:00:00Z",
    "stop": "2025-01-03T10:30:00Z",
    "workspace_id": 9361160,
    "project_id": 12345,
    "task_id": 67890,
    "billable": true,
    "tags": ["review", "backend"]
  }
}
```

**Note:** 
1. The `workspace_id` parameter is required. Either:
   - Include it in your request (e.g., `"workspace_id": 9361160`)
   - Or set `TOGGL_WORKSPACE_ID` environment variable in your Cursor configuration

2. Some workspaces have **time entry constraints** that require additional fields:
   - If you get error: `"Please fill in all required field(s) to save: project and task"`
   - This means the workspace requires both `project_id` and `task_id`
   - Use `toggl_list_projects` to find project IDs
   - Use `toggl_list_project_tasks` to find task IDs for a project

### Listing Time Entries
```json
{
  "tool": "toggl_list_time_entries",
  "arguments": {
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-01-03T23:59:59Z"
  }
}
```

## Parameter Types Reference

- **str**: String value (text)
- **int**: Integer number
- **bool**: Boolean value (true/false)
- **array<str>**: Array of strings
- **array<int>**: Array of integers

## Important Notes

1. **Workspace ID**: Most tools accept an optional `workspace_id` parameter. If not provided, the default workspace from the `TOGGL_WORKSPACE_ID` environment variable will be used. **If neither is provided, you'll get an error: "No workspace_id provided and no default workspace set"**

2. **Date/Time Format**: All date and time parameters must be in ISO 8601 format (e.g., "2025-01-03T14:30:00Z")

3. **IDs vs Names**: When referencing projects, tasks, or tags, you typically need to use their numeric IDs, not names. Use the list tools to find the appropriate IDs.

4. **Running Timers**: To start a timer (running time entry), use `toggl_start_timer`. The timer will continue running until you call `toggl_stop_timer`.

5. **Task IDs**: Tasks are only available for projects that have tasks enabled. Not all projects support tasks.

6. **Tag IDs vs Tag Names**: You can use either `tags` (array of tag names) or `tag_ids` (array of tag IDs). If both are provided, both will be used.

7. **Created With**: The `created_with` parameter helps identify the source of time entries. It defaults to "toggl-mcp" but can be customized.

8. **Time Entry Constraints**: Some workspaces enforce constraints on time entries:
   - **project_present**: Requires a project_id
   - **task_present**: Requires a task_id (only for projects with tasks enabled)
   - **tag_present**: Requires at least one tag
   - **description_present**: Requires a description
   - Check workspace settings or watch for "Please fill in all required field(s)" errors

## Toggl API Parameter Mapping

This MCP server implements a subset of the Toggl Track API v9 parameters. Here's what's currently supported:

### Time Entry Parameters
- ✅ `description` - Time entry description
- ✅ `workspace_id` (`wid`) - Workspace ID
- ✅ `project_id` (`pid`) - Project ID
- ✅ `task_id` (`tid`) - Task ID
- ✅ `start` - Start time
- ✅ `stop` - Stop time
- ✅ `duration` - Duration in seconds (calculated automatically)
- ✅ `tags` - Tag names
- ✅ `tag_ids` - Tag IDs
- ✅ `billable` - Billable flag
- ✅ `created_with` - Client identifier
- ✅ `duronly` - Duration only mode
- ❌ `user_id` (`uid`) - Not yet implemented
- ❌ `shared_with_user_ids` - Not yet implemented
- ❌ `expense_ids` - Not yet implemented
- ❌ `event_metadata` - Not yet implemented

### Project Parameters
- ✅ `name` - Project name
- ✅ `workspace_id` (`wid`) - Workspace ID
- ✅ `client_id` (`cid`) - Client ID
- ✅ `color` - Color in hex format
- ✅ `is_private` - Privacy flag
- ❌ `active` - Not yet implemented
- ❌ `billable` - Not yet implemented (project-level default)
- ❌ `auto_estimates` - Not yet implemented
- ❌ `estimated_hours` - Not yet implemented
- ❌ `rate` - Not yet implemented

For parameters not yet implemented, please submit a feature request or contribute to the project!