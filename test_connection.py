#!/usr/bin/env python3
"""
Test script to verify Toggl API connection
"""

import asyncio
import os
import sys
from toggl_mcp.toggl_client import TogglClient


async def test_connection():
    """Test the Toggl API connection"""
    api_token = os.getenv("TOGGL_API_TOKEN")
    
    if not api_token:
        print("❌ TOGGL_API_TOKEN environment variable not set")
        print("Please set it with: export TOGGL_API_TOKEN=your_api_token_here")
        return False
    
    print("🔧 Testing Toggl API connection...")
    client = TogglClient(api_token)
    
    try:
        # Test API connection by getting user info
        user_info = await client.get_me()
        print(f"✅ Connected successfully!")
        print(f"👤 User: {user_info.get('fullname', 'Unknown')}")
        print(f"📧 Email: {user_info.get('email', 'Unknown')}")
        
        # Get workspaces
        workspaces = await client.get_workspaces()
        print(f"\n📁 Found {len(workspaces)} workspace(s):")
        for ws in workspaces:
            print(f"  - {ws['name']} (ID: {ws['id']})")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        await client.close()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
