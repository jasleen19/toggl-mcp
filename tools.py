"""
Tool definitions and handlers for Toggl MCP Server
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from mcp.types import Tool
from dateutil import parser


def get_workspace_id(args: Dict, default_workspace_id: Optional[int]) -> int:
    """Helper to get workspace ID from arguments or default"""
    if "workspace_id" in args and args["workspace_id"]:
        return args["workspace_id"]
    if default_workspace_id:
        return default_workspace_id
    raise ValueError("No workspace_id provided and no default workspace set")


def get_all_tools() -> List[Tool]:
    """Get all available Toggl tools"""
    return [
        # User & Workspace Tools
        Tool(
            name="toggl_get_user",
            description="Get current Toggl user information",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="toggl_list_workspaces",
            description="List all available Toggl workspaces",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="toggl_list_organizations",
            description="List user's organizations",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        # Project Tools
        Tool(
            name="toggl_list_projects",
            description="List all projects in a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {
                        "type": "integer",
                        "description": "Workspace ID (uses default if not provided)",
                    }
                },
            }
        ),
        Tool(
            name="toggl_create_project",
            description="Create a new project in a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Project name"},
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"},
                    "client_id": {"type": "integer", "description": "Client ID (optional)"},
                    "color": {"type": "string", "description": "Project color in hex format (optional)"},
                    "is_private": {"type": "boolean", "description": "Whether the project is private (optional)"},
                },
                "required": ["name"],
            }
        ),
        
        # Time Entry Tools
        Tool(
            name="toggl_list_time_entries",
            description="List time entries within a date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date (ISO 8601 format, defaults to 7 days ago)"},
                    "end_date": {"type": "string", "description": "End date (ISO 8601 format, defaults to today)"},
                },
            }
        ),
        Tool(
            name="toggl_get_current_timer",
            description="Get the currently running time entry",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="toggl_start_timer",
            description="Start a new time entry (timer)",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Time entry description"},
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"},
                    "project_id": {"type": "integer", "description": "Project ID (optional)"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "List of tag names (optional)"},
                    "billable": {"type": "boolean", "description": "Whether the time entry is billable (optional)"},
                },
                "required": ["description"],
            }
        ),
        Tool(
            name="toggl_stop_timer",
            description="Stop a running time entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_entry_id": {"type": "integer", "description": "Time entry ID to stop"},
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"},
                },
                "required": ["time_entry_id"],
            }
        ),
        Tool(
            name="toggl_create_time_entry",
            description="Create a completed time entry with specific start and stop times",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Time entry description"},
                    "start": {"type": "string", "description": "Start time (ISO 8601 format)"},
                    "stop": {"type": "string", "description": "Stop time (ISO 8601 format)"},
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"},
                    "project_id": {"type": "integer", "description": "Project ID (optional)"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "List of tag names (optional)"},
                    "billable": {"type": "boolean", "description": "Whether the time entry is billable (optional)"},
                },
                "required": ["description", "start", "stop"],
            }
        ),
        
        # Tag Tools
        Tool(
            name="toggl_list_tags",
            description="List all tags in a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"}
                },
            }
        ),
        Tool(
            name="toggl_create_tag",
            description="Create a new tag in a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Tag name"},
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"},
                },
                "required": ["name"],
            }
        ),
        
        # Client Tools
        Tool(
            name="toggl_list_clients",
            description="List all clients in a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"}
                },
            }
        ),
        Tool(
            name="toggl_create_client",
            description="Create a new client in a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Client name"},
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"},
                },
                "required": ["name"],
            }
        ),
        
        # Bulk Time Entry Tools
        Tool(
            name="toggl_bulk_create_time_entries",
            description="Create multiple time entries at once",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_entries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "start": {"type": "string", "description": "ISO 8601 format"},
                                "stop": {"type": "string", "description": "ISO 8601 format"},
                                "duration": {"type": "integer", "description": "Duration in seconds"},
                                "project_id": {"type": "integer"},
                                "tags": {"type": "array", "items": {"type": "string"}},
                                "billable": {"type": "boolean"},
                            },
                            "required": ["description", "start"]
                        },
                        "description": "Array of time entry objects to create"
                    },
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"},
                },
                "required": ["time_entries"],
            }
        ),
        Tool(
            name="toggl_bulk_update_time_entries",
            description="Update multiple time entries at once",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_entry_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of time entry IDs to update"
                    },
                    "updates": {
                        "type": "object",
                        "description": "Fields to update (e.g., description, project_id, tags)",
                    },
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"},
                },
                "required": ["time_entry_ids", "updates"],
            }
        ),
        Tool(
            name="toggl_bulk_delete_time_entries",
            description="Delete multiple time entries at once",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_entry_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of time entry IDs to delete"
                    },
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"},
                },
                "required": ["time_entry_ids"],
            }
        ),
        
        # Project Task Tools
        Tool(
            name="toggl_list_project_tasks",
            description="List tasks for a project (only if tasks are enabled)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "Project ID"},
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"},
                },
                "required": ["project_id"],
            }
        ),
        Tool(
            name="toggl_create_project_task",
            description="Create a task for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "Project ID"},
                    "name": {"type": "string", "description": "Task name"},
                    "workspace_id": {"type": "integer", "description": "Workspace ID (uses default if not provided)"},
                },
                "required": ["project_id", "name"],
            }
        ),
    ]


async def handle_tool_call(
    client: Any, 
    default_workspace_id: Optional[int], 
    name: str, 
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """Handle individual tool calls"""
    
    # User & Workspace tools
    if name == "toggl_get_user":
        return await client.get_me()
    
    elif name == "toggl_list_workspaces":
        return await client.get_workspaces()
    
    elif name == "toggl_list_organizations":
        return await client.get_organizations()
    
    # Project tools
    elif name == "toggl_list_projects":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        return await client.get_projects(workspace_id)
    
    elif name == "toggl_create_project":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        name_val = arguments["name"]
        kwargs = {k: v for k, v in arguments.items() 
                 if k not in ["name", "workspace_id"] and v is not None}
        return await client.create_project(workspace_id, name_val, **kwargs)
    
    # Time entry tools
    elif name == "toggl_list_time_entries":
        end_date = arguments.get("end_date") or datetime.now().isoformat()
        start_date = arguments.get("start_date") or (
            datetime.now() - timedelta(days=7)
        ).isoformat()
        return await client.get_time_entries(start_date, end_date)
    
    elif name == "toggl_get_current_timer":
        result = await client.get_current_time_entry()
        return result if result else {"message": "No timer currently running"}
    
    elif name == "toggl_start_timer":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        description = arguments["description"]
        kwargs = {k: v for k, v in arguments.items() 
                 if k not in ["description", "workspace_id"] and v is not None}
        kwargs["start"] = datetime.now().isoformat() + "Z"
        kwargs["duration"] = -1  # Negative duration indicates running
        return await client.create_time_entry(workspace_id, description, **kwargs)
    
    elif name == "toggl_stop_timer":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        time_entry_id = arguments["time_entry_id"]
        return await client.stop_time_entry(workspace_id, time_entry_id)
    
    elif name == "toggl_create_time_entry":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        description = arguments["description"]
        kwargs = {k: v for k, v in arguments.items() 
                 if k not in ["description", "workspace_id"] and v is not None}
        # Calculate duration from start and stop
        if "start" in kwargs and "stop" in kwargs:
            start_dt = parser.parse(kwargs["start"])
            stop_dt = parser.parse(kwargs["stop"])
            duration = int((stop_dt - start_dt).total_seconds())
            kwargs["duration"] = duration
        return await client.create_time_entry(workspace_id, description, **kwargs)
    
    # Tag tools
    elif name == "toggl_list_tags":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        return await client.get_tags(workspace_id)
    
    elif name == "toggl_create_tag":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        name_val = arguments["name"]
        return await client.create_tag(workspace_id, name_val)
    
    # Client tools
    elif name == "toggl_list_clients":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        return await client.get_clients(workspace_id)
    
    elif name == "toggl_create_client":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        name_val = arguments["name"]
        return await client.create_client(workspace_id, name_val)
    
    # Bulk time entry tools
    elif name == "toggl_bulk_create_time_entries":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        time_entries = arguments["time_entries"]
        # Process each entry to calculate duration if needed
        for entry in time_entries:
            if "start" in entry and "stop" in entry and "duration" not in entry:
                start_dt = parser.parse(entry["start"])
                stop_dt = parser.parse(entry["stop"])
                entry["duration"] = int((stop_dt - start_dt).total_seconds())
            entry["created_with"] = "toggl-mcp"
            entry["workspace_id"] = workspace_id
        return await client.bulk_create_time_entries(workspace_id, time_entries)
    
    elif name == "toggl_bulk_update_time_entries":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        time_entry_ids = arguments["time_entry_ids"]
        updates = arguments["updates"]
        return await client.bulk_update_time_entries(workspace_id, time_entry_ids, updates)
    
    elif name == "toggl_bulk_delete_time_entries":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        time_entry_ids = arguments["time_entry_ids"]
        return await client.bulk_delete_time_entries(workspace_id, time_entry_ids)
    
    # Project task tools
    elif name == "toggl_list_project_tasks":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        project_id = arguments["project_id"]
        return await client.get_project_tasks(workspace_id, project_id)
    
    elif name == "toggl_create_project_task":
        workspace_id = get_workspace_id(arguments, default_workspace_id)
        project_id = arguments["project_id"]
        name_val = arguments["name"]
        return await client.create_project_task(workspace_id, project_id, name_val)
    
    else:
        raise ValueError(f"Unknown tool '{name}'")
