"""Test MCP server tools without stdio blocking

This script tests the MCP server tools directly to validate functionality
before deploying through VS Code's MCP integration.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the server directory to path
sys.path.append(str(Path(__file__).parent))

# Import the tool functions directly - they should be regular functions now
import server

async def test_tools():
    """Test all MCP tools directly"""
    
    print("=" * 60)
    print("Testing Wind Farm Analytics MCP Server Tools")
    print("=" * 60)
    
    # Import the mcp instance to access tools
    from server import mcp
    
    # Get the actual function implementations
    tools = {}
    for tool in mcp.list_tools():
        tools[tool.name] = tool
    
    # Test 1: Server Status
    print("\n1. Testing server_status tool...")
    try:
        # Find the server_status function directly
        from server import server_status
        status = server_status()
        print(f"✅ Server Status: {status['status']}")
        print(f"   Available tools: {len(status['available_tools'])}")
        print(f"   Data files: {len(status['data_files_available'])}")
    except Exception as e:
        print(f"❌ Server status failed: {e}")
    
    # Test 2: List Available Wind Farms
    print("\n2. Testing list_available_wind_farms tool...")
    try:
        from server import list_available_wind_farms
        farms_list = list_available_wind_farms()
        if 'error' in farms_list:
            print(f"❌ Error: {farms_list['error']}")
        else:
            print(f"✅ Found {farms_list['total_farms']} wind farms")
            print(f"   Available farms: {farms_list['available_wind_farms']}")
            print(f"   Best performer: {farms_list['best_performer']}")
    except Exception as e:
        print(f"❌ List farms failed: {e}")
    
    # Test 3: Summarize Specific Wind Farm
    print("\n3. Testing summarize_wind_farm tool...")
    test_farms = ["wf1", "WF2", "3"]  # Test different input formats
    
    for farm in test_farms:
        try:
            from server import summarize_wind_farm
            result = summarize_wind_farm(farm)
            if 'error' in result:
                print(f"❌ Error for {farm}: {result['error']}")
            else:
                print(f"✅ Summary for {result['wind_farm']}:")
                print(f"   Capacity Factor: {result['performance_metrics']['capacity_factor']}")
                print(f"   Annual Generation: {result['estimated_annual_metrics']['annual_generation_mwh_per_mw']} MWh/MW")
                print(f"   CO2 Displaced: {result['estimated_annual_metrics']['co2_displaced_tons_per_mw']} tons/MW")
        except Exception as e:
            print(f"❌ Summary for {farm} failed: {e}")
    
    # Test 4: Compare Wind Farms
    print("\n4. Testing compare_wind_farms tool...")
    try:
        from server import compare_wind_farms
        # Test with all farms
        comparison = compare_wind_farms()
        if 'error' in comparison:
            print(f"❌ Error: {comparison['error']}")
        else:
            print(f"✅ Compared {len(comparison['farms_compared'])} farms")
            print(f"   Best capacity factor: {comparison['rankings']['best_capacity_factor']}")
            print(f"   Most stable: {comparison['rankings']['most_stable']}")
            
            if 'portfolio_analysis' in comparison:
                print(f"   Portfolio diversification: {comparison['portfolio_analysis']['diversification_benefit']}")
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
    
    # Test 5: Compare Specific Farms
    print("\n5. Testing compare_wind_farms with specific farms...")
    try:
        from server import compare_wind_farms
        specific_comparison = compare_wind_farms("wf1,wf3")
        if 'error' in specific_comparison:
            print(f"❌ Error: {specific_comparison['error']}")
        else:
            print(f"✅ Compared specific farms: {specific_comparison['farms_compared']}")
            cf_values = specific_comparison['comparison_metrics']['capacity_factors']
            for farm, cf in cf_values.items():
                print(f"   {farm}: {cf} capacity factor")
    except Exception as e:
        print(f"❌ Specific comparison failed: {e}")
    
    print("\n" + "=" * 60)
    print("Testing Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_tools())
