"""Unit tests for toggl-mcp tool functions"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Import the main module and functions
from toggl_mcp import main
from toggl_mcp.main import (
    get_workspace_id,
    toggl_get_user,
    toggl_list_workspaces,
    toggl_list_organizations,
    toggl_list_projects,
    toggl_create_project,
    toggl_list_time_entries,
    toggl_get_current_timer,
    toggl_start_timer,
    toggl_stop_timer,
    toggl_create_time_entry,
    toggl_list_tags,
    toggl_create_tag,
    toggl_list_clients,
    toggl_create_client,
    toggl_list_project_tasks,
    toggl_create_project_task
)


class TestWorkspaceHelper:
    """Test the get_workspace_id helper function"""
    
    def test_get_workspace_id_with_provided_id(self):
        """Test that provided workspace ID is used"""
        result = get_workspace_id(123)
        assert result == 123
    
    def test_get_workspace_id_with_default(self):
        """Test that default workspace ID is used when not provided"""
        main.default_workspace_id = 456
        result = get_workspace_id(None)
        assert result == 456
        main.default_workspace_id = None
    
    def test_get_workspace_id_raises_error(self):
        """Test that error is raised when no workspace ID available"""
        main.default_workspace_id = None
        with pytest.raises(ValueError, match="No workspace_id provided"):
            get_workspace_id(None)


@pytest.mark.asyncio
class TestUserAndWorkspaceTools:
    """Test user and workspace-related tools"""
    
    async def test_toggl_get_user_success(self, mock_toggl_client):
        """Test successful user info retrieval"""
        main.toggl_client = mock_toggl_client
        result = await toggl_get_user()
        assert result["fullname"] == "Test User"
        assert result["email"] == "test@example.com"
        mock_toggl_client.get_me.assert_called_once()
    
    async def test_toggl_get_user_no_client(self):
        """Test error when client not initialized"""
        main.toggl_client = None
        result = await toggl_get_user()
        assert "error" in result
        assert "not initialized" in result["error"]
    
    async def test_toggl_list_workspaces_success(self, mock_toggl_client):
        """Test successful workspace listing"""
        main.toggl_client = mock_toggl_client
        result = await toggl_list_workspaces()
        assert len(result) == 1
        assert result[0]["name"] == "Test Workspace"
        mock_toggl_client.get_workspaces.assert_called_once()
    
    async def test_toggl_list_organizations_success(self, mock_toggl_client):
        """Test successful organization listing"""
        main.toggl_client = mock_toggl_client
        result = await toggl_list_organizations()
        assert result == []
        mock_toggl_client.get_organizations.assert_called_once()


@pytest.mark.asyncio
class TestProjectTools:
    """Test project-related tools"""
    
    async def test_toggl_list_projects_success(self, mock_toggl_client, default_workspace_id):
        """Test successful project listing"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        result = await toggl_list_projects()
        assert len(result) == 1
        assert result[0]["name"] == "Test Project"
        mock_toggl_client.get_projects.assert_called_once_with(default_workspace_id)
    
    async def test_toggl_list_projects_with_workspace_id(self, mock_toggl_client):
        """Test project listing with specific workspace ID"""
        main.toggl_client = mock_toggl_client
        result = await toggl_list_projects(workspace_id=999)
        mock_toggl_client.get_projects.assert_called_once_with(999)
    
    async def test_toggl_list_projects_string_workspace_id(self, mock_toggl_client):
        """Test project listing with string workspace ID"""
        main.toggl_client = mock_toggl_client
        result = await toggl_list_projects(workspace_id="999")
        mock_toggl_client.get_projects.assert_called_once_with(999)
    
    async def test_toggl_create_project_success(self, mock_toggl_client, default_workspace_id):
        """Test successful project creation"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        result = await toggl_create_project(
            name="New Project",
            color="#ff0000",
            is_private=True
        )
        assert result["name"] == "New Project"
        mock_toggl_client.create_project.assert_called_once_with(
            default_workspace_id,
            "New Project",
            color="#ff0000",
            is_private=True
        )
    
    async def test_toggl_create_project_minimal(self, mock_toggl_client, default_workspace_id):
        """Test project creation with minimal parameters"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        result = await toggl_create_project(name="Minimal Project")
        mock_toggl_client.create_project.assert_called_once_with(
            default_workspace_id,
            "Minimal Project"
        )


