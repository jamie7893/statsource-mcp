#!/usr/bin/env python3
"""
Backward compatibility script for running the MCP server.
This allows users to run the server using the old method:
python mcp_server.py
"""

from mcp_server_stats.server import run_server

if __name__ == "__main__":
    print("Note: For better compatibility, consider using 'python -m mcp_server_stats' instead.")
    run_server() 