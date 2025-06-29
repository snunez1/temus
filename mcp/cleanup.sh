#!/bin/bash
# MCP Directory Cleanup Script
# Run this if unwanted test files reappear after switching VS Code sessions

cd "$(dirname "$0")"

echo "🧹 Cleaning up MCP directory..."

# Remove test files
rm -f test_*.py debug_*.py validate_*.py verify_*.py final_*.py simple_*.py

# Remove backup files  
rm -f *_backup.py server_new.py

# Remove shell test scripts
rm -f test_*.sh debug_*.sh start_server_new.sh

# Remove development files
rm -f code_analysis.py demo_*.py

# Remove documentation files that belong in docs/
rm -f IMPLEMENTATION_SUMMARY.md PHASE1_COMPLETE.md TESTING_GUIDE.md
rm -f design-choices.md tool-design.md tools-implementation.md
rm -f phase-1-tool-implementation.md

# Remove cache and logs
rm -rf __pycache__ .pytest_cache *.log

echo "✅ MCP directory cleaned!"
echo "📁 Essential files remaining:"
ls -la | grep -v "^total" | grep -v "^d" | awk '{print "   " $9}'

echo ""
echo "🚀 To start the MCP server: ./start_server.sh"
