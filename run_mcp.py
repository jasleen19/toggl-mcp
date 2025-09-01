#!/usr/bin/env python3 -u
"""
Wrapper script to ensure proper MCP execution with unbuffered I/O
"""
import os
import sys

# Force unbuffered mode
os.environ['PYTHONUNBUFFERED'] = '1'
sys.stdout = sys.stdout.reconfigure(line_buffering=True)
sys.stderr = sys.stderr.reconfigure(line_buffering=True)

# Import and run the main function
from toggl_mcp.main import run

if __name__ == "__main__":
    run()

