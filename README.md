# Toggl MCP Server

[![PyPI version](https://badge.fury.io/py/toggl-mcp.svg)](https://pypi.org/project/toggl-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/toggl-mcp.svg)](https://pypi.org/project/toggl-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that provides tools for interacting with the Toggl Track API v9. This server allows AI assistants to manage time tracking, projects, tags, and more through a standardized interface.

## Features

The Toggl MCP server provides tools for:

- **User & Workspace Management**: Get user info, list workspaces and organizations
- **Project Management**: Create, list, update, and delete projects
- **Time Tracking**: Start/stop timers, create time entries, list time entries
- **Bulk Operations**: Create, update, and delete multiple time entries at once
- **Tag Management**: Create, list, update, and delete tags
- **Client Management**: Create and list clients
- **Task Management**: List and create project tasks (if enabled for the project)

## Installation

Install the package using `uvx`:

```bash
uvx toggl-mcp
```

## Configuration

### Environment Variables

The server requires the following environment variables:

- `TOGGL_API_TOKEN` (required): Your Toggl API token
- `TOGGL_WORKSPACE_ID` (optional): Default workspace ID to use for operations

### Getting Your API Token

1. Log in to your Toggl Track account
2. Go to Profile Settings
3. Scroll down to "API Token" section
4. Copy your API token

### Finding Your Workspace ID

1. Use the `toggl_list_workspaces` tool after setting up the server
2. Note the ID of the workspace you want to use as default

## Usage with Claude Desktop

Add the following to your Claude Desktop configuration file:

### macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
### Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "toggl-mcp": {
      "command": "uvx",
      "args": ["toggl-mcp"],
      "env": {
        "TOGGL_API_TOKEN": "your_api_token_here",
        "TOGGL_WORKSPACE_ID": "optional_default_workspace_id"
      }
    }
  }
}
```

## Available Tools

### User & Workspace Tools

- `toggl_get_user`: Get current user information
- `toggl_list_workspaces`: List all available workspaces
- `toggl_list_organizations`: List user's organizations

### Project Tools

- `toggl_list_projects`: List all projects in a workspace
- `toggl_create_project`: Create a new project
  - Parameters: `name` (required), `workspace_id`, `client_id`, `color`, `is_private`

### Time Entry Tools

- `toggl_list_time_entries`: List time entries within a date range
  - Parameters: `start_date`, `end_date` (defaults to last 7 days)
- `toggl_get_current_timer`: Get the currently running time entry
- `toggl_start_timer`: Start a new timer
  - Parameters: `description` (required), `workspace_id`, `project_id`, `tags`, `billable`
- `toggl_stop_timer`: Stop a running time entry
  - Parameters: `time_entry_id` (required), `workspace_id`
- `toggl_create_time_entry`: Create a completed time entry
  - Parameters: `description`, `start`, `stop` (all required), `workspace_id`, `project_id`, `tags`, `billable`

### Tag Tools

- `toggl_list_tags`: List all tags in a workspace
- `toggl_create_tag`: Create a new tag
  - Parameters: `name` (required), `workspace_id`

### Client Tools

- `toggl_list_clients`: List all clients in a workspace
- `toggl_create_client`: Create a new client
  - Parameters: `name` (required), `workspace_id`

### Bulk Operation Tools

- `toggl_bulk_create_time_entries`: Create multiple time entries at once
  - Parameters: `time_entries` (array, required), `workspace_id`
- `toggl_bulk_update_time_entries`: Update multiple time entries at once
  - Parameters: `time_entry_ids` (array, required), `updates` (object, required), `workspace_id`
- `toggl_bulk_delete_time_entries`: Delete multiple time entries at once
  - Parameters: `time_entry_ids` (array, required), `workspace_id`

### Project Task Tools

- `toggl_list_project_tasks`: List tasks for a project (only if tasks are enabled)
  - Parameters: `project_id` (required), `workspace_id`
- `toggl_create_project_task`: Create a task for a project
  - Parameters: `project_id` (required), `name` (required), `workspace_id`

## Example Usage

Here are some example prompts you can use with Claude:

1. "Show me my Toggl workspaces"
2. "List my time entries from the last week"
3. "Start a timer for 'Working on documentation' in my default workspace"
4. "Create a new project called 'Website Redesign' with the client 'Acme Corp'"
5. "What timer am I currently tracking?"
6. "Stop the current timer"
7. "Create a tag called 'billable'"
8. "Show me all projects in workspace 123456"

## Development

### Project Structure

```
toggl-mcp/
├── main.py          # Main MCP server entry point
├── toggl_client.py  # Toggl API client implementation
├── tools.py         # Tool definitions and handlers
├── pyproject.toml   # Project configuration
└── README.md        # This file
```

### Running Locally

1. Clone the repository
2. Install dependencies: `pip install -e .`
3. Set environment variables:
   ```bash
   export TOGGL_API_TOKEN=your_api_token_here
   export TOGGL_WORKSPACE_ID=your_workspace_id  # optional
   ```
4. Run the server: `python main.py`

### Adding New Tools

To add new tools:

1. Add the API method to `toggl_client.py`
2. Define the tool schema in `tools.py` in the `get_all_tools()` function
3. Add the handler logic in `tools.py` in the `handle_tool_call()` function

### Testing

The project includes comprehensive test scripts:

1. **Test Connection** (`test_connection.py`): Verify API token and basic connectivity
   ```bash
   python test_connection.py
   ```

2. **Test All Operations** (`test_all_operations.py`): Test all API operations directly
   ```bash
   python test_all_operations.py
   ```

3. **Test MCP Tools** (`test_mcp_tools.py`): Test all tools through the MCP interface
   ```bash
   python test_mcp_tools.py
   ```

All test scripts will create temporary data (projects, time entries, etc.) and clean up after themselves.

## API Reference

This server implements tools for the [Toggl Track API v9](https://engineering.toggl.com/docs/index.html).

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
