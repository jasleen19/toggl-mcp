#!/usr/bin/env python3
"""
Toggl MCP Server - A Model Context Protocol server for Toggl API integration
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Union
from dateutil import parser  # type: ignore
import pytz  # type: ignore
import httpx  # type: ignore

from mcp.server.fastmcp import FastMCP  # type: ignore
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



def to_bool(value: Any) -> Optional[bool]:
    """Convert various types to boolean.
    
    Args:
        value: Can be bool, string, number, or None
        
    Returns:
        Boolean value or None if input is None
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower_val = value.lower()
        if lower_val in ('true', '1', 'yes', 'y', 'on'):
            return True
        elif lower_val in ('false', '0', 'no', 'n', 'off', ''):
            return False
        else:
            # Try to parse as number
            try:
                return bool(int(value))
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to boolean")
    if isinstance(value, (int, float)):
        return bool(value)
    return bool(value)


def to_utc_string(dt_str: Optional[str] = None, user_timezone: Optional[str] = None) -> str:
    """Convert a datetime string to UTC format required by Toggl API.
    
    Args:
        dt_str: Datetime string (if None, uses current UTC time)
        user_timezone: User's timezone (e.g., 'America/New_York', 'Europe/London')
                      If None, assumes dt_str is already in UTC or has timezone info
    
    Returns:
        UTC datetime string in format "YYYY-MM-DDTHH:MM:SS.000Z"
    """
    if dt_str is None:
        # Use current UTC time
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    # Parse the datetime string
    dt = parser.parse(dt_str)
    
    # If user timezone is specified and datetime is naive (no timezone info)
    if user_timezone and dt.tzinfo is None:
        # Assume the datetime is in user's timezone
        tz = pytz.timezone(user_timezone)
        dt = tz.localize(dt)
    
    # Convert to UTC if it has timezone info
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    else:
        # If still no timezone info, assume it's already UTC
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Return in Toggl's expected format
    return dt.isoformat().replace('+00:00', 'Z')


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
    workspace_id: Optional[Union[int, str]] = None,
    client_id: Optional[Union[int, str]] = None,
    color: Optional[str] = None,
    is_private: Optional[Union[bool, str, int]] = None
) -> Dict[str, Any]:
    """Create a new project in a workspace
    
    Args:
        name: Project name
        workspace_id: Workspace ID (uses default if not provided)
        client_id: Client ID (optional)
        color: Project color in hex format (optional)
        is_private: Whether the project is private (accepts bool, string, or number)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    # Convert string to int if needed
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    if client_id is not None and isinstance(client_id, str):
        client_id = int(client_id)
    
    # Convert to bool if needed
    is_private = to_bool(is_private)
    
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
    # Use UTC time for default dates
    end = end_date or datetime.now(timezone.utc).isoformat()
    start = start_date or (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
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
    workspace_id: Optional[Union[int, str]] = None,
    project_id: Optional[Union[int, str]] = None,
    task_id: Optional[Union[int, str]] = None,
    tags: Optional[List[str]] = None,
    tag_ids: Optional[List[int]] = None,
    billable: Optional[Union[bool, str, int]] = None,
    created_with: Optional[str] = "toggl-mcp",
    user_timezone: Optional[str] = None
) -> Dict[str, Any]:
    """Start a new time entry (timer)
    
    Args:
        description: Time entry description
        workspace_id: Workspace ID (uses default if not provided)
        project_id: Project ID (optional)
        task_id: Task ID for the project (optional)
        tags: List of tag names (optional)
        tag_ids: List of tag IDs (optional)
        billable: Whether the time entry is billable (accepts bool, string, or number)
        created_with: Source of the time entry (default: "toggl-mcp")
        user_timezone: User's timezone (e.g., 'America/New_York'). If not provided, uses UTC.
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    # Convert string to int if needed
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    if project_id is not None and isinstance(project_id, str):
        project_id = int(project_id)
    if task_id is not None and isinstance(task_id, str):
        task_id = int(task_id)
    
    # Convert to bool if needed
    if billable is not None:
        original_billable = billable
        billable = to_bool(billable)
        logger.debug(f"toggl_start_timer: Converted billable from {original_billable!r} ({type(original_billable).__name__}) to {billable!r} ({type(billable).__name__})")
    
    wid = get_workspace_id(workspace_id)
    kwargs = {
        "start": to_utc_string(None, user_timezone),  # Use current time in user's timezone or UTC
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
    time_entry_id: Union[int, str],
    workspace_id: Optional[Union[int, str]] = None
) -> Dict[str, Any]:
    """Stop a running time entry
    
    Args:
        time_entry_id: Time entry ID to stop
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    # Convert string to int if needed
    if time_entry_id is not None and isinstance(time_entry_id, str):
        time_entry_id = int(time_entry_id)
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    
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
    billable: Optional[Union[bool, str, int]] = None,
    duronly: Optional[Union[bool, str, int]] = None,
    created_with: Optional[str] = "toggl-mcp",
    user_timezone: Optional[str] = None
) -> Dict[str, Any]:
    """Create a completed time entry with specific start and stop times
    
    Args:
        description: Time entry description
        start: Start time (ISO 8601 format or any parseable datetime string)
        stop: Stop time (ISO 8601 format or any parseable datetime string)
        workspace_id: Workspace ID (uses default if not provided)
        project_id: Project ID (optional)
        task_id: Task ID for the project (optional)
        tags: List of tag names (optional)
        tag_ids: List of tag IDs (optional)
        billable: Whether the time entry is billable (accepts bool, string, or number)
        duronly: Whether to save only duration, no start/stop times (accepts bool, string, or number)
        created_with: Source of the time entry (default: "toggl-mcp")
        user_timezone: User's timezone (e.g., 'America/New_York'). If not provided, assumes times are in UTC.
                      This is used to interpret start/stop times if they don't have timezone info.
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
    
    # Convert to bool if needed
    if billable is not None:
        original_billable = billable
        billable = to_bool(billable)
        logger.debug(f"toggl_create_time_entry: Converted billable from {original_billable!r} ({type(original_billable).__name__}) to {billable!r} ({type(billable).__name__})")
    duronly = to_bool(duronly)
    
    try:
        wid = get_workspace_id(workspace_id)
        logger.debug(f"Using workspace ID: {wid}")
    except ValueError as e:
        logger.error(f"Workspace ID error: {e}")
        return {"error": str(e)}
    
    # Convert times to UTC format required by Toggl
    start_utc = to_utc_string(start, user_timezone)
    stop_utc = to_utc_string(stop, user_timezone)
    
    kwargs = {"start": start_utc, "stop": stop_utc}
    
    # Calculate duration
    start_dt = parser.parse(start_utc)
    stop_dt = parser.parse(stop_utc)
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


