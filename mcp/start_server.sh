#!/bin/bash
# Start the Wind Farm Analytics MCP Server

echo "Starting Wind Farm Analytics MCP Server..."
echo "Server: server.py (Wind Power Forecasting Analysis)"
echo "Port: 8000"
echo ""

cd /workspaces/temus/mcp
python3 server.py

echo "Server stopped."
