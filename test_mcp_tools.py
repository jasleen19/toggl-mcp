#!/usr/bin/env python3
"""
Test script for Toggl MCP tools via the MCP interface
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from main import create_toggl_server
from toggl_client import TogglClient


async def test_mcp_tools():
    """Test MCP tools through the server interface"""
    print("🚀 Testing Toggl MCP Tools\n")
    
    # Initialize globals as in main.py
    import main
    main.toggl_client = TogglClient(os.getenv("TOGGL_API_TOKEN"))
    
    # Get default workspace if set
    workspace_id_str = os.getenv("TOGGL_WORKSPACE_ID")
    if workspace_id_str:
        try:
            main.default_workspace_id = int(workspace_id_str)
        except ValueError:
            pass
    
    server = create_toggl_server()
    
    # Get available tools
    tools = await server.list_tools()
    print(f"📋 Found {len(tools)} available tools\n")
    
    try:
        # Test 1: Get user info
        print("1️⃣ Testing toggl_get_user...")
        result = await server.call_tool("toggl_get_user", {})
        user_data = json.loads(result[0].text)
        print(f"   ✅ User: {user_data.get('fullname', 'Unknown')}")
        
        # Test 2: List workspaces
        print("\n2️⃣ Testing toggl_list_workspaces...")
        result = await server.call_tool("toggl_list_workspaces", {})
        workspaces = json.loads(result[0].text)
        print(f"   ✅ Found {len(workspaces)} workspace(s)")
        workspace_id = workspaces[0]['id'] if workspaces else None
        
        # Test 3: List projects
        print("\n3️⃣ Testing toggl_list_projects...")
        result = await server.call_tool("toggl_list_projects", {"workspace_id": workspace_id})
        projects = json.loads(result[0].text)
        print(f"   ✅ Found {len(projects)} project(s)")
        
        # Test 4: Create a project
        print("\n4️⃣ Testing toggl_create_project...")
        result = await server.call_tool("toggl_create_project", {
            "name": f"MCP Test Project {datetime.now().strftime('%H%M%S')}",
            "workspace_id": workspace_id,
            "color": "#ff0000"
        })
        project = json.loads(result[0].text)
        project_id = project['id']
        print(f"   ✅ Created project: {project['name']} (ID: {project_id})")
        
        # Test 5: Start a timer
        print("\n5️⃣ Testing toggl_start_timer...")
        result = await server.call_tool("toggl_start_timer", {
            "description": "MCP test timer",
            "workspace_id": workspace_id,
            "project_id": project_id
        })
        timer = json.loads(result[0].text)
        timer_id = timer['id']
        print(f"   ✅ Started timer: {timer['description']} (ID: {timer_id})")
        
        # Test 6: Get current timer
        print("\n6️⃣ Testing toggl_get_current_timer...")
        result = await server.call_tool("toggl_get_current_timer", {})
        current = json.loads(result[0].text)
        print(f"   ✅ Current timer: {current.get('description', 'No timer running')}")
        
        # Test 7: Stop timer
        await asyncio.sleep(2)  # Let it run for a bit
        print("\n7️⃣ Testing toggl_stop_timer...")
        result = await server.call_tool("toggl_stop_timer", {
            "time_entry_id": timer_id,
            "workspace_id": workspace_id
        })
        stopped = json.loads(result[0].text)
        print(f"   ✅ Stopped timer after {stopped.get('duration', 0)} seconds")
        
        # Test 8: Create time entry
        print("\n8️⃣ Testing toggl_create_time_entry...")
        start = (datetime.now() - timedelta(hours=2)).isoformat() + "Z"
        stop = (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
        result = await server.call_tool("toggl_create_time_entry", {
            "description": "MCP test entry",
            "start": start,
            "stop": stop,
            "workspace_id": workspace_id,
            "project_id": project_id
        })
        entry = json.loads(result[0].text)
        entry_id = entry['id']
        print(f"   ✅ Created time entry: {entry['description']} (Duration: {entry['duration']}s)")
        
        # Test 9: List time entries
        print("\n9️⃣ Testing toggl_list_time_entries...")
        result = await server.call_tool("toggl_list_time_entries", {
            "start_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "end_date": datetime.now().isoformat()
        })
        entries = json.loads(result[0].text)
        print(f"   ✅ Found {len(entries)} time entries in the last day")
        
        # Test 10: Create a tag
        print("\n🔟 Testing toggl_create_tag...")
        result = await server.call_tool("toggl_create_tag", {
            "name": f"mcp-test-{datetime.now().strftime('%H%M%S')}",
            "workspace_id": workspace_id
        })
        tag = json.loads(result[0].text)
        tag_id = tag['id']
        print(f"   ✅ Created tag: {tag['name']} (ID: {tag_id})")
        
        # Test 11: List tags
        print("\n1️⃣1️⃣ Testing toggl_list_tags...")
        result = await server.call_tool("toggl_list_tags", {"workspace_id": workspace_id})
        tags = json.loads(result[0].text)
        print(f"   ✅ Found {len(tags)} tag(s)")
        
        # Test 12: Bulk create time entries
        print("\n1️⃣2️⃣ Testing toggl_bulk_create_time_entries...")
        entries_data = []
        for i in range(3):
            start = (datetime.now() - timedelta(hours=i+4)).isoformat() + "Z"
            stop = (datetime.now() - timedelta(hours=i+3)).isoformat() + "Z"
            entries_data.append({
                "description": f"Bulk MCP entry {i+1}",
                "start": start,
                "stop": stop
            })
        
        result = await server.call_tool("toggl_bulk_create_time_entries", {
            "time_entries": entries_data,
            "workspace_id": workspace_id
        })
        bulk_entries = json.loads(result[0].text)
        bulk_ids = [e['id'] for e in bulk_entries]
        print(f"   ✅ Created {len(bulk_entries)} entries in bulk")
        
        # Test 13: Bulk update
        print("\n1️⃣3️⃣ Testing toggl_bulk_update_time_entries...")
        result = await server.call_tool("toggl_bulk_update_time_entries", {
            "time_entry_ids": bulk_ids[:2],
            "updates": {"description": "Bulk updated via MCP"},
            "workspace_id": workspace_id
        })
        print(f"   ✅ Updated {len(bulk_ids[:2])} entries in bulk")
        
        # Test 14: List project tasks
        print("\n1️⃣4️⃣ Testing toggl_list_project_tasks...")
        result = await server.call_tool("toggl_list_project_tasks", {
            "project_id": project_id,
            "workspace_id": workspace_id
        })
        tasks = json.loads(result[0].text)
        print(f"   ✅ Found {len(tasks)} task(s) (tasks may not be enabled)")
        
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        
        # Delete time entries
        all_test_ids = [timer_id, entry_id] + bulk_ids
        result = await server.call_tool("toggl_bulk_delete_time_entries", {
            "time_entry_ids": all_test_ids,
            "workspace_id": workspace_id
        })
        print(f"   ✅ Deleted {len(all_test_ids)} test time entries")
        
        # Delete tag
        await main.toggl_client.delete_tag(workspace_id, tag_id)
        print(f"   ✅ Deleted test tag")
        
        # Delete project
        await main.toggl_client.delete_project(workspace_id, project_id)
        print(f"   ✅ Deleted test project")
        
        print("\n✅ All MCP tool tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if main.toggl_client:
            await main.toggl_client.close()


async def main():
    """Main entry point"""
    # Check for API token
    if not os.getenv("TOGGL_API_TOKEN"):
        print("❌ TOGGL_API_TOKEN environment variable not set")
        print("Please set it with: export TOGGL_API_TOKEN=your_api_token_here")
        sys.exit(1)
    
    success = await test_mcp_tools()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
