"""Pytest configuration and shared fixtures for toggl-mcp tests"""

import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

# Add the parent directory to the path to import toggl_mcp
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from toggl_mcp.toggl_client import TogglClient


@pytest.fixture
def mock_toggl_client():
    """Create a mock TogglClient for testing"""
    client = AsyncMock(spec=TogglClient)
    
    # Mock common responses
    client.get_me.return_value = {
        "id": 123456,
        "fullname": "Test User",
        "email": "test@example.com"
    }
    
    client.get_workspaces.return_value = [
        {"id": 1234567, "name": "Test Workspace"}
    ]
    
    client.get_organizations.return_value = []
    
    client.get_projects.return_value = [
        {"id": 1, "name": "Test Project", "workspace_id": 1234567}
    ]
    
    client.create_project.return_value = {
        "id": 2,
        "name": "New Project",
        "workspace_id": 1234567
    }
    
    client.get_time_entries.return_value = []
    
    client.get_current_time_entry.return_value = None
    
    client.create_time_entry.return_value = {
        "id": 100,
        "description": "Test Entry",
        "workspace_id": 1234567,
        "duration": -1
    }
    
    client.stop_time_entry.return_value = {
        "id": 100,
        "description": "Test Entry",
        "workspace_id": 1234567,
        "duration": 120
    }
    
    client.get_tags.return_value = []
    
    client.create_tag.return_value = {
        "id": 10,
        "name": "test-tag",
        "workspace_id": 1234567
    }
    
    client.get_clients.return_value = []
    
    client.create_client.return_value = {
        "id": 20,
        "name": "Test Client",
        "workspace_id": 1234567
    }
    
    client.get_project_tasks.return_value = []
    
    client.create_project_task.return_value = {
        "id": 30,
        "name": "Test Task",
        "project_id": 1,
        "workspace_id": 1234567
    }
    
    client.close = AsyncMock()
    
    return client


@pytest.fixture
def default_workspace_id():
    """Default workspace ID for testing"""
    return 1234567


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("TOGGL_API_TOKEN", "test_token_123456")
    monkeypatch.setenv("TOGGL_WORKSPACE_ID", "1234567")
    return {
        "TOGGL_API_TOKEN": "test_token_123456",
        "TOGGL_WORKSPACE_ID": "1234567"
    }
