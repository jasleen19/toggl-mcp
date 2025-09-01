"""
Toggl API Parameter Documentation

This module documents all available parameters for Toggl API endpoints.
Based on Toggl Track API v9 documentation.
"""

from typing import Dict, List, Any, TypedDict, Optional

class TimeEntryParams(TypedDict, total=False):
    """All available parameters for time entry creation/update"""
    # Required fields
    description: str  # Required: Time entry description
    workspace_id: int  # Required: Workspace ID
    
    # Time-related fields
    start: str  # ISO 8601 datetime (required for new entries)
    stop: Optional[str]  # ISO 8601 datetime (omit for running timer)
    duration: Optional[int]  # Duration in seconds (negative for running)
    duronly: Optional[bool]  # If true, only duration is saved, not start/stop times
    start_date: Optional[str]  # Date in YYYY-MM-DD format
    
    # Project and task fields
    project_id: Optional[int]  # Project ID
    pid: Optional[int]  # Alternative to project_id
    task_id: Optional[int]  # Task ID (requires project with tasks enabled)
    tid: Optional[int]  # Alternative to task_id
    
    # Tag fields
    tags: Optional[List[str]]  # Tag names
    tag_ids: Optional[List[int]]  # Tag IDs
    tag_action: Optional[str]  # "add" or "replace" for bulk operations
    
    # User and sharing
    user_id: Optional[int]  # User ID (for admins creating entries for others)
    uid: Optional[int]  # Alternative to user_id
    shared_with_user_ids: Optional[List[int]]  # Share time entry with users
    
    # Billing and expenses
    billable: Optional[bool]  # Whether time entry is billable
    expense_ids: Optional[List[int]]  # Associated expense IDs
    
    # Metadata
    created_with: Optional[str]  # Client name (e.g., "toggl-mcp", "web", "mobile")
    event_metadata: Optional[Dict[str, Any]]  # Additional metadata
    at: Optional[str]  # Last update time (ISO 8601)
    

class ProjectParams(TypedDict, total=False):
    """All available parameters for project creation/update"""
    # Required fields
    name: str  # Required: Project name
    workspace_id: int  # Required: Workspace ID
    
    # Optional fields
    client_id: Optional[int]  # Client ID
    cid: Optional[int]  # Alternative to client_id
    color: Optional[str]  # Hex color code (e.g., "#06aaf5")
    hex_color: Optional[str]  # Alternative to color
    is_private: Optional[bool]  # Whether project is private
    active: Optional[bool]  # Whether project is active
    billable: Optional[bool]  # Default billable setting for time entries
    auto_estimates: Optional[bool]  # Whether auto estimates are enabled
    estimated_hours: Optional[float]  # Estimated hours for project
    template: Optional[bool]  # Whether project is a template
    template_id: Optional[int]  # Template to create project from
    currency: Optional[str]  # Project currency (e.g., "USD")
    recurring: Optional[bool]  # Whether project is recurring
    recurring_parameters: Optional[Dict[str, Any]]  # Recurring project settings
    fixed_fee: Optional[float]  # Fixed fee amount
    rate: Optional[float]  # Hourly rate


class TagParams(TypedDict, total=False):
    """All available parameters for tag creation/update"""
    # Required fields
    name: str  # Required: Tag name
    workspace_id: int  # Required: Workspace ID


class ClientParams(TypedDict, total=False):
    """All available parameters for client creation/update"""
    # Required fields
    name: str  # Required: Client name
    workspace_id: int  # Required: Workspace ID
    
    # Optional fields
    notes: Optional[str]  # Client notes
    

class TaskParams(TypedDict, total=False):
    """All available parameters for task creation/update"""
    # Required fields
    name: str  # Required: Task name
    project_id: int  # Required: Project ID
    workspace_id: int  # Required: Workspace ID
    
    # Optional fields
    active: Optional[bool]  # Whether task is active
    estimated_seconds: Optional[int]  # Estimated time in seconds
    user_id: Optional[int]  # Assigned user ID


# API endpoint documentation
API_ENDPOINTS = {
    "time_entries": {
        "create": {
            "required": ["description", "workspace_id", "start"],
            "optional": ["stop", "duration", "project_id", "task_id", "tags", "tag_ids", 
                        "billable", "created_with", "duronly", "user_id", "shared_with_user_ids"]
        },
        "update": {
            "required": ["workspace_id", "time_entry_id"],
            "optional": ["description", "start", "stop", "duration", "project_id", "task_id", 
                        "tags", "tag_ids", "billable", "duronly"]
        },
        "start_timer": {
            "required": ["description", "workspace_id"],
            "optional": ["project_id", "task_id", "tags", "tag_ids", "billable", "created_with"]
        },
        "stop_timer": {
            "required": ["workspace_id", "time_entry_id"],
            "optional": []
        }
    },
    "projects": {
        "create": {
            "required": ["name", "workspace_id"],
            "optional": ["client_id", "color", "is_private", "active", "billable", 
                        "auto_estimates", "estimated_hours", "currency", "rate"]
        },
        "update": {
            "required": ["workspace_id", "project_id"],
            "optional": ["name", "client_id", "color", "is_private", "active", "billable",
                        "auto_estimates", "estimated_hours", "currency", "rate"]
        }
    },
    "tags": {
        "create": {
            "required": ["name", "workspace_id"],
            "optional": []
        },
        "update": {
            "required": ["name", "workspace_id", "tag_id"],
            "optional": []
        }
    },
    "clients": {
        "create": {
            "required": ["name", "workspace_id"],
            "optional": ["notes"]
        },
        "update": {
            "required": ["workspace_id", "client_id"],
            "optional": ["name", "notes"]
        }
    },
    "tasks": {
        "create": {
            "required": ["name", "project_id", "workspace_id"],
            "optional": ["active", "estimated_seconds", "user_id"]
        },
        "update": {
            "required": ["workspace_id", "project_id", "task_id"],
            "optional": ["name", "active", "estimated_seconds", "user_id"]
        }
    }
}