@mcp.tool()
async def toggl_update_time_entry(
    time_entry_id: Union[int, str],
    workspace_id: Optional[Union[int, str]] = None,
    description: Optional[str] = None,
    project_id: Optional[Union[int, str]] = None,
    task_id: Optional[Union[int, str]] = None,
    tags: Optional[List[str]] = None,
    tag_ids: Optional[List[int]] = None,
    billable: Optional[Union[bool, str, int]] = None,
    start: Optional[str] = None,
    stop: Optional[str] = None,
    duration: Optional[int] = None,
    duronly: Optional[Union[bool, str, int]] = None,
    user_timezone: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing time entry
    
    Args:
        time_entry_id: Time entry ID to update
        workspace_id: Workspace ID (uses default if not provided)
        description: Time entry description (optional)
        project_id: Project ID (optional)
        task_id: Task ID for the project (optional)
        tags: List of tag names (optional)
        tag_ids: List of tag IDs (optional)
        billable: Whether the time entry is billable (accepts bool, string, or number)
        start: Start time (ISO 8601 format or any parseable datetime string, optional)
        stop: Stop time (ISO 8601 format or any parseable datetime string, optional)
        duration: Duration in seconds (optional)
        duronly: Whether to save only duration, no start/stop times (accepts bool, string, or number)
        user_timezone: User's timezone (e.g., 'America/New_York'). If not provided, assumes times are in UTC.
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    # Convert string to int if needed
    if time_entry_id is not None and isinstance(time_entry_id, str):
        time_entry_id = int(time_entry_id)
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    if project_id is not None and isinstance(project_id, str):
        project_id = int(project_id)
    if task_id is not None and isinstance(task_id, str):
        task_id = int(task_id)
    
    # Convert to bool if needed
    if billable is not None:
        original_billable = billable
        billable = to_bool(billable)
        logger.debug(f"toggl_update_time_entry: Converted billable from {original_billable!r} ({type(original_billable).__name__}) to {billable!r} ({type(billable).__name__})")
    duronly = to_bool(duronly)
    
    wid = get_workspace_id(workspace_id)
    
    # Build update data
    kwargs = {}
    if description is not None:
        kwargs["description"] = description
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
    if start is not None:
        kwargs["start"] = to_utc_string(start, user_timezone)
    if stop is not None:
        kwargs["stop"] = to_utc_string(stop, user_timezone)
    if duration is not None:
        kwargs["duration"] = duration
    if duronly is not None:
        kwargs["duronly"] = duronly
    
    if not kwargs:
        return {"error": "No fields to update provided"}
    
    logger.info(f"Updating time entry {time_entry_id} with: {kwargs}")
    
    try:
        result = await toggl_client.update_time_entry(wid, time_entry_id, **kwargs)
        logger.info(f"Successfully updated time entry {time_entry_id}")
        return result
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response else str(e)
        logger.error(f"HTTP {e.response.status_code} error updating time entry: {error_detail}")
        return {"error": f"HTTP {e.response.status_code}: {error_detail}"}
    except Exception as e:
        logger.error(f"Failed to update time entry: {e}")
        return {"error": f"Failed to update time entry: {str(e)}"}


@mcp.tool()
async def toggl_delete_time_entry(
    time_entry_id: Union[int, str],
    workspace_id: Optional[Union[int, str]] = None
) -> Dict[str, Any]:
    """Delete a time entry
    
    Args:
        time_entry_id: Time entry ID to delete
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    # Convert string to int if needed
    if time_entry_id is not None and isinstance(time_entry_id, str):
        time_entry_id = int(time_entry_id)
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    
    wid = get_workspace_id(workspace_id)
    
    logger.info(f"Deleting time entry {time_entry_id}")
    
    try:
        result = await toggl_client.delete_time_entry(wid, time_entry_id)
        logger.info(f"Successfully deleted time entry {time_entry_id}")
        return {"success": True, "message": f"Time entry {time_entry_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete time entry: {e}")
        return {"error": f"Failed to delete time entry: {str(e)}"}


@mcp.tool()
async def toggl_bulk_update_time_entries(
    time_entry_ids: List[Union[int, str]],
    workspace_id: Optional[Union[int, str]] = None,
    description: Optional[str] = None,
    project_id: Optional[Union[int, str]] = None,
    task_id: Optional[Union[int, str]] = None,
    tags: Optional[List[str]] = None,
    tag_ids: Optional[List[int]] = None,
    billable: Optional[Union[bool, str, int]] = None,
    tag_action: Optional[str] = None
) -> Dict[str, Any]:
    """Update multiple time entries at once
    
    Args:
        time_entry_ids: List of time entry IDs to update
        workspace_id: Workspace ID (uses default if not provided)
        description: Time entry description (optional)
        project_id: Project ID (optional)
        task_id: Task ID for the project (optional)
        tags: List of tag names (optional)
        tag_ids: List of tag IDs (optional)
        billable: Whether the time entries are billable (optional)
        tag_action: How to handle tags - "add" or "replace" (optional)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    if not time_entry_ids:
        return {"error": "No time entry IDs provided"}
    
    # Convert string to int if needed
    converted_ids = []
    for entry_id in time_entry_ids:
        if isinstance(entry_id, str):
            converted_ids.append(int(entry_id))
        else:
            converted_ids.append(entry_id)
    
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    if project_id is not None and isinstance(project_id, str):
        project_id = int(project_id)
    if task_id is not None and isinstance(task_id, str):
        task_id = int(task_id)
    
    # Convert to bool if needed
    if billable is not None:
        original_billable = billable
        billable = to_bool(billable)
        logger.debug(f"toggl_bulk_update_time_entries: Converted billable from {original_billable!r} ({type(original_billable).__name__}) to {billable!r} ({type(billable).__name__})")
    
    wid = get_workspace_id(workspace_id)
    
    # Build update data
    updates = {}
    if description is not None:
        updates["description"] = description
    if project_id is not None:
        updates["project_id"] = project_id
    if task_id is not None:
        updates["task_id"] = task_id
    if tags is not None:
        updates["tags"] = tags
    if tag_ids is not None:
        updates["tag_ids"] = tag_ids
    if billable is not None:
        updates["billable"] = billable
    if tag_action is not None:
        updates["tag_action"] = tag_action
    
    if not updates:
        return {"error": "No fields to update provided"}
    
    logger.info(f"Bulk updating {len(converted_ids)} time entries with: {updates}")
    
    try:
        result = await toggl_client.bulk_update_time_entries(wid, converted_ids, updates)
        logger.info(f"Successfully bulk updated {len(converted_ids)} time entries")
        return result
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text if e.response else str(e)
        logger.error(f"HTTP {e.response.status_code} error bulk updating time entries: {error_detail}")
        return {"error": f"HTTP {e.response.status_code}: {error_detail}"}
    except Exception as e:
        logger.error(f"Failed to bulk update time entries: {e}")
        return {"error": f"Failed to bulk update time entries: {str(e)}"}


@mcp.tool()
async def toggl_bulk_delete_time_entries(
    time_entry_ids: List[Union[int, str]],
    workspace_id: Optional[Union[int, str]] = None
) -> Dict[str, Any]:
    """Delete multiple time entries at once
    
    Args:
        time_entry_ids: List of time entry IDs to delete
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    if not time_entry_ids:
        return {"error": "No time entry IDs provided"}
    
    # Convert string to int if needed
    converted_ids = []
    for entry_id in time_entry_ids:
        if isinstance(entry_id, str):
            converted_ids.append(int(entry_id))
        else:
            converted_ids.append(entry_id)
    
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    
    wid = get_workspace_id(workspace_id)
    
    logger.info(f"Bulk deleting {len(converted_ids)} time entries")
    
    try:
        result = await toggl_client.bulk_delete_time_entries(wid, converted_ids)
        logger.info(f"Successfully bulk deleted {len(converted_ids)} time entries")
        return {"success": True, "message": f"Successfully deleted {len(converted_ids)} time entries", "details": result}
    except Exception as e:
        logger.error(f"Failed to bulk delete time entries: {e}")
        return {"error": f"Failed to bulk delete time entries: {str(e)}"}


# Tag Tools
@mcp.tool()
async def toggl_list_tags(workspace_id: Optional[Union[int, str]] = None) -> List[Dict[str, Any]]:
    """List all tags in a workspace
    
    Args:
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    # Convert string to int if needed
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    
    wid = get_workspace_id(workspace_id)
    return await toggl_client.get_tags(wid)


@mcp.tool()
async def toggl_create_tag(
    name: str,
    workspace_id: Optional[Union[int, str]] = None
) -> Dict[str, Any]:
    """Create a new tag in a workspace
    
    Args:
        name: Tag name
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    # Convert string to int if needed
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    
    wid = get_workspace_id(workspace_id)
    return await toggl_client.create_tag(wid, name)


# Client Tools
@mcp.tool()
async def toggl_list_clients(workspace_id: Optional[Union[int, str]] = None) -> List[Dict[str, Any]]:
    """List all clients in a workspace
    
    Args:
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    # Convert string to int if needed
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    
    wid = get_workspace_id(workspace_id)
    return await toggl_client.get_clients(wid)


@mcp.tool()
async def toggl_create_client(
    name: str,
    workspace_id: Optional[Union[int, str]] = None
) -> Dict[str, Any]:
    """Create a new client in a workspace
    
    Args:
        name: Client name
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    # Convert string to int if needed
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    
    wid = get_workspace_id(workspace_id)
    return await toggl_client.create_client(wid, name)


# Project Task Tools
@mcp.tool()
async def toggl_list_project_tasks(
    project_id: Union[int, str],
    workspace_id: Optional[Union[int, str]] = None
) -> List[Dict[str, Any]]:
    """List tasks for a project (only if tasks are enabled)
    
    Args:
        project_id: Project ID
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    # Convert string to int if needed
    if project_id is not None and isinstance(project_id, str):
        project_id = int(project_id)
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    
    wid = get_workspace_id(workspace_id)
    return await toggl_client.get_project_tasks(wid, project_id)


@mcp.tool()
async def toggl_create_project_task(
    project_id: Union[int, str],
    name: str,
    workspace_id: Optional[Union[int, str]] = None
) -> Dict[str, Any]:
    """Create a task for a project
    
    Args:
        project_id: Project ID
        name: Task name
        workspace_id: Workspace ID (uses default if not provided)
    """
    if not toggl_client:
        return {"error": "Toggl client not initialized. Please set TOGGL_API_TOKEN environment variable."}
    
    # Convert string to int if needed
    if project_id is not None and isinstance(project_id, str):
        project_id = int(project_id)
    if workspace_id is not None and isinstance(workspace_id, str):
        workspace_id = int(workspace_id)
    
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