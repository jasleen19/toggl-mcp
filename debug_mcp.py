#!/usr/bin/env python3
"""Debug script to test MCP server initialization"""

import asyncio
import json
import sys
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Create a minimal test server
server = Server("toggl-test")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List test tools"""
    print("DEBUG: list_tools called", file=sys.stderr)
    tools = [
        Tool(
            name="test_tool",
            description="A test tool",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    print(f"DEBUG: Returning {len(tools)} tools", file=sys.stderr)
    return tools

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    return [TextContent(type="text", text=f"Called {name}")]

async def main():
    print("DEBUG: Starting server", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        print("DEBUG: Got stdio streams", file=sys.stderr)
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="toggl-test",
                server_version="0.1.0",
                capabilities={},
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
