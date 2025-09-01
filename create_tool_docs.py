#!/usr/bin/env python3
"""
Create comprehensive tool documentation from code inspection
"""

import ast
import inspect
from typing import get_type_hints, get_origin, get_args
from toggl_mcp import main
import json

def extract_tool_info():
    """Extract tool information by inspecting the code"""
    # Import the mcp object which has all the tools registered
    from toggl_mcp.main import mcp
    
    tools = []
    
    # FastMCP stores tools in mcp._tools
    if hasattr(mcp, '_tools'):
        for tool_name, tool_func in mcp._tools.items():
            # Get function signature
            sig = inspect.signature(tool_func)
            
            # Get docstring
            doc = inspect.getdoc(tool_func) or "No description available"
            
            # Parse parameters
            parameters = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                # Skip 'self' if present
                if param_name == 'self':
                    continue
                    
                # Get type annotation
                param_type = "any"
                if param.annotation != inspect.Parameter.empty:
                    if hasattr(param.annotation, '__name__'):
                        param_type = param.annotation.__name__
                    else:
                        param_type = str(param.annotation).replace('typing.', '')
                
                # Check if required (no default value)
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
                
                # Extract parameter description from docstring
                param_desc = "No description available"
                if "Args:" in doc:
                    lines = doc.split('\n')
                    for i, line in enumerate(lines):
                        if param_name + ":" in line:
                            param_desc = line.split(':', 1)[1].strip()
                            # Continue reading multi-line descriptions
                            j = i + 1
                            while j < len(lines) and lines[j].startswith('            '):
                                param_desc += ' ' + lines[j].strip()
                                j += 1
                            break
                
                parameters[param_name] = {
                    "type": param_type,
                    "description": param_desc,
                    "required": param.default == inspect.Parameter.empty
                }
            
            # Extract main description (before Args:)
            main_desc = doc.split('\n')[0] if doc else "No description available"
            
            tools.append({
                "name": tool_name,
                "description": main_desc,
                "parameters": parameters,
                "required": required
            })
    
    return tools

def generate_markdown(tools):
    """Generate markdown documentation"""
    doc = """# Toggl MCP Tools Documentation

This document provides comprehensive documentation for all available tools in the Toggl MCP server, including all parameters with their types and whether they are required or optional.

## Tool Categories

"""
    
    # Categorize tools
    categories = {
        "User & Workspace Management": [],
        "Project Management": [],
        "Time Entry Management": [],
        "Timer Controls": [],
        "Tag Management": [],
        "Client Management": [],
        "Task Management": []
    }
    
    for tool in tools:
        name = tool['name']
        if 'user' in name or 'workspace' in name or 'organization' in name:
            categories["User & Workspace Management"].append(tool)
        elif 'project' in name and 'task' not in name:
            categories["Project Management"].append(tool)
        elif 'timer' in name:
            categories["Timer Controls"].append(tool)
        elif 'time' in name:
            categories["Time Entry Management"].append(tool)
        elif 'tag' in name:
            categories["Tag Management"].append(tool)
        elif 'client' in name:
            categories["Client Management"].append(tool)
        elif 'task' in name:
            categories["Task Management"].append(tool)
    
    # Generate docs for each category
    for category, category_tools in categories.items():
        if not category_tools:
            continue
            
        doc += f"## {category}\n\n"
        
        for tool in sorted(category_tools, key=lambda x: x['name']):
            doc += f"### `{tool['name']}`\n\n"
            doc += f"**Description:** {tool['description']}\n\n"
            
            if tool['parameters']:
                doc += "**Parameters:**\n\n"
                doc += "| Parameter | Type | Required | Description |\n"
                doc += "|-----------|------|----------|-------------|\n"
                
                # Sort parameters: required first
                sorted_params = sorted(
                    tool['parameters'].items(),
                    key=lambda x: (not x[1]['required'], x[0])
                )
                
                for param_name, param_info in sorted_params:
                    required = "✅ Yes" if param_info['required'] else "❌ No"
                    param_type = param_info['type'].replace('Optional[', '').replace(']', '').replace('List[', 'array<').replace(']', '>')
                    desc = param_info['description']
                    doc += f"| `{param_name}` | {param_type} | {required} | {desc} |\n"
            else:
                doc += "_This tool requires no parameters._\n"
            
            doc += "\n"
    
    # Add examples section
    doc += """## Usage Examples

### Starting a Timer
```json
{
  "tool": "toggl_start_timer",
  "arguments": {
    "description": "Working on API documentation",
    "project_id": 12345,
    "tags": ["documentation", "api"],
    "billable": true
  }
}
```

### Creating a Time Entry
```json
{
  "tool": "toggl_create_time_entry",
  "arguments": {
    "description": "Code review",
    "start": "2025-01-03T09:00:00Z",
    "stop": "2025-01-03T10:30:00Z",
    "project_id": 12345,
    "task_id": 67890,
    "billable": true,
    "tags": ["review", "backend"]
  }
}
```

### Listing Time Entries
```json
{
  "tool": "toggl_list_time_entries",
  "arguments": {
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2025-01-03T23:59:59Z"
  }
}
```

## Important Notes

1. **Workspace ID**: Most tools accept an optional `workspace_id` parameter. If not provided, the default workspace from the `TOGGL_WORKSPACE_ID` environment variable will be used.

2. **Date/Time Format**: All date and time parameters must be in ISO 8601 format (e.g., "2025-01-03T14:30:00Z").

3. **IDs vs Names**: When referencing projects, tasks, or tags, you typically need to use their numeric IDs, not names. Use the list tools to find the appropriate IDs.

4. **Running Timers**: To start a timer (running time entry), use `toggl_start_timer`. The timer will continue running until you call `toggl_stop_timer`.

5. **Bulk Operations**: For creating, updating, or deleting multiple time entries at once, use the bulk operation tools which are more efficient than individual operations.
"""
    
    return doc

def main():
    print("📚 Generating Toggl MCP tools documentation...\n")
    
    try:
        tools = extract_tool_info()
        print(f"✅ Found {len(tools)} tools\n")
        
        # Generate markdown
        doc = generate_markdown(tools)
        
        # Save documentation
        with open('TOOLS_DOCUMENTATION.md', 'w') as f:
            f.write(doc)
        print("✅ Documentation saved to TOOLS_DOCUMENTATION.md")
        
        # Save JSON schema
        with open('tool_schemas.json', 'w') as f:
            json.dump(tools, f, indent=2)
        print("✅ Tool schemas saved to tool_schemas.json")
        
        # Print summary
        print("\n📊 Tool Summary:")
        print(f"   Total tools: {len(tools)}")
        for tool in tools:
            req_count = len(tool['required'])
            opt_count = len(tool['parameters']) - req_count
            print(f"   - {tool['name']}: {req_count} required, {opt_count} optional parameters")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
