"""Integration/smoke test for toggl-mcp stdio server"""

import pytest
import asyncio
import json
import os
import sys
from unittest.mock import patch, AsyncMock, MagicMock
from io import StringIO
import tempfile

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent


@pytest.mark.asyncio
class TestStdioServer:
    """Smoke tests for the stdio server"""
    
    async def test_server_initialization(self):
        """Test that the server can be initialized"""
        from toggl_mcp.main import mcp
        
        assert mcp is not None
        assert mcp.name == "toggl-mcp"
    
    async def test_list_tools(self):
        """Test that server can list available tools"""
        from toggl_mcp.main import mcp
        
        # Mock the toggl_client to avoid needing real API token
        with patch('toggl_mcp.main.toggl_client', AsyncMock()):
            tools = await mcp.list_tools()
            
            assert isinstance(tools, list)
            assert len(tools) > 0
            
            # Check that some expected tools are present
            tool_names = [tool.name for tool in tools]
            assert "toggl_get_user" in tool_names
            assert "toggl_list_workspaces" in tool_names
            assert "toggl_list_projects" in tool_names
            assert "toggl_start_timer" in tool_names
            assert "toggl_stop_timer" in tool_names
            assert "toggl_create_time_entry" in tool_names
    
    async def test_tool_schemas(self):
        """Test that tools have proper input schemas"""
        from toggl_mcp.main import mcp
        
        with patch('toggl_mcp.main.toggl_client', AsyncMock()):
            tools = await mcp.list_tools()
            
            for tool in tools:
                assert hasattr(tool, 'name')
                assert hasattr(tool, 'description')
                assert hasattr(tool, 'inputSchema')
                
                # Check that inputSchema is valid
                schema = tool.inputSchema
                assert 'type' in schema
                assert schema['type'] == 'object'
                
                # Tools should have properties defined
                if tool.name != "toggl_get_user" and tool.name != "toggl_list_workspaces" and tool.name != "toggl_list_organizations" and tool.name != "toggl_get_current_timer":
                    # These tools have parameters
                    assert 'properties' in schema
    
    async def test_call_tool_get_user(self):
        """Test calling the get_user tool"""
        from toggl_mcp import main
        
        # Setup mock client
        mock_client = AsyncMock()
        mock_client.get_me.return_value = {
            "id": 123,
            "fullname": "Test User",
            "email": "test@example.com"
        }
        
        with patch.object(main, 'toggl_client', mock_client):
            result = await main.mcp.call_tool("toggl_get_user", {})
            
            # FastMCP returns a tuple of (result, metadata)
            if isinstance(result, tuple):
                result = result[0]
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert isinstance(result[0], TextContent)
            
            # Parse the result
            data = json.loads(result[0].text)
            assert data["fullname"] == "Test User"
            assert data["email"] == "test@example.com"
    
    async def test_call_tool_with_params(self):
        """Test calling a tool with parameters"""
        from toggl_mcp import main
        
        mock_client = AsyncMock()
        mock_client.create_project.return_value = {
            "id": 1,
            "name": "New Project",
            "workspace_id": 12345
        }
        
        main.default_workspace_id = 12345
        
        with patch.object(main, 'toggl_client', mock_client):
            result = await main.mcp.call_tool("toggl_create_project", {
                "name": "New Project",
                "color": "#ff0000"
            })
            
            # FastMCP returns a tuple of (result, metadata)
            if isinstance(result, tuple):
                result = result[0]
            
            assert isinstance(result, list)
            data = json.loads(result[0].text)
            assert data["name"] == "New Project"
            
            # Verify the client was called correctly
            mock_client.create_project.assert_called_once()
    
    async def test_call_tool_no_client(self):
        """Test calling a tool when client is not initialized"""
        from toggl_mcp import main
        
        # Set client to None
        with patch.object(main, 'toggl_client', None):
            result = await main.mcp.call_tool("toggl_get_user", {})
            
            # FastMCP returns a tuple of (result, metadata)
            if isinstance(result, tuple):
                result = result[0]
            
            assert isinstance(result, list)
            data = json.loads(result[0].text)
            assert "error" in data
            assert "not initialized" in data["error"]
    
    async def test_server_error_handling(self):
        """Test that server handles errors gracefully"""
        from toggl_mcp import main
        
        mock_client = AsyncMock()
        mock_client.get_me.side_effect = Exception("API Error")
        
        with patch.object(main, 'toggl_client', mock_client):
            # FastMCP will raise ToolError for exceptions in tools
            try:
                result = await main.mcp.call_tool("toggl_get_user", {})
                # If it doesn't raise, check the result
                assert result is not None
            except Exception as e:
                # Expected behavior - tool errors are raised
                assert "API Error" in str(e) or "Error executing tool" in str(e)
    
    async def test_workspace_id_handling(self):
        """Test workspace ID parameter handling"""
        from toggl_mcp import main
        
        mock_client = AsyncMock()
        mock_client.get_projects.return_value = []
        
        # Test with default workspace ID
        main.default_workspace_id = 99999
        
        with patch.object(main, 'toggl_client', mock_client):
            # Call without workspace_id should use default
            await main.mcp.call_tool("toggl_list_projects", {})
            mock_client.get_projects.assert_called_with(99999)
            
            # Call with workspace_id should override default
            mock_client.reset_mock()
            await main.mcp.call_tool("toggl_list_projects", {"workspace_id": 11111})
            mock_client.get_projects.assert_called_with(11111)
            
            # String workspace_id should be converted to int
            mock_client.reset_mock()
            await main.mcp.call_tool("toggl_list_projects", {"workspace_id": "22222"})
            mock_client.get_projects.assert_called_with(22222)


