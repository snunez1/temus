#!/usr/bin/env python3
"""Wind Farm Analytics MCP Server using FastMCP

This MCP server provides tools for analyzing wind farm data and statistics.
It serves pre-computed analysis results from the processed data directory.
"""

import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Wind Farm Analytics")

# Define data paths
DATA_DIR = Path(__file__).parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / 'mcp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@mcp.tool()
def summarize_wind_farm(farm_id: str = "wf1") -> Dict[str, Any]:
    """
    Summarize statistics for a specific wind farm from the GEF2012 dataset.
    
    Args:
        farm_id: Wind farm identifier (wf1-wf7)
        
    Returns:
        Dictionary containing wind farm statistics including:
        - Basic statistics (mean, std, min, max power output)
        - Capacity factor
        - Wind speed statistics
        - Data quality metrics
    """
    logger.info(f"Received request for wind farm summary: {farm_id}")
    
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
        
        # Add correlation info if multiple farms exist
        correlations = summary_data.get('correlations', {})
        farm_correlations = {}
        for corr_key, corr_value in correlations.items():
            if farm_id in corr_key:
                other_farm = corr_key.replace(f'{farm_id} vs ', '').replace(f' vs {farm_id}', '')
                farm_correlations[other_farm] = round(corr_value, 4)
        
        if farm_correlations:
            result["correlations_with_other_farms"] = farm_correlations
        
        # Add ranking information
        volatility_ranking = summary_data.get('volatility_ranking', {})
        if farm_id in volatility_ranking:
            result["volatility_rank"] = {
                "coefficient_of_variation": volatility_ranking[farm_id],
                "rank_position": list(volatility_ranking.keys()).index(farm_id) + 1,
                "total_farms": len(volatility_ranking)
            }
        
        logger.info(f"Successfully returned summary for {farm_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing wind farm summary for {farm_id}: {str(e)}")
        return {
            "error": f"Failed to retrieve statistics: {str(e)}",
            "type": "processing_error",
            "farm_id": farm_id
        }


@mcp.tool()
def list_available_wind_farms() -> Dict[str, Any]:
    """
    List all available wind farms in the GEF2012 dataset.
    
    Returns:
        Dictionary containing list of wind farm IDs and basic metadata
    """
    logger.info("Received request for available wind farms list")
    
    try:
        summary_file = PROCESSED_DIR / "wind_farm_comparison_summary.json"
        
        if not summary_file.exists():
            return {
                "error": "Wind farm data not found",
                "suggestion": "Run analysis notebooks to generate wind farm data"
            }
        
        with open(summary_file, 'r') as f:
            summary_data = json.load(f)
        
        wind_farms = summary_data['metadata']['wind_farms_analyzed']
        capacity_factors = summary_data['capacity_factors']
        
        # Create summary of all farms
        farms_overview = []
        for farm in wind_farms:
            farms_overview.append({
                "farm_id": farm,
                "capacity_factor": round(capacity_factors[farm], 4),
                "performance_rank": sorted(capacity_factors.items(), 
                                         key=lambda x: x[1], reverse=True).index((farm, capacity_factors[farm])) + 1
            })
        
        return {
            "available_wind_farms": wind_farms,
            "total_farms": len(wind_farms),
            "data_period": summary_data['metadata']['data_period'],
            "total_observations": summary_data['metadata']['total_observations'],
            "farms_overview": farms_overview,
            "best_performer": summary_data['key_insights']['best_performer'],
            "most_stable": summary_data['key_insights']['most_stable']
        }
        
    except Exception as e:
        logger.error(f"Error listing available wind farms: {str(e)}")
        return {
            "error": f"Failed to retrieve wind farm list: {str(e)}",
            "type": "processing_error"
        }


