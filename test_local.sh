#!/bin/bash
# Local test script for Toggl MCP

echo "🔧 Toggl MCP Local Test"
echo "======================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e . > /dev/null 2>&1

# Check for API token
if [ -z "$TOGGL_API_TOKEN" ]; then
    echo ""
    echo "❌ TOGGL_API_TOKEN not set!"
    echo ""
    echo "Please run:"
    echo "  export TOGGL_API_TOKEN='your_token_here'"
    echo ""
    exit 1
fi

echo "✅ Environment ready"
echo ""
echo "Running Toggl MCP server..."
echo "Press Ctrl+C to stop"
echo ""

# Run the server
python3 -m toggl_mcp


