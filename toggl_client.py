"""
Toggl API v9 Client
"""

from base64 import b64encode
from typing import Dict, List, Optional
import httpx


class TogglClient:
    """Client for interacting with Toggl API v9"""
    
    BASE_URL = "https://api.track.toggl.com/api/v9"
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = self._get_headers()
        self.client = httpx.AsyncClient()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        auth = b64encode(f"{self.api_token}:api_token".encode()).decode()
        return {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        }
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make an API request"""
        url = f"{self.BASE_URL}{endpoint}"
        response = await self.client.request(
            method, url, headers=self.headers, **kwargs
        )
        response.raise_for_status()
        return response.json() if response.content else {}
    
    async def get_me(self) -> Dict:
        """Get current user information"""
        return await self._request("GET", "/me")
    
    async def get_workspaces(self) -> List[Dict]:
        """Get all workspaces"""
        return await self._request("GET", "/workspaces")
    
    async def get_projects(self, workspace_id: int) -> List[Dict]:
        """Get all projects in a workspace"""
        return await self._request("GET", f"/workspaces/{workspace_id}/projects")
    
    async def create_project(self, workspace_id: int, name: str, **kwargs) -> Dict:
        """Create a new project"""
        data = {"name": name, **kwargs}
        return await self._request("POST", f"/workspaces/{workspace_id}/projects", json=data)
    
    async def update_project(self, workspace_id: int, project_id: int, **kwargs) -> Dict:
        """Update a project"""
        return await self._request("PUT", f"/workspaces/{workspace_id}/projects/{project_id}", json=kwargs)
    
    async def delete_project(self, workspace_id: int, project_id: int) -> Dict:
        """Delete a project"""
        return await self._request("DELETE", f"/workspaces/{workspace_id}/projects/{project_id}")
    
    async def get_time_entries(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Get time entries"""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self._request("GET", "/me/time_entries", params=params)
    
    async def get_current_time_entry(self) -> Optional[Dict]:
        """Get the currently running time entry"""
        result = await self._request("GET", "/me/time_entries/current")
        return result if result else None
    
    async def create_time_entry(self, workspace_id: int, description: str, **kwargs) -> Dict:
        """Create a new time entry"""
        data = {
            "workspace_id": workspace_id,
            "description": description,
            "created_with": "toggl-mcp",
            **kwargs
        }
        return await self._request("POST", f"/workspaces/{workspace_id}/time_entries", json=data)
    
    async def update_time_entry(self, workspace_id: int, time_entry_id: int, **kwargs) -> Dict:
        """Update a time entry"""
        return await self._request("PUT", f"/workspaces/{workspace_id}/time_entries/{time_entry_id}", json=kwargs)
    
    async def delete_time_entry(self, workspace_id: int, time_entry_id: int) -> Dict:
        """Delete a time entry"""
        return await self._request("DELETE", f"/workspaces/{workspace_id}/time_entries/{time_entry_id}")
    
    async def stop_time_entry(self, workspace_id: int, time_entry_id: int) -> Dict:
        """Stop a running time entry"""
        return await self._request("PATCH", f"/workspaces/{workspace_id}/time_entries/{time_entry_id}/stop")
    
    async def get_tags(self, workspace_id: int) -> List[Dict]:
        """Get all tags in a workspace"""
        return await self._request("GET", f"/workspaces/{workspace_id}/tags")
    
    async def create_tag(self, workspace_id: int, name: str) -> Dict:
        """Create a new tag"""
        data = {"name": name}
        return await self._request("POST", f"/workspaces/{workspace_id}/tags", json=data)
    
    async def update_tag(self, workspace_id: int, tag_id: int, name: str) -> Dict:
        """Update a tag"""
        data = {"name": name}
        return await self._request("PUT", f"/workspaces/{workspace_id}/tags/{tag_id}", json=data)
    
    async def delete_tag(self, workspace_id: int, tag_id: int) -> Dict:
        """Delete a tag"""
        return await self._request("DELETE", f"/workspaces/{workspace_id}/tags/{tag_id}")
    
    async def get_clients(self, workspace_id: int) -> List[Dict]:
        """Get all clients in a workspace"""
        return await self._request("GET", f"/workspaces/{workspace_id}/clients")
    
    async def create_client(self, workspace_id: int, name: str) -> Dict:
        """Create a new client"""
        data = {"name": name}
        return await self._request("POST", f"/workspaces/{workspace_id}/clients", json=data)
    
    async def get_workspace_users(self, workspace_id: int) -> List[Dict]:
        """Get all users in a workspace"""
        return await self._request("GET", f"/workspaces/{workspace_id}/users")
    
    async def get_organizations(self) -> List[Dict]:
        """Get user's organizations"""
        return await self._request("GET", "/organizations")
    
    # Bulk operations
    async def bulk_create_time_entries(self, workspace_id: int, time_entries: List[Dict]) -> List[Dict]:
        """Create multiple time entries at once"""
        return await self._request("POST", f"/workspaces/{workspace_id}/time_entries", json=time_entries)
    
    async def bulk_update_time_entries(self, workspace_id: int, time_entry_ids: List[int], updates: Dict) -> Dict:
        """Update multiple time entries at once"""
        time_entry_ids_str = ",".join(map(str, time_entry_ids))
        return await self._request("PATCH", f"/workspaces/{workspace_id}/time_entries/{time_entry_ids_str}", json=updates)
    
    async def bulk_delete_time_entries(self, workspace_id: int, time_entry_ids: List[int]) -> Dict:
        """Delete multiple time entries at once"""
        time_entry_ids_str = ",".join(map(str, time_entry_ids))
        return await self._request("DELETE", f"/workspaces/{workspace_id}/time_entries/{time_entry_ids_str}")
    
    # Project tasks (if enabled)
    async def get_project_tasks(self, workspace_id: int, project_id: int) -> List[Dict]:
        """Get tasks for a project (only if tasks are enabled for the project)"""
        try:
            return await self._request("GET", f"/workspaces/{workspace_id}/projects/{project_id}/tasks")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []  # Tasks not enabled for this project
            raise
    
    async def create_project_task(self, workspace_id: int, project_id: int, name: str) -> Dict:
        """Create a task for a project"""
        data = {"name": name}
        return await self._request("POST", f"/workspaces/{workspace_id}/projects/{project_id}/tasks", json=data)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