@mcp.tool()
def compare_wind_farms(farm_ids: Optional[str] = None) -> Dict[str, Any]:
    """
    Compare statistics across multiple wind farms.
    
    Args:
        farm_ids: Comma-separated list of farm IDs (e.g., "wf1,wf2,wf3"). 
                 If None, compares all farms.
    
    Returns:
        Dictionary containing comparative statistics across wind farms
    """
    logger.info(f"Received request for wind farm comparison: {farm_ids}")
    
    try:
        summary_file = PROCESSED_DIR / "wind_farm_comparison_summary.json"
        
        if not summary_file.exists():
            return {
                "error": "Wind farm comparison data not found",
                "suggestion": "Run analysis notebooks to generate comparison data"
            }
        
        with open(summary_file, 'r') as f:
            summary_data = json.load(f)
        
        available_farms = summary_data['metadata']['wind_farms_analyzed']
        
        # Parse farm_ids if provided
        if farm_ids:
            requested_farms = [f.strip().upper() for f in farm_ids.split(',')]
            # Normalize farm IDs
            normalized_farms = []
            for farm in requested_farms:
                if not farm.startswith('WF'):
                    farm = f'WF{farm}'
                if farm in available_farms:
                    normalized_farms.append(farm)
            
            if not normalized_farms:
                return {
                    "error": f"None of the requested farms found: {requested_farms}",
                    "available_farms": available_farms
                }
            
            compare_farms = normalized_farms
        else:
            compare_farms = available_farms
        
        # Extract comparison metrics
        performance = summary_data['performance_metrics']
        capacity_factors = summary_data['capacity_factors']
        correlations = summary_data.get('correlations', {})
        
        comparison_result = {
            "farms_compared": compare_farms,
            "comparison_metrics": {
                "capacity_factors": {farm: round(capacity_factors[farm], 4) for farm in compare_farms},
                "mean_power": {farm: round(performance['Mean Power (MW)'][farm], 4) for farm in compare_farms},
                "volatility": {farm: round(performance['Coefficient of Variation'][farm], 4) for farm in compare_farms},
                "availability": {farm: round(100 - performance['Zero Generation %'][farm], 2) for farm in compare_farms}
            },
            "rankings": {
                "best_capacity_factor": max(compare_farms, key=lambda f: capacity_factors[f]),
                "most_stable": min(compare_farms, key=lambda f: performance['Coefficient of Variation'][f]),
                "highest_availability": min(compare_farms, key=lambda f: performance['Zero Generation %'][f])
            },
            "correlations": correlations,
            "insights": summary_data['key_insights']
        }
        
        # Add diversity analysis if multiple farms
        if len(compare_farms) > 1:
            avg_correlation = sum(correlations.values()) / len(correlations) if correlations else 0
            comparison_result["portfolio_analysis"] = {
                "average_correlation": round(avg_correlation, 4),
                "diversification_benefit": avg_correlation < 0.7,
                "recommended_for_portfolio": avg_correlation < 0.7
            }
        
        logger.info(f"Successfully compared {len(compare_farms)} wind farms")
        return comparison_result
        
    except Exception as e:
        logger.error(f"Error comparing wind farms: {str(e)}")
        return {
            "error": f"Failed to compare wind farms: {str(e)}",
            "type": "processing_error"
        }


@mcp.tool()
def server_status() -> Dict[str, Any]:
    """
    Get server status and configuration information.
    
    Returns:
        Dictionary containing server status and configuration
    """
    return {
        "server_name": "Wind Farm Analytics MCP Server",
        "version": "1.0.0",
        "status": "active",
        "data_directory": str(PROCESSED_DIR),
        "available_tools": [
            "summarize_wind_farm",
            "list_available_wind_farms", 
            "compare_wind_farms",
            "server_status"
        ],
        "data_files_available": [
            f.name for f in PROCESSED_DIR.glob("*.parquet")
        ] + [
            f.name for f in PROCESSED_DIR.glob("*.json")
        ]
    }


if __name__ == "__main__":
    logger.info("Starting Wind Farm Analytics MCP Server")
    mcp.run()
