#!/usr/bin/env python3
"""
Toggl MCP Server - A Model Context Protocol server for Toggl API integration
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dateutil import parser

from mcp.server.fastmcp import FastMCP
from .toggl_client import TogglClient


# Initialize FastMCP server
mcp = FastMCP("toggl-mcp")

# Global variables
toggl_client: Optional[TogglClient] = None
default_workspace_id: Optional[int] = None


def get_workspace_id(workspace_id: Optional[int] = None) -> int:
    """Helper to get workspace ID from arguments or default"""
    if workspace_id:
        return workspace_id
    if default_workspace_id:
        return default_workspace_id
    raise ValueError("No workspace_id provided and no default workspace set")


# User & Workspace Tools
@mcp.tool()
async def toggl_get_user() -> Dict[str, Any]:
    """Get current Toggl user information"""
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    return await toggl_client.get_me()


@mcp.tool()
async def toggl_list_workspaces() -> List[Dict[str, Any]]:
    """List all available Toggl workspaces"""
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    return await toggl_client.get_workspaces()


@mcp.tool()
async def toggl_list_organizations() -> List[Dict[str, Any]]:
    """List user's organizations"""
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    return await toggl_client.get_organizations()


# Project Tools
@mcp.tool()
async def toggl_list_projects(workspace_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """List all projects in a workspace
    
    Args:
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    wid = get_workspace_id(workspace_id)
    return await toggl_client.get_projects(wid)


@mcp.tool()
async def toggl_create_project(
    name: str,
    workspace_id: Optional[int] = None,
    client_id: Optional[int] = None,
    color: Optional[str] = None,
    is_private: Optional[bool] = None
) -> Dict[str, Any]:
    """Create a new project in a workspace
    
    Args:
        name: Project name
        workspace_id: Workspace ID (uses default if not provided)
        client_id: Client ID (optional)
        color: Project color in hex format (optional)
        is_private: Whether the project is private (optional)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    wid = get_workspace_id(workspace_id)
    kwargs = {}
    if client_id is not None:
        kwargs["client_id"] = client_id
    if color is not None:
        kwargs["color"] = color
    if is_private is not None:
        kwargs["is_private"] = is_private
    return await toggl_client.create_project(wid, name, **kwargs)


# Time Entry Tools
@mcp.tool()
async def toggl_list_time_entries(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List time entries within a date range
    
    Args:
        start_date: Start date (ISO 8601 format, defaults to 7 days ago)
        end_date: End date (ISO 8601 format, defaults to today)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    end = end_date or datetime.now().isoformat()
    start = start_date or (datetime.now() - timedelta(days=7)).isoformat()
    return await toggl_client.get_time_entries(start, end)


@mcp.tool()
async def toggl_get_current_timer() -> Dict[str, Any]:
    """Get the currently running time entry"""
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    result = await toggl_client.get_current_time_entry()
    return result if result else {"message": "No timer currently running"}


@mcp.tool()
async def toggl_start_timer(
    description: str,
    workspace_id: Optional[int] = None,
    project_id: Optional[int] = None,
    tags: Optional[List[str]] = None,
    billable: Optional[bool] = None
) -> Dict[str, Any]:
    """Start a new time entry (timer)
    
    Args:
        description: Time entry description
        workspace_id: Workspace ID (uses default if not provided)
        project_id: Project ID (optional)
        tags: List of tag names (optional)
        billable: Whether the time entry is billable (optional)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    wid = get_workspace_id(workspace_id)
    kwargs = {
        "start": datetime.now().isoformat() + "Z",
        "duration": -1  # Negative duration indicates running
    }
    if project_id is not None:
        kwargs["project_id"] = project_id
    if tags is not None:
        kwargs["tags"] = tags
    if billable is not None:
        kwargs["billable"] = billable
    return await toggl_client.create_time_entry(wid, description, **kwargs)


@mcp.tool()
async def toggl_stop_timer(
    time_entry_id: int,
    workspace_id: Optional[int] = None
) -> Dict[str, Any]:
    """Stop a running time entry
    
    Args:
        time_entry_id: Time entry ID to stop
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    wid = get_workspace_id(workspace_id)
    return await toggl_client.stop_time_entry(wid, time_entry_id)


@mcp.tool()
async def toggl_create_time_entry(
    description: str,
    start: str,
    stop: str,
    workspace_id: Optional[int] = None,
    project_id: Optional[int] = None,
    tags: Optional[List[str]] = None,
    billable: Optional[bool] = None
) -> Dict[str, Any]:
    """Create a completed time entry with specific start and stop times
    
    Args:
        description: Time entry description
        start: Start time (ISO 8601 format)
        stop: Stop time (ISO 8601 format)
        workspace_id: Workspace ID (uses default if not provided)
        project_id: Project ID (optional)
        tags: List of tag names (optional)
        billable: Whether the time entry is billable (optional)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    wid = get_workspace_id(workspace_id)
    kwargs = {"start": start, "stop": stop}
    
    # Calculate duration
    start_dt = parser.parse(start)
    stop_dt = parser.parse(stop)
    kwargs["duration"] = int((stop_dt - start_dt).total_seconds())
    
    if project_id is not None:
        kwargs["project_id"] = project_id
    if tags is not None:
        kwargs["tags"] = tags
    if billable is not None:
        kwargs["billable"] = billable
    return await toggl_client.create_time_entry(wid, description, **kwargs)


# Tag Tools
@mcp.tool()
async def toggl_list_tags(workspace_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """List all tags in a workspace
    
    Args:
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    wid = get_workspace_id(workspace_id)
    return await toggl_client.get_tags(wid)


@mcp.tool()
async def toggl_create_tag(
    name: str,
    workspace_id: Optional[int] = None
) -> Dict[str, Any]:
    """Create a new tag in a workspace
    
    Args:
        name: Tag name
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    wid = get_workspace_id(workspace_id)
    return await toggl_client.create_tag(wid, name)


# Client Tools
@mcp.tool()
async def toggl_list_clients(workspace_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """List all clients in a workspace
    
    Args:
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    wid = get_workspace_id(workspace_id)
    return await toggl_client.get_clients(wid)


@mcp.tool()
async def toggl_create_client(
    name: str,
    workspace_id: Optional[int] = None
) -> Dict[str, Any]:
    """Create a new client in a workspace
    
    Args:
        name: Client name
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    wid = get_workspace_id(workspace_id)
    return await toggl_client.create_client(wid, name)


# Project Task Tools
@mcp.tool()
async def toggl_list_project_tasks(
    project_id: int,
    workspace_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """List tasks for a project (only if tasks are enabled)
    
    Args:
        project_id: Project ID
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    wid = get_workspace_id(workspace_id)
    return await toggl_client.get_project_tasks(wid, project_id)


@mcp.tool()
async def toggl_create_project_task(
    project_id: int,
    name: str,
    workspace_id: Optional[int] = None
) -> Dict[str, Any]:
    """Create a task for a project
    
    Args:
        project_id: Project ID
        name: Task name
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    wid = get_workspace_id(workspace_id)
    return await toggl_client.create_project_task(wid, project_id, name)


def run():
    """Entry point for the package"""
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
    
    # Run the server
    mcp.run(transport='stdio')


if __name__ == "__main__":
    run()