# Wind Farm Analytics MCP Server

This Model Context Protocol (MCP) server provides AI agents with access to wind farm analysis data from the GEF2012 (Global Energy Forecasting Competition 2012) dataset.

## Overview

The server enables LLMs to:
- Query wind farm performance statistics
- Compare multiple wind farms  
- Access capacity factors and generation estimates
- Calculate environmental impact metrics (CO2 displacement)
- **NEW**: Direct access to structured data from pre-processed parquet files
- **NEW**: Real-time data serving without notebook execution

## Architecture

The server now provides **dual access modes**:

1. **Prompt-Guided Analysis**: Smart routing to relevant notebook analyses
2. **Direct Data Access**: Fast, structured access to pre-processed results

## Available Tools

### Core Data Access

#### `get_wind_farm_data(wind_farm, data_type, include_metadata)`
**NEW**: Direct access to structured wind farm data from parquet files.

**Parameters:**
- `wind_farm`: Farm ID ("wf1", "wp2", etc.) or None for all farms
- `data_type`: "power_curve", "capacity_factors", "data_quality", "summary"  
- `include_metadata`: Boolean flag for metadata inclusion

**Returns:**
- Structured data based on data_type
- Metadata including source files and timestamps
- Data quality indicators
- ~1ms response time

**Example:**
```python
# Get power curve data for wind farm 1
result = get_wind_farm_data("wf1", "power_curve", True)

# Get capacity factors for all farms
result = get_wind_farm_data(None, "capacity_factors", False)
```

### Legacy Tools (Prompt-Guided)

#### `summarize_wind_farm(farm_id)`
Returns comprehensive statistics for a specific wind farm.

**Parameters:**
- `farm_id`: Wind farm identifier ("wf1", "WF2", "3", etc.)

**Returns:**
- Capacity factor and performance metrics
- Annual generation estimates (MWh/MW)
- CO2 displacement calculations (tons/MW)
- Data quality indicators

### 2. `list_available_wind_farms()`
Lists all available wind farms in the dataset.

**Returns:**
- Available wind farm IDs
- Performance rankings
- Dataset metadata

### 3. `compare_wind_farms(farm_ids?)`
Compares statistics across multiple wind farms.

**Parameters:**
- `farm_ids`: Optional comma-separated list (e.g., "wf1,wf2,wf3")

**Returns:**
- Comparative performance metrics
- Portfolio diversification analysis
- Correlation statistics

### 4. `server_status()`
Returns server status and configuration information.

## Data Source

Based on pre-processed analysis results from:
- **Dataset**: GEF2012 Wind Forecasting Competition
- **Period**: July 2009 - August 2011 (18,757 hourly observations)
- **Wind Farms**: WF1, WF2, WF3 (normalized power outputs)

## Installation & Setup

### Prerequisites
```bash
pip install fastmcp pandas pyarrow
```

### Configuration for VS Code
The server is configured in `.vscode/mcp.json`:

```json
{
  "servers": {
    "windFarmAnalytics": {
      "type": "stdio",
      "command": "/workspaces/temus/mcp/start_server.sh",
      "env": {
        "PYTHONPATH": "/workspaces/temus"
      }
    }
  }
}
```

### Usage from VS Code Copilot Agent

1. Open VS Code Copilot Chat
2. Switch to "Agent" mode
3. Reference the MCP server in your queries

**Example queries:**
```
Using the windFarmAnalytics MCP server, summarize statistics for wind farm wf3.

What's the capacity factor comparison between wf1 and wf2?

Show me the CO2 displacement potential for all wind farms.
```

## New Direct Data Access Features

### ParquetDataReader
Fast, direct access to 40+ pre-processed parquet files containing:
- Power curve parameters and capacity factors
- Forecast performance metrics (RMSE, MAE, skill scores)
- Temporal and spatial analysis results
- Business impact calculations
- Data quality assessments

### Performance
- **Response Time**: ~1ms average
- **Caching**: In-memory caching for frequently accessed files
- **Error Handling**: Comprehensive validation and fallback
- **Scalability**: No blocking operations, concurrent access safe

### Data Types Supported
1. **power_curve**: Cut-in/rated/cut-out speeds, capacity factors
2. **capacity_factors**: Individual and portfolio-level metrics
3. **data_quality**: Missing data, outliers, validation status
4. **summary**: Comprehensive wind farm overview

### Usage Examples
```python
# Power curve analysis for specific farm
data = get_wind_farm_data("wf1", "power_curve", True)

# Portfolio capacity factors
data = get_wind_farm_data(None, "capacity_factors", False)

# Comprehensive summary with metadata
data = get_wind_farm_data("wf3", "summary", True)
```

## Testing

Run validation tests:
```bash
# Test core functionality
python test_core.py

# Test MCP tool integration  
python test_mcp_function.py

# Full integration test
python test_data_access.py
```

## Environmental Impact Calculations

The server uses standard industry factors:
- **CO2 Displacement**: 0.5 tons CO2 per MWh generated
- **Capacity Factor**: Actual generation / Maximum possible generation
- **Annual Estimates**: Based on 8,760 hours per year

## Files Structure

```
/mcp/
├── server.py              # Main FastMCP server
├── start_server.sh        # VS Code integration script
├── requirements.txt       # Dependencies
├── validate_data.py       # Data validation tests
├── test_functions.py      # Function logic tests
└── README.md             # This file
```

## Logging

Server logs are written to `/mcp/mcp_server.log` for debugging and monitoring.

## Business Context

This MCP server supports the Temus case study by:
- Demonstrating practical ML deployment for sustainability
- Enabling real-time wind farm analysis through AI chat
- Providing quantified environmental impact metrics
- Supporting grid optimization decision-making

The server represents a "small but practical step" toward sustainability by enabling AI-assisted wind farm optimization and portfolio management.

## Next Steps

The MVP can be extended with:
- Real-time forecast evaluation tools
- Advanced correlation analysis
- Weather pattern integration
- Portfolio optimization recommendations
