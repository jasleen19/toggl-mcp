#!/usr/bin/env python3
"""
Toggl MCP Server - A Model Context Protocol server for Toggl API integration
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from dateutil import parser

from mcp.server.fastmcp import FastMCP
from .toggl_client import TogglClient

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


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
async def toggl_list_projects(workspace_id: Optional[Union[int, str]] = None) -> List[Dict[str, Any]]:
    """List all projects in a workspace
    
    Args:
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    # Convert string to int if needed
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
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
    task_id: Optional[int] = None,
    tags: Optional[List[str]] = None,
    tag_ids: Optional[List[int]] = None,
    billable: Optional[bool] = None,
    created_with: Optional[str] = "toggl-mcp"
) -> Dict[str, Any]:
    """Start a new time entry (timer)
    
    Args:
        description: Time entry description
        workspace_id: Workspace ID (uses default if not provided)
        project_id: Project ID (optional)
        task_id: Task ID for the project (optional)
        tags: List of tag names (optional)
        tag_ids: List of tag IDs (optional)
        billable: Whether the time entry is billable (optional)
        created_with: Source of the time entry (default: "toggl-mcp")
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
    if task_id is not None:
        kwargs["task_id"] = task_id
    if tags is not None:
        kwargs["tags"] = tags
    if tag_ids is not None:
        kwargs["tag_ids"] = tag_ids
    if billable is not None:
        kwargs["billable"] = billable
    if created_with is not None:
        kwargs["created_with"] = created_with
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
    workspace_id: Optional[Union[int, str]] = None,
    project_id: Optional[Union[int, str]] = None,
    task_id: Optional[Union[int, str]] = None,
    tags: Optional[List[str]] = None,
    tag_ids: Optional[List[int]] = None,
    billable: Optional[bool] = None,
    duronly: Optional[bool] = None,
    created_with: Optional[str] = "toggl-mcp"
) -> Dict[str, Any]:
    """Create a completed time entry with specific start and stop times
    
    Args:
        description: Time entry description
        start: Start time (ISO 8601 format, e.g., "2025-08-27T17:00:00Z")
        stop: Stop time (ISO 8601 format, e.g., "2025-08-27T19:00:00Z")
        workspace_id: Workspace ID (uses default if not provided)
        project_id: Project ID (optional)
        task_id: Task ID for the project (optional)
        tags: List of tag names (optional)
        tag_ids: List of tag IDs (optional)
        billable: Whether the time entry is billable (optional)
        duronly: Whether to save only duration, no start/stop times (optional)
        created_with: Source of the time entry (default: "toggl-mcp")
    """
    logger.info(f"Creating time entry: '{description}' from {start} to {stop}")
    logger.debug(f"Parameters: workspace_id={workspace_id}, project_id={project_id}, task_id={task_id}")
    
    if not toggl_client:
        logger.error("Toggl client not initialized")
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    # Convert string IDs to integers
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    if project_id is not None and isinstance(project_id, str):
        project_id = int(project_id)
    if task_id is not None and isinstance(task_id, str):
        task_id = int(task_id)
    
    try:
        wid = get_workspace_id(workspace_id)
        logger.debug(f"Using workspace ID: {wid}")
    except ValueError as e:
        logger.error(f"Workspace ID error: {e}")
        return {"error": str(e)}
    
    kwargs = {"start": start, "stop": stop}
    
    # Calculate duration
    start_dt = parser.parse(start)
    stop_dt = parser.parse(stop)
    kwargs["duration"] = int((stop_dt - start_dt).total_seconds())
    logger.debug(f"Calculated duration: {kwargs['duration']} seconds")
    
    if project_id is not None:
        kwargs["project_id"] = project_id
    if task_id is not None:
        kwargs["task_id"] = task_id
    if tags is not None:
        kwargs["tags"] = tags
    if tag_ids is not None:
        kwargs["tag_ids"] = tag_ids
    if billable is not None:
        kwargs["billable"] = billable
    if duronly is not None:
        kwargs["duronly"] = duronly
    if created_with is not None:
        kwargs["created_with"] = created_with
    
    logger.debug(f"Final kwargs for API call: {kwargs}")
    
    try:
        result = await toggl_client.create_time_entry(wid, description, **kwargs)
        logger.info(f"Successfully created time entry with ID: {result.get('id', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"Failed to create time entry: {e}")
        return {"error": f"Failed to create time entry: {str(e)}"}


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


async def setup_and_run():
    """Setup and run the server"""
    global toggl_client, default_workspace_id
    
    logger.info("Starting Toggl MCP server...")
    
    # Get API token from environment
    api_token = os.getenv("TOGGL_API_TOKEN")
    if not api_token:
        logger.error("TOGGL_API_TOKEN environment variable not set")
        print("Error: TOGGL_API_TOKEN environment variable not set", file=sys.stderr)
        print("Please set your Toggl API token:", file=sys.stderr)
        print("  export TOGGL_API_TOKEN=your_api_token_here", file=sys.stderr)
        sys.exit(1)
    
    logger.info("API token found, initializing Toggl client")
    
    # Initialize Toggl client
    toggl_client = TogglClient(api_token)
    
    # Get default workspace if specified
    workspace_id_str = os.getenv("TOGGL_WORKSPACE_ID")
    if workspace_id_str:
        try:
            default_workspace_id = int(workspace_id_str)
            logger.info(f"Using default workspace ID: {default_workspace_id}")
        except ValueError:
            logger.warning(f"Invalid TOGGL_WORKSPACE_ID '{workspace_id_str}', ignoring")
            print(f"Warning: Invalid TOGGL_WORKSPACE_ID '{workspace_id_str}', ignoring", file=sys.stderr)
    else:
        logger.info("No default workspace ID set")
    
    # Run the server
    logger.info("Starting MCP server on stdio transport")
    await mcp.run_stdio_async()


def run():
    """Entry point for the package"""
    import asyncio
    asyncio.run(setup_and_run())


if __name__ == "__main__":
    run()