@pytest.mark.asyncio
class TestTimeEntryTools:
    """Test time entry-related tools"""
    
    async def test_toggl_list_time_entries_default_dates(self, mock_toggl_client):
        """Test time entry listing with default date range"""
        main.toggl_client = mock_toggl_client
        result = await toggl_list_time_entries()
        assert result == []
        mock_toggl_client.get_time_entries.assert_called_once()
        # Check that dates are provided
        call_args = mock_toggl_client.get_time_entries.call_args[0]
        assert len(call_args) == 2  # start and end dates
    
    async def test_toggl_list_time_entries_custom_dates(self, mock_toggl_client):
        """Test time entry listing with custom date range"""
        main.toggl_client = mock_toggl_client
        start = "2024-01-01T00:00:00Z"
        end = "2024-01-31T23:59:59Z"
        result = await toggl_list_time_entries(start_date=start, end_date=end)
        mock_toggl_client.get_time_entries.assert_called_once_with(start, end)
    
    async def test_toggl_get_current_timer_running(self, mock_toggl_client):
        """Test getting current timer when one is running"""
        main.toggl_client = mock_toggl_client
        mock_toggl_client.get_current_time_entry.return_value = {
            "id": 123,
            "description": "Running timer"
        }
        result = await toggl_get_current_timer()
        assert result["description"] == "Running timer"
    
    async def test_toggl_get_current_timer_none(self, mock_toggl_client):
        """Test getting current timer when none is running"""
        main.toggl_client = mock_toggl_client
        mock_toggl_client.get_current_time_entry.return_value = None
        result = await toggl_get_current_timer()
        assert "message" in result
        assert "No timer currently running" in result["message"]
    
    async def test_toggl_start_timer_success(self, mock_toggl_client, default_workspace_id):
        """Test starting a timer"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        result = await toggl_start_timer(
            description="Test Timer",
            project_id=1,
            tags=["test", "timer"],
            billable=True
        )
        assert result["description"] == "Test Entry"
        mock_toggl_client.create_time_entry.assert_called_once()
        call_kwargs = mock_toggl_client.create_time_entry.call_args[1]
        assert call_kwargs["duration"] == -1  # Running timer
        assert call_kwargs["project_id"] == 1
        assert call_kwargs["tags"] == ["test", "timer"]
        assert call_kwargs["billable"] == True
    
    async def test_toggl_stop_timer_success(self, mock_toggl_client, default_workspace_id):
        """Test stopping a timer"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        result = await toggl_stop_timer(time_entry_id=100)
        assert result["duration"] == 120
        mock_toggl_client.stop_time_entry.assert_called_once_with(default_workspace_id, 100)
    
    async def test_toggl_create_time_entry_success(self, mock_toggl_client, default_workspace_id):
        """Test creating a completed time entry"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        start = "2024-01-01T10:00:00Z"
        stop = "2024-01-01T11:00:00Z"
        result = await toggl_create_time_entry(
            description="Completed Entry",
            start=start,
            stop=stop,
            project_id=1
        )
        assert result["description"] == "Test Entry"
        mock_toggl_client.create_time_entry.assert_called_once()
        call_kwargs = mock_toggl_client.create_time_entry.call_args[1]
        assert call_kwargs["start"] == start
        assert call_kwargs["stop"] == stop
        assert call_kwargs["duration"] == 3600  # 1 hour in seconds
        assert call_kwargs["project_id"] == 1
    
    async def test_toggl_create_time_entry_string_ids(self, mock_toggl_client, default_workspace_id):
        """Test creating time entry with string IDs"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        start = "2024-01-01T10:00:00Z"
        stop = "2024-01-01T11:00:00Z"
        result = await toggl_create_time_entry(
            description="String ID Entry",
            start=start,
            stop=stop,
            workspace_id="999",
            project_id="123",
            task_id="456"
        )
        mock_toggl_client.create_time_entry.assert_called_once()
        call_args = mock_toggl_client.create_time_entry.call_args
        assert call_args[0][0] == 999  # workspace_id converted to int
        call_kwargs = call_args[1]
        assert call_kwargs["project_id"] == 123
        assert call_kwargs["task_id"] == 456


@pytest.mark.asyncio
class TestTagTools:
    """Test tag-related tools"""
    
    async def test_toggl_list_tags_success(self, mock_toggl_client, default_workspace_id):
        """Test successful tag listing"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        result = await toggl_list_tags()
        assert result == []
        mock_toggl_client.get_tags.assert_called_once_with(default_workspace_id)
    
    async def test_toggl_create_tag_success(self, mock_toggl_client, default_workspace_id):
        """Test successful tag creation"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        result = await toggl_create_tag(name="new-tag")
        assert result["name"] == "test-tag"
        mock_toggl_client.create_tag.assert_called_once_with(default_workspace_id, "new-tag")


@pytest.mark.asyncio
class TestClientTools:
    """Test client-related tools"""
    
    async def test_toggl_list_clients_success(self, mock_toggl_client, default_workspace_id):
        """Test successful client listing"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        result = await toggl_list_clients()
        assert result == []
        mock_toggl_client.get_clients.assert_called_once_with(default_workspace_id)
    
    async def test_toggl_create_client_success(self, mock_toggl_client, default_workspace_id):
        """Test successful client creation"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        result = await toggl_create_client(name="New Client")
        assert result["name"] == "Test Client"
        mock_toggl_client.create_client.assert_called_once_with(default_workspace_id, "New Client")


@pytest.mark.asyncio
class TestProjectTaskTools:
    """Test project task-related tools"""
    
    async def test_toggl_list_project_tasks_success(self, mock_toggl_client, default_workspace_id):
        """Test successful project task listing"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        result = await toggl_list_project_tasks(project_id=1)
        assert result == []
        mock_toggl_client.get_project_tasks.assert_called_once_with(default_workspace_id, 1)
    
    async def test_toggl_create_project_task_success(self, mock_toggl_client, default_workspace_id):
        """Test successful project task creation"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = default_workspace_id
        result = await toggl_create_project_task(project_id=1, name="New Task")
        assert result["name"] == "Test Task"
        mock_toggl_client.create_project_task.assert_called_once_with(default_workspace_id, 1, "New Task")


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling in tools"""
    
    async def test_no_workspace_id_error(self):
        """Test error when no workspace ID is available"""
        main.toggl_client = AsyncMock()
        main.default_workspace_id = None
        
        # This should raise an error since no workspace_id is provided
        with pytest.raises(ValueError):
            await toggl_list_projects()
    
    async def test_client_exception_handling(self, mock_toggl_client):
        """Test handling of client exceptions"""
        main.toggl_client = mock_toggl_client
        main.default_workspace_id = 1234567
        
        # Make the client raise an exception
        mock_toggl_client.create_time_entry.side_effect = Exception("API Error")
        
        result = await toggl_create_time_entry(
            description="Error Test",
            start="2024-01-01T10:00:00Z",
            stop="2024-01-01T11:00:00Z"
        )
        
        assert "error" in result
        assert "Failed to create time entry" in result["error"]
