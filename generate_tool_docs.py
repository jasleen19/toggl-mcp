#!/usr/bin/env python3
"""
Generate comprehensive documentation for all Toggl MCP tools
"""

import json
import subprocess
import sys
import os
from typing import Dict, Any

def get_tool_definitions():
    """Get tool definitions from the MCP server"""
    env = os.environ.copy()
    env['TOGGL_API_TOKEN'] = 'test_token'
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, '-m', 'toggl_mcp'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True
    )
    
    # Send requests
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "1.0.0", "capabilities": {}, "clientInfo": {"name": "doc-generator", "version": "1.0.0"}}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    ]
    
    responses = []
    try:
        for req in requests:
            process.stdin.write(json.dumps(req) + '\n')
            process.stdin.flush()
            
        # Read responses
        for _ in range(len(requests)):
            line = process.stdout.readline()
            if line:
                responses.append(json.loads(line.strip()))
                
    finally:
        process.terminate()
        process.wait()
    
    # Find tools response
    for resp in responses:
        if resp.get('id') == 2 and 'result' in resp:
            return resp['result'].get('tools', [])
    
    return []

def format_parameter(name: str, schema: Dict[str, Any], required: bool) -> str:
    """Format a parameter for documentation"""
    param_type = schema.get('type', 'any')
    desc = schema.get('description', 'No description available')
    
    # Handle array types
    if param_type == 'array' and 'items' in schema:
        item_type = schema['items'].get('type', 'any')
        param_type = f"array<{item_type}>"
    
    # Format the parameter line
    status = "**Required**" if required else "_Optional_"
    return f"  - `{name}` ({param_type}): {desc} - {status}"

def generate_markdown_docs(tools):
    """Generate markdown documentation for tools"""
    doc = """# Toggl MCP Tools Documentation

This document provides comprehensive documentation for all available tools in the Toggl MCP server.

## Overview

The Toggl MCP server provides tools for interacting with the Toggl Track API v9. Each tool clearly indicates which parameters are required and which are optional.

## Available Tools

"""
    
    # Group tools by category
    categories = {
        "User & Workspace": [],
        "Projects": [],
        "Time Entries": [],
        "Tags": [],
        "Clients": [],
        "Tasks": [],
        "Bulk Operations": []
    }
    
    for tool in tools:
        name = tool['name']
        if 'user' in name or 'workspace' in name or 'organization' in name:
            categories["User & Workspace"].append(tool)
        elif 'project' in name and 'task' not in name:
            categories["Projects"].append(tool)
        elif 'time' in name or 'timer' in name:
            if 'bulk' in name:
                categories["Bulk Operations"].append(tool)
            else:
                categories["Time Entries"].append(tool)
        elif 'tag' in name:
            categories["Tags"].append(tool)
        elif 'client' in name:
            categories["Clients"].append(tool)
        elif 'task' in name:
            categories["Tasks"].append(tool)
        elif 'bulk' in name:
            categories["Bulk Operations"].append(tool)
    
    # Generate documentation for each category
    for category, category_tools in categories.items():
        if not category_tools:
            continue
            
        doc += f"### {category}\n\n"
        
        for tool in sorted(category_tools, key=lambda x: x['name']):
            doc += f"#### `{tool['name']}`\n\n"
            doc += f"{tool['description']}\n\n"
            
            if 'inputSchema' in tool:
                schema = tool['inputSchema']
                properties = schema.get('properties', {})
                required = schema.get('required', [])
                
                if properties:
                    doc += "**Parameters:**\n\n"
                    
                    # Sort parameters: required first, then alphabetical
                    sorted_params = sorted(
                        properties.items(),
                        key=lambda x: (x[0] not in required, x[0])
                    )
                    
                    for param_name, param_schema in sorted_params:
                        is_required = param_name in required
                        doc += format_parameter(param_name, param_schema, is_required) + "\n"
                else:
                    doc += "_No parameters required_\n"
            else:
                doc += "_No parameters required_\n"
            
            doc += "\n"
    
    return doc

def generate_api_comparison():
    """Generate comparison with actual Toggl API parameters"""
    from toggl_mcp.api_params import API_ENDPOINTS
    
    doc = """## API Parameter Comparison

This section shows how our MCP tools map to the actual Toggl API endpoints and their parameters.

"""
    
    for endpoint_group, endpoints in API_ENDPOINTS.items():
        doc += f"### {endpoint_group.replace('_', ' ').title()}\n\n"
        
        for operation, params in endpoints.items():
            doc += f"#### {operation.replace('_', ' ').title()}\n\n"
            doc += f"**Required Parameters:** {', '.join(f'`{p}`' for p in params['required'])}\n\n"
            if params['optional']:
                doc += f"**Optional Parameters:** {', '.join(f'`{p}`' for p in params['optional'])}\n\n"
            else:
                doc += "_No optional parameters_\n\n"
    
    return doc

def main():
    print("📚 Generating Toggl MCP tools documentation...\n")
    
    # Get tool definitions
    tools = get_tool_definitions()
    
    if not tools:
        print("❌ Failed to get tool definitions")
        return
    
    print(f"✅ Found {len(tools)} tools\n")
    
    # Generate documentation
    doc = generate_markdown_docs(tools)
    doc += generate_api_comparison()
    
    # Save to file
    with open('TOOLS_DOCUMENTATION.md', 'w') as f:
        f.write(doc)
    
    print("✅ Documentation saved to TOOLS_DOCUMENTATION.md")
    
    # Also generate a JSON file with all tool schemas
    tool_schemas = {
        tool['name']: {
            'description': tool['description'],
            'parameters': tool.get('inputSchema', {})
        }
        for tool in tools
    }
    
    with open('tool_schemas.json', 'w') as f:
        json.dump(tool_schemas, f, indent=2)
    
    print("✅ Tool schemas saved to tool_schemas.json")

if __name__ == "__main__":
    main()
