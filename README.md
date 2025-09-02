# Toggl MCP Server

[![PyPI version](https://badge.fury.io/py/toggl-mcp.svg)](https://pypi.org/project/toggl-mcp/)

MCP server for [Toggl](https://engineering.toggl.com/docs/index.html)

## Prerequisites

- [`uvx`](https://docs.astral.sh/uv/guides/tools/)

## Configuration

### Cursor

Add to `~/.cursor/mcp.json`:

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

### Claude Code

```bash
claude mcp add toggl-mcp -s user \
  --command uvx \
  --args toggl-mcp \
  --env TOGGL_API_TOKEN=YOUR_API_TOKEN \
  --env TOGGL_WORKSPACE_ID=YOUR_WORKSPACE_ID
```

## License

MIT