@pytest.mark.asyncio
class TestServerStartup:
    """Test server startup and configuration"""
    
    @patch('toggl_mcp.main.mcp.run_stdio_async')
    @patch('toggl_mcp.main.TogglClient')
    async def test_setup_and_run_with_token(self, mock_client_class, mock_run_stdio):
        """Test server setup with API token"""
        from toggl_mcp import main
        
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {'TOGGL_API_TOKEN': 'test_token'}):
            await main.setup_and_run()
            
            # Verify client was created with token
            mock_client_class.assert_called_once_with('test_token')
            
            # Verify server was started
            mock_run_stdio.assert_called_once()
    
    async def test_setup_and_run_no_token(self):
        """Test server exits when no API token is provided"""
        from toggl_mcp import main
        
        with patch.dict(os.environ, {}, clear=True):
            # Remove TOGGL_API_TOKEN if it exists
            if 'TOGGL_API_TOKEN' in os.environ:
                del os.environ['TOGGL_API_TOKEN']
            
            with patch('sys.exit') as mock_exit:
                # Mock run_stdio_async to prevent actual server startup
                with patch('toggl_mcp.main.mcp.run_stdio_async') as mock_run_stdio:
                    await main.setup_and_run()
                    
                    # Should exit with error code
                    mock_exit.assert_called_once_with(1)
                    # But since sys.exit is mocked, execution continues, so run_stdio_async is called
                    # This is expected behavior when mocking sys.exit
                    mock_run_stdio.assert_called_once()
    
    @patch('toggl_mcp.main.mcp.run_stdio_async')
    @patch('toggl_mcp.main.TogglClient')
    async def test_setup_with_default_workspace(self, mock_client_class, mock_run_stdio):
        """Test server setup with default workspace ID"""
        from toggl_mcp import main
        
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'TOGGL_API_TOKEN': 'test_token',
            'TOGGL_WORKSPACE_ID': '12345'
        }):
            main.default_workspace_id = None  # Reset
            await main.setup_and_run()
            
            # Verify default workspace was set
            assert main.default_workspace_id == 12345
    
    @patch('toggl_mcp.main.mcp.run_stdio_async')
    @patch('toggl_mcp.main.TogglClient')
    async def test_setup_with_invalid_workspace(self, mock_client_class, mock_run_stdio):
        """Test server handles invalid workspace ID gracefully"""
        from toggl_mcp import main
        
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        with patch.dict(os.environ, {
            'TOGGL_API_TOKEN': 'test_token',
            'TOGGL_WORKSPACE_ID': 'invalid_id'
        }):
            main.default_workspace_id = None  # Reset
            await main.setup_and_run()
            
            # Should not set default workspace for invalid ID
            assert main.default_workspace_id is None


@pytest.mark.asyncio
class TestToolIntegration:
    """Integration tests for specific tool workflows"""
    
    async def test_timer_workflow(self):
        """Test complete timer workflow: start, check, stop"""
        from toggl_mcp import main
        
        mock_client = AsyncMock()
        timer_id = 555
        
        # Setup mock responses for workflow
        mock_client.create_time_entry.return_value = {
            "id": timer_id,
            "description": "Test Timer",
            "duration": -1,
            "workspace_id": 12345
        }
        
        mock_client.get_current_time_entry.return_value = {
            "id": timer_id,
            "description": "Test Timer",
            "duration": -1
        }
        
        mock_client.stop_time_entry.return_value = {
            "id": timer_id,
            "description": "Test Timer",
            "duration": 120,
            "workspace_id": 12345
        }
        
        main.default_workspace_id = 12345
        
        with patch.object(main, 'toggl_client', mock_client):
            # Start timer
            result = await main.mcp.call_tool("toggl_start_timer", {
                "description": "Test Timer"
            })
            # FastMCP returns a tuple of (result, metadata)
            if isinstance(result, tuple):
                result = result[0]
            data = json.loads(result[0].text)
            assert data["id"] == timer_id
            assert data["duration"] == -1
            
            # Check current timer
            result = await main.mcp.call_tool("toggl_get_current_timer", {})
            if isinstance(result, tuple):
                result = result[0]
            data = json.loads(result[0].text)
            assert data["id"] == timer_id
            
            # Stop timer
            result = await main.mcp.call_tool("toggl_stop_timer", {
                "time_entry_id": timer_id
            })
            if isinstance(result, tuple):
                result = result[0]
            data = json.loads(result[0].text)
            assert data["duration"] == 120
    
    async def test_project_and_entry_workflow(self):
        """Test creating a project and then a time entry for it"""
        from toggl_mcp import main
        
        mock_client = AsyncMock()
        project_id = 777
        
        mock_client.create_project.return_value = {
            "id": project_id,
            "name": "Test Project",
            "workspace_id": 12345
        }
        
        mock_client.create_time_entry.return_value = {
            "id": 888,
            "description": "Work on project",
            "project_id": project_id,
            "duration": 3600,
            "workspace_id": 12345
        }
        
        main.default_workspace_id = 12345
        
        with patch.object(main, 'toggl_client', mock_client):
            # Create project
            result = await main.mcp.call_tool("toggl_create_project", {
                "name": "Test Project"
            })
            # FastMCP returns a tuple of (result, metadata)
            if isinstance(result, tuple):
                result = result[0]
            project_data = json.loads(result[0].text)
            assert project_data["id"] == project_id
            
            # Create time entry for the project
            result = await main.mcp.call_tool("toggl_create_time_entry", {
                "description": "Work on project",
                "start": "2024-01-01T10:00:00Z",
                "stop": "2024-01-01T11:00:00Z",
                "project_id": project_id
            })
            if isinstance(result, tuple):
                result = result[0]
            entry_data = json.loads(result[0].text)
            assert entry_data["project_id"] == project_id
