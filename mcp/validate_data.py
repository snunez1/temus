"""Simple validation test for wind farm data

This script validates that the required data files exist and can be read.
"""

import json
import pandas as pd
from pathlib import Path

def test_data_availability():
    """Test if required data files exist and are readable"""
    
    print("=" * 60)
    print("Testing Wind Farm Data Availability")
    print("=" * 60)
    
    data_dir = Path("/workspaces/temus/data/processed")
    
    # Test 1: Check if processed directory exists
    print(f"\n1. Checking processed data directory: {data_dir}")
    if data_dir.exists():
        print("✅ Processed data directory exists")
        files = list(data_dir.glob("*"))
        print(f"   Found {len(files)} files")
    else:
        print("❌ Processed data directory not found")
        return
    
    # Test 2: Check for wind farm comparison summary
    summary_file = data_dir / "wind_farm_comparison_summary.json"
    print(f"\n2. Checking summary file: {summary_file.name}")
    if summary_file.exists():
        print("✅ Wind farm comparison summary exists")
        try:
            with open(summary_file, 'r') as f:
                summary_data = json.load(f)
            
            print(f"   Wind farms: {summary_data['metadata']['wind_farms_analyzed']}")
            print(f"   Data period: {summary_data['metadata']['data_period']}")
            print(f"   Observations: {summary_data['metadata']['total_observations']}")
            
            # Test capacity factors
            capacity_factors = summary_data['capacity_factors']
            print("\n   Capacity Factors:")
            for farm, cf in capacity_factors.items():
                print(f"     {farm}: {cf:.4f}")
                
        except Exception as e:
            print(f"❌ Error reading summary: {e}")
    else:
        print("❌ Wind farm comparison summary not found")
    
    # Test 3: Check for other data files
    print(f"\n3. Checking other data files...")
    key_files = [
        "summary_stats.parquet",
        "combined_power_wind.parquet",
        "power_correlations.parquet"
    ]
    
    for filename in key_files:
        filepath = data_dir / filename
        if filepath.exists():
            print(f"✅ {filename} exists")
            try:
                if filename.endswith('.parquet'):
                    df = pd.read_parquet(filepath)
                    print(f"   Shape: {df.shape}")
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
        else:
            print(f"⚠️  {filename} not found")
    
    print("\n" + "=" * 60)
    print("Data validation complete")
    print("=" * 60)

def test_basic_wind_farm_lookup():
    """Test basic wind farm data lookup functionality"""
    
    print("\n" + "=" * 60)
    print("Testing Basic Wind Farm Lookup")
    print("=" * 60)
    
    try:
        summary_file = Path("/workspaces/temus/data/processed/wind_farm_comparison_summary.json")
        
        with open(summary_file, 'r') as f:
            summary_data = json.load(f)
        
        # Test farm lookup
        test_farm = "WF1"
        print(f"\nTesting lookup for {test_farm}:")
        
        available_farms = summary_data['metadata']['wind_farms_analyzed']
        if test_farm in available_farms:
            print(f"✅ {test_farm} found in dataset")
            
            # Extract key metrics
            capacity_factor = summary_data['capacity_factors'][test_farm]
            mean_power = summary_data['performance_metrics']['Mean Power (MW)'][test_farm]
            zero_gen_pct = summary_data['performance_metrics']['Zero Generation %'][test_farm]
            
            print(f"   Capacity Factor: {capacity_factor:.4f}")
            print(f"   Mean Power: {mean_power:.4f}")
            print(f"   Zero Generation %: {zero_gen_pct:.2f}%")
            
            # Calculate estimates
            annual_mwh = capacity_factor * 8760
            co2_displaced = annual_mwh * 0.5
            
            print(f"   Estimated Annual Generation: {annual_mwh:.0f} MWh/MW")
            print(f"   Estimated CO2 Displaced: {co2_displaced:.0f} tons/MW")
            
        else:
            print(f"❌ {test_farm} not found in available farms: {available_farms}")
            
    except Exception as e:
        print(f"❌ Error in basic lookup test: {e}")

if __name__ == "__main__":
    test_data_availability()
    test_basic_wind_farm_lookup()
