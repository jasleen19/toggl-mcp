#!/usr/bin/env python3
"""
Comprehensive test script for all Toggl MCP operations
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from toggl_client import TogglClient
import json


class TogglTester:
    def __init__(self):
        self.api_token = os.getenv("TOGGL_API_TOKEN")
        if not self.api_token:
            raise ValueError("TOGGL_API_TOKEN environment variable not set")
        
        self.client = TogglClient(self.api_token)
        self.workspace_id = None
        self.test_project_id = None
        self.test_time_entry_ids = []
        self.test_tag_id = None
        self.test_client_id = None
    
    async def setup(self):
        """Set up test environment"""
        print("🔧 Setting up test environment...")
        
        # Get user info
        user_info = await self.client.get_me()
        print(f"✅ Authenticated as: {user_info.get('fullname', 'Unknown')}")
        
        # Get first workspace
        workspaces = await self.client.get_workspaces()
        if not workspaces:
            raise ValueError("No workspaces found")
        
        self.workspace_id = workspaces[0]['id']
        print(f"✅ Using workspace: {workspaces[0]['name']} (ID: {self.workspace_id})")
    
    async def test_workspace_operations(self):
        """Test workspace-related operations"""
        print("\n📁 Testing Workspace Operations...")
        
        # List workspaces
        workspaces = await self.client.get_workspaces()
        print(f"  ✅ Found {len(workspaces)} workspace(s)")
        
        # Get organizations
        orgs = await self.client.get_organizations()
        print(f"  ✅ Found {len(orgs)} organization(s)")
        
        return True
    
    async def test_project_operations(self):
        """Test project CRUD operations"""
        print("\n📋 Testing Project Operations...")
        
        # Create a test project
        project_data = await self.client.create_project(
            self.workspace_id,
            f"Test Project {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            color="#06aaf5",
            is_private=False
        )
        self.test_project_id = project_data['id']
        print(f"  ✅ Created project: {project_data['name']} (ID: {self.test_project_id})")
        
        # List projects
        projects = await self.client.get_projects(self.workspace_id)
        print(f"  ✅ Listed {len(projects)} project(s)")
        
        # Update project
        updated = await self.client.update_project(
            self.workspace_id,
            self.test_project_id,
            name=f"Updated Test Project {datetime.now().strftime('%H%M%S')}",
            color="#ff6600"
        )
        print(f"  ✅ Updated project: {updated['name']}")
        
        return True
    
    async def test_time_entry_operations(self):
        """Test time entry CRUD operations"""
        print("\n⏱️  Testing Time Entry Operations...")
        
        # Create a time entry
        start_time = (datetime.now() - timedelta(hours=2)).isoformat() + "Z"
        stop_time = (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
        
        entry = await self.client.create_time_entry(
            self.workspace_id,
            "Test time entry",
            start=start_time,
            stop=stop_time,
            duration=3600,
            project_id=self.test_project_id if self.test_project_id else None
        )
        self.test_time_entry_ids.append(entry['id'])
        print(f"  ✅ Created time entry: {entry['description']} (ID: {entry['id']})")
        
        # List time entries
        entries = await self.client.get_time_entries()
        print(f"  ✅ Listed {len(entries)} time entries")
        
        # Update time entry
        updated = await self.client.update_time_entry(
            self.workspace_id,
            entry['id'],
            description="Updated test time entry"
        )
        print(f"  ✅ Updated time entry: {updated['description']}")
        
        return True
    
    async def test_timer_operations(self):
        """Test timer start/stop operations"""
        print("\n⏰ Testing Timer Operations...")
        
        # Check current timer
        current = await self.client.get_current_time_entry()
        if current:
            print(f"  ⚠️  Found running timer: {current['description']}, stopping it...")
            await self.client.stop_time_entry(self.workspace_id, current['id'])
        
        # Start a new timer
        timer = await self.client.create_time_entry(
            self.workspace_id,
            "Test timer",
            start=datetime.now().isoformat() + "Z",
            duration=-1,  # Running timer
            project_id=self.test_project_id if self.test_project_id else None
        )
        self.test_time_entry_ids.append(timer['id'])
        print(f"  ✅ Started timer: {timer['description']} (ID: {timer['id']})")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Stop the timer
        stopped = await self.client.stop_time_entry(self.workspace_id, timer['id'])
        print(f"  ✅ Stopped timer after {stopped.get('duration', 0)} seconds")
        
        return True
    
    async def test_bulk_operations(self):
        """Test bulk time entry operations"""
        print("\n📦 Testing Bulk Operations...")
        
        # Create multiple time entries
        now = datetime.now()
        entries_data = []
        for i in range(3):
            start = (now - timedelta(hours=i+3)).isoformat() + "Z"
            stop = (now - timedelta(hours=i+2)).isoformat() + "Z"
            entries_data.append({
                "description": f"Bulk test entry {i+1}",
                "start": start,
                "stop": stop,
                "duration": 3600,
                "workspace_id": self.workspace_id,
                "created_with": "toggl-mcp"
            })
        
        created = await self.client.bulk_create_time_entries(self.workspace_id, entries_data)
        bulk_ids = [e['id'] for e in created]
        self.test_time_entry_ids.extend(bulk_ids)
        print(f"  ✅ Created {len(created)} time entries in bulk")
        
        # Bulk update
        updates = {
            "description": "Bulk updated entry",
            "project_id": self.test_project_id if self.test_project_id else None
        }
        await self.client.bulk_update_time_entries(self.workspace_id, bulk_ids[:2], updates)
        print(f"  ✅ Updated {len(bulk_ids[:2])} time entries in bulk")
        
        # Bulk delete (only the last one to keep some for cleanup)
        await self.client.bulk_delete_time_entries(self.workspace_id, [bulk_ids[-1]])
        self.test_time_entry_ids.remove(bulk_ids[-1])
        print(f"  ✅ Deleted 1 time entry in bulk")
        
        return True
    
    async def test_tag_operations(self):
        """Test tag operations"""
        print("\n🏷️  Testing Tag Operations...")
        
        # Create a tag
        tag = await self.client.create_tag(
            self.workspace_id,
            f"test-tag-{datetime.now().strftime('%H%M%S')}"
        )
        self.test_tag_id = tag['id']
        print(f"  ✅ Created tag: {tag['name']} (ID: {tag['id']})")
        
        # List tags
        tags = await self.client.get_tags(self.workspace_id)
        print(f"  ✅ Listed {len(tags)} tag(s)")
        
        # Update tag
        updated = await self.client.update_tag(
            self.workspace_id,
            tag['id'],
            f"updated-tag-{datetime.now().strftime('%H%M%S')}"
        )
        print(f"  ✅ Updated tag: {updated['name']}")
        
        return True
    
    async def test_client_operations(self):
        """Test client operations"""
        print("\n👥 Testing Client Operations...")
        
        # Create a client
        client = await self.client.create_client(
            self.workspace_id,
            f"Test Client {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.test_client_id = client['id']
        print(f"  ✅ Created client: {client['name']} (ID: {client['id']})")
        
        # List clients
        clients = await self.client.get_clients(self.workspace_id)
        print(f"  ✅ Listed {len(clients)} client(s)")
        
        return True
    
    async def test_task_operations(self):
        """Test project task operations (if enabled)"""
        print("\n📝 Testing Task Operations...")
        
        if not self.test_project_id:
            print("  ⚠️  No test project available, skipping task tests")
            return True
        
        try:
            # List tasks
            tasks = await self.client.get_project_tasks(self.workspace_id, self.test_project_id)
            print(f"  ✅ Listed {len(tasks)} task(s)")
            
            # Try to create a task
            task = await self.client.create_project_task(
                self.workspace_id,
                self.test_project_id,
                f"Test Task {datetime.now().strftime('%H%M%S')}"
            )
            print(f"  ✅ Created task: {task['name']} (ID: {task['id']})")
            
        except Exception as e:
            print(f"  ℹ️  Tasks not enabled for this project or workspace: {str(e)}")
        
        return True
    
    async def cleanup(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete time entries
        if self.test_time_entry_ids:
            try:
                await self.client.bulk_delete_time_entries(self.workspace_id, self.test_time_entry_ids)
                print(f"  ✅ Deleted {len(self.test_time_entry_ids)} test time entries")
            except Exception as e:
                print(f"  ⚠️  Failed to delete some time entries: {e}")
        
        # Delete tag
        if self.test_tag_id:
            try:
                await self.client.delete_tag(self.workspace_id, self.test_tag_id)
                print(f"  ✅ Deleted test tag")
            except Exception as e:
                print(f"  ⚠️  Failed to delete tag: {e}")
        
        # Delete project
        if self.test_project_id:
            try:
                await self.client.delete_project(self.workspace_id, self.test_project_id)
                print(f"  ✅ Deleted test project")
            except Exception as e:
                print(f"  ⚠️  Failed to delete project: {e}")
        
        # Note: Clients cannot be deleted via API
        if self.test_client_id:
            print(f"  ℹ️  Test client (ID: {self.test_client_id}) cannot be deleted via API")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Running Toggl MCP Comprehensive Tests\n")
        
        try:
            await self.setup()
            
            tests = [
                self.test_workspace_operations,
                self.test_project_operations,
                self.test_time_entry_operations,
                self.test_timer_operations,
                self.test_bulk_operations,
                self.test_tag_operations,
                self.test_client_operations,
                self.test_task_operations,
            ]
            
            passed = 0
            failed = 0
            
            for test in tests:
                try:
                    result = await test()
                    if result:
                        passed += 1
                except Exception as e:
                    print(f"  ❌ Test failed: {str(e)}")
                    failed += 1
            
            print(f"\n📊 Test Results: {passed} passed, {failed} failed")
            
            await self.cleanup()
            
            return failed == 0
            
        finally:
            await self.client.close()


async def main():
    """Main entry point"""
    tester = TogglTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
