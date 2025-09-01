# Setting up Toggl MCP in Cursor

## Method 1: Using uvx (Recommended)

In Cursor settings, add this MCP configuration:

```json
{
  "toggl-mcp": {
    "command": "uvx",
    "args": ["toggl-mcp"],
    "env": {
      "TOGGL_API_TOKEN": "your_actual_toggl_api_token",
      "TOGGL_WORKSPACE_ID": "your_workspace_id"
    }
  }
}
```

## Method 2: Using Python directly

If uvx doesn't work, try using Python directly:

```json
{
  "toggl-mcp": {
    "command": "python3",
    "args": ["-m", "toggl_mcp"],
    "env": {
      "TOGGL_API_TOKEN": "your_actual_toggl_api_token",
      "TOGGL_WORKSPACE_ID": "your_workspace_id"
    }
  }
}
```

## Method 3: Using the main.py file directly

If the package installation doesn't work, use the source directly:

```json
{
  "toggl-mcp": {
    "command": "python3",
    "args": ["/path/to/toggl-mcp/main.py"],
    "env": {
      "TOGGL_API_TOKEN": "your_actual_toggl_api_token",
      "TOGGL_WORKSPACE_ID": "your_workspace_id"
    }
  }
}
```

## Troubleshooting Steps

1. **Check if toggl-mcp is installed:**
   ```bash
   pip show toggl-mcp
   ```

2. **Test the command manually:**
   ```bash
   TOGGL_API_TOKEN=your_token uvx toggl-mcp
   ```

3. **Check Cursor logs:**
   - Open Cursor Developer Tools (View > Toggle Developer Tools)
   - Check Console for MCP-related errors

4. **Verify Python path:**
   ```bash
   which python3
   ```

## Common Issues

- **"No tools" error**: Usually means the MCP server isn't starting
- **Permission denied**: Make sure the command is executable
- **Module not found**: Package might not be installed in the right Python environment
