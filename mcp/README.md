# Wind Farm Analytics MCP Server

This Model Context Protocol (MCP) server provides AI agents with access to wind farm analysis data from the GEF2012 (Global Energy Forecasting Competition 2012) dataset.

## Overview

The server enables LLMs to:
- Query wind farm performance statistics
- Compare multiple wind farms
- Access capacity factors and generation estimates
- Calculate environmental impact metrics (CO2 displacement)

## Available Tools

### 1. `summarize_wind_farm(farm_id)`
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

## Testing

Run validation tests:
```bash
# Test data availability
python mcp/validate_data.py

# Test function logic
python mcp/test_functions.py
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
