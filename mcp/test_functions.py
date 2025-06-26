"""Standalone MCP tool functions for testing

This creates standalone versions of the MCP tools for testing without FastMCP.
"""

import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

# Define data paths
DATA_DIR = Path(__file__).parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"

def summarize_wind_farm_standalone(farm_id: str = "wf1") -> Dict[str, Any]:
    """Standalone version of summarize_wind_farm for testing"""
    
    try:
        # Normalize farm_id input
        farm_id = farm_id.upper() if not farm_id.upper().startswith('WF') else farm_id.upper()
        if not farm_id.startswith('WF'):
            farm_id = f'WF{farm_id}'
        
        # Read pre-computed comparison summary
        summary_file = PROCESSED_DIR / "wind_farm_comparison_summary.json"
        
        if not summary_file.exists():
            return {
                "error": "Wind farm comparison summary not found. Please run analysis notebooks first.",
                "suggestion": "Execute notebooks 01-04 to generate wind farm statistics.",
                "farm_id": farm_id
            }
        
        # Load the comparison summary
        with open(summary_file, 'r') as f:
            summary_data = json.load(f)
        
        # Check if farm exists in data
        available_farms = summary_data['metadata']['wind_farms_analyzed']
        if farm_id not in available_farms:
            return {
                "error": f"No data found for wind farm '{farm_id}'",
                "available_farms": available_farms,
                "farm_id": farm_id
            }
        
        # Extract metrics for the specific farm
        performance = summary_data['performance_metrics']
        capacity_factors = summary_data['capacity_factors']
        
        # Calculate annual generation estimate (assuming 1 MW nameplate capacity)
        capacity_factor = capacity_factors[farm_id]
        annual_generation_mwh = capacity_factor * 8760  # hours per year
        co2_displaced_tons = annual_generation_mwh * 0.5  # 0.5 tons CO2/MWh displacement factor
        
        result = {
            "wind_farm": farm_id,
            "data_period": summary_data['metadata']['data_period'],
            "total_observations": summary_data['metadata']['total_observations'],
            "performance_metrics": {
                "capacity_factor": round(capacity_factor, 4),
                "mean_power_normalized": round(performance['Mean Power (MW)'][farm_id], 4),
                "median_power_normalized": round(performance['Median Power (MW)'][farm_id], 4),
                "max_power_normalized": round(performance['Max Power (MW)'][farm_id], 4),
                "std_deviation": round(performance['Std Dev (MW)'][farm_id], 4),
                "coefficient_variation": round(performance['Coefficient of Variation'][farm_id], 4),
                "zero_generation_hours": int(performance['Zero Generation Hours'][farm_id]),
                "zero_generation_percentage": round(performance['Zero Generation %'][farm_id], 2),
                "peak_events_95th_percentile": int(performance['Peak Power Events (>95th percentile)'][farm_id])
            },
            "estimated_annual_metrics": {
                "annual_generation_mwh_per_mw": round(annual_generation_mwh, 0),
                "co2_displaced_tons_per_mw": round(co2_displaced_tons, 0)
            },
            "data_quality": {
                "availability_percentage": round((1 - performance['Zero Generation %'][farm_id]/100) * 100, 2)
            }
        }
        
        return result
        
    except Exception as e:
        return {
            "error": f"Failed to retrieve statistics: {str(e)}",
            "type": "processing_error",
            "farm_id": farm_id
        }

def test_standalone_functions():
    """Test the standalone functions"""
    
    print("=" * 60)
    print("Testing Standalone MCP Functions")
    print("=" * 60)
    
    # Test 1: Valid wind farm
    print("\n1. Testing WF1...")
    result1 = summarize_wind_farm_standalone("wf1")
    if 'error' in result1:
        print(f"❌ Error: {result1['error']}")
    else:
        print(f"✅ Success for {result1['wind_farm']}")
        print(f"   Capacity Factor: {result1['performance_metrics']['capacity_factor']}")
        print(f"   Annual Generation: {result1['estimated_annual_metrics']['annual_generation_mwh_per_mw']} MWh/MW")
        print(f"   CO2 Displaced: {result1['estimated_annual_metrics']['co2_displaced_tons_per_mw']} tons/MW")
    
    # Test 2: Different input format
    print("\n2. Testing WF3...")
    result2 = summarize_wind_farm_standalone("3")
    if 'error' in result2:
        print(f"❌ Error: {result2['error']}")
    else:
        print(f"✅ Success for {result2['wind_farm']}")
        print(f"   Capacity Factor: {result2['performance_metrics']['capacity_factor']}")
        print(f"   Availability: {result2['data_quality']['availability_percentage']}%")
    
    # Test 3: Invalid wind farm
    print("\n3. Testing invalid farm (WF99)...")
    result3 = summarize_wind_farm_standalone("99")
    if 'error' in result3:
        print(f"✅ Expected error: {result3['error']}")
        print(f"   Available farms: {result3.get('available_farms', 'Not provided')}")
    else:
        print(f"❌ Unexpected success for invalid farm")
    
    print("\n" + "=" * 60)
    print("Standalone Function Testing Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_standalone_functions()
