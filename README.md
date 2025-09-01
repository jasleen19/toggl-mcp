# Toggl MCP Server

[![PyPI version](https://badge.fury.io/py/toggl-mcp.svg)](https://pypi.org/project/toggl-mcp/)

MCP server for [Toggl Track API v9](https://engineering.toggl.com/docs/index.html).

## Installation

Requires [`uvx`](https://docs.astral.sh/uv/guides/tools/).

```bash
uvx toggl-mcp
```

## Configuration

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "toggl-mcp": {
      "command": "uvx",
      "args": ["toggl-mcp"],
      "env": {
        "TOGGL_API_TOKEN": "YOUR_API_TOKEN",
        "TOGGL_WORKSPACE_ID": "YOUR_WORKSPACE_ID"
      }
    }
  }
}
```

### Claude Desktop

Add to config file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "toggl-mcp": {
      "command": "uvx",
      "args": ["toggl-mcp"],
      "env": {
        "TOGGL_API_TOKEN": "YOUR_API_TOKEN",
        "TOGGL_WORKSPACE_ID": "YOUR_WORKSPACE_ID"
      }
    }
  }
}
```

## License

MIT