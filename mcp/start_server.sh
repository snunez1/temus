#!/bin/bash
# Start script for Wind Farm Analytics MCP Server
# This script is called by VS Code's MCP integration

cd /workspaces/temus
export PYTHONPATH="/workspaces/temus:$PYTHONPATH"
exec python3 /workspaces/temus/mcp/server.py
