#!/usr/bin/env python3 -u
"""Simple MCP test server"""

import asyncio
import os
import sys

# Force unbuffered
os.environ['PYTHONUNBUFFERED'] = '1'

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

print("Starting simple test server...", file=sys.stderr)

server = Server("toggl-simple")

@server.list_tools()
async def list_tools() -> list[Tool]:
    tools = [
        Tool(
            name="toggl_test",
            description="Test tool",
            inputSchema={"type": "object", "properties": {}}
        )
    ]
    print(f"Returning {len(tools)} tools", file=sys.stderr)
    return tools

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    return [TextContent(type="text", text=f"Test response from {name}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="toggl-simple",
                server_version="0.1.0",
                capabilities={},
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
