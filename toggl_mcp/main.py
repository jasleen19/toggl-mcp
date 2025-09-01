#!/usr/bin/env python3
"""
Toggl MCP Server - A Model Context Protocol server for Toggl API integration
"""

import asyncio
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .toggl_client import TogglClient
from .tools import get_all_tools, handle_tool_call


# Global variables
toggl_client: Optional[TogglClient] = None
default_workspace_id: Optional[int] = None


def create_toggl_server() -> Server:
    """Create and configure the MCP server"""
    server = Server("toggl-mcp")
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List all available Toggl tools"""
        return get_all_tools()
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls"""
        if not toggl_client:
            return [TextContent(
                type="text",
                text="Error: Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."
            )]
        
        try:
            result = await handle_tool_call(toggl_client, default_workspace_id, name, arguments)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    return server


async def main():
    """Main entry point for the MCP server"""
    global toggl_client, default_workspace_id
    
    # Get API token from environment
    api_token = os.getenv("TOGGL_API_TOKEN")
    if not api_token:
        print("Error: TOGGL_API_TOKEN environment variable not set", file=sys.stderr)
        print("Please set your Toggl API token:", file=sys.stderr)
        print("  export TOGGL_API_TOKEN=your_api_token_here", file=sys.stderr)
        sys.exit(1)
    
    # Initialize Toggl client
    toggl_client = TogglClient(api_token)
    
    # Get default workspace if specified
    workspace_id_str = os.getenv("TOGGL_WORKSPACE_ID")
    if workspace_id_str:
        try:
            default_workspace_id = int(workspace_id_str)
        except ValueError:
            print(f"Warning: Invalid TOGGL_WORKSPACE_ID '{workspace_id_str}', ignoring", file=sys.stderr)
    
    # Create and run the server
    server = create_toggl_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="toggl-mcp",
                server_version="0.1.0",
            ),
        )
    
    # Cleanup
    if toggl_client:
        await toggl_client.close()


def run():
    """Entry point for the package"""
    asyncio.run(main())


if __name__ == "__main__":
    run()
