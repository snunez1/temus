#!/bin/bash
# Test MCP integration end-to-end

echo "=== MCP Integration Test ==="
echo

# Test 1: Check if MCP is enabled in VS Code settings
echo "1. Checking MCP settings..."
grep -q "chat.mcp.enabled.*true" /workspaces/temus/.vscode/settings.json && echo "✅ MCP enabled" || echo "❌ MCP not enabled"

# Test 2: Verify MCP configuration file exists and is valid
echo "2. Checking MCP configuration..."
if [ -f "/workspaces/temus/.vscode/mcp.json" ]; then
    echo "✅ MCP config file exists"
    python3 -c "import json; json.load(open('/workspaces/temus/.vscode/mcp.json'))" && echo "✅ MCP config is valid JSON" || echo "❌ MCP config invalid"
else
    echo "❌ MCP config file missing"
fi

# Test 3: Check start script
echo "3. Checking start script..."
if [ -x "/workspaces/temus/mcp/start_server.sh" ]; then
    echo "✅ Start script is executable"
else
    echo "❌ Start script not executable"
fi

# Test 4: Test server can start
echo "4. Testing server startup..."
timeout 2s /workspaces/temus/mcp/start_server.sh > /dev/null 2>&1
if [ $? -eq 143 ]; then  # timeout exit code
    echo "✅ Server starts successfully (killed by timeout as expected)"
else
    echo "❌ Server failed to start"
fi

# Test 5: Test individual tools
echo "5. Testing MCP tools..."
cd /workspaces/temus
python3 -c "
import sys
sys.path.append('mcp')
from test_functions import summarize_wind_farm_standalone
result = summarize_wind_farm_standalone('wf1')
if 'error' not in result:
    print('✅ MCP tools working - WF1 capacity factor:', result['performance_metrics']['capacity_factor'])
else:
    print('❌ MCP tools failed:', result['error'])
"

echo
echo "=== Next Steps ==="
echo "1. Open VS Code Copilot Chat (Ctrl+Alt+I)"
echo "2. Switch to 'Agent' mode"
echo "3. Try: 'Using the windFarmAnalytics server, what's the capacity factor for wind farm wf3?'"
echo
echo "=== Expected Result ==="
echo "VS Code should automatically start the MCP server and call the summarize_wind_farm tool"
