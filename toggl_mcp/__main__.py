#!/usr/bin/env python3 -u
"""
Entry point for the toggl-mcp package when run as a module or script
"""

import os
import sys

# Force unbuffered mode for MCP
os.environ['PYTHONUNBUFFERED'] = '1'

from .main import run

if __name__ == "__main__":
    run()
