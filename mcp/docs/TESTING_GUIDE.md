# Testing Wind Farm Analytics MCP Routing in VS Code Chat

## How to Test the Routing

### 1. Start the MCP Server
```bash
./start_server_new.sh
```

### 2. Connect in VS Code
- Open VS Code
- Ensure MCP extension/client is installed and configured
- The MCP server runs via stdio (not localhost:8000)
- VS Code will connect to the server automatically based on mcp.json configuration

### 3. Test Queries in Chat

**Important**: The exact syntax depends on how you access the MCP tools:

#### Option A: Direct MCP Tool Access (most likely)
VS Code chat will have access to MCP tools directly. Use natural language:

#### Option B: If there's a VS Code Participant (hypothetical)
If `@windFarmAnalytics` participant exists, use the @ syntax:

Use these specific queries to test different routing scenarios:

## Data Foundation Routing (Notebook 01)

### Direct MCP Tool Access:
```
What's the data completeness rate for wind speed measurements?
```

### With Participant (if available):
```
@windFarmAnalytics What's the data completeness rate for wind speed measurements?
```

**Expected Routing**: 
- Intent: `data_quality`
- Notebook: `01_data_foundation.ipynb`
- Should provide guidance about missing values, data quality assessment

### Direct MCP Tool Access:
```
Check for outliers in the wind speed data across all farms
```

### With Participant (if available):
```
@windFarmAnalytics Check for outliers in the wind speed data across all farms
```

**Expected Routing**:
- Intent: `data_quality` 
- Notebook: `01_data_foundation.ipynb`
- Should guide to outlier detection sections

## Wind Physics Routing (Notebook 02)
```
@windFarmAnalytics What's the capacity factor for wind farm wf3?
```
**Expected Routing**:
- Intent: `power_curve`
- Entity: `wf3`
- Notebook: `02_wind_physics_analysis.ipynb`
- Should provide power curve analysis guidance

```
@windFarmAnalytics Show me the cut-in and rated speeds for all turbines
```
**Expected Routing**:
- Intent: `power_curve`
- Notebook: `02_wind_physics_analysis.ipynb`
- Should guide to power curve parameter extraction

## Multi-Intent Routing
```
@windFarmAnalytics Compare capacity factors and check data quality for wf1 and wf3
```
**Expected Routing**:
- Intents: `power_curve`, `comparison`, `data_quality`
- Entities: `wf1`, `wf3`
- Notebooks: `01_data_foundation.ipynb`, `02_wind_physics_analysis.ipynb`
- Should provide combined analysis workflow

## Performance Analysis Routing
```
@windFarmAnalytics What's the RMSE of the best model compared to persistence baseline?
```
**Expected Routing**:
- Intent: `performance`
- Notebook: `10_model_evaluation.ipynb`
- Should guide to model comparison sections

## Business Impact Routing
```
@windFarmAnalytics What's the CO2 impact of improving forecast accuracy by 20%?
```
**Expected Routing**:
- Intents: `business`, `performance`
- Entity: `20%`
- Notebook: `12_business_impact.ipynb`
- Should provide CO2 calculation guidance

## Entity Extraction Testing
```
@windFarmAnalytics Compare Random Forest vs XGBoost performance for 24-hour forecasts
```
**Expected Routing**:
- Intent: `performance`, `comparison`
- Entities: `random forest`, `xgboost`, `24 hours`
- Should extract all entities and provide targeted guidance

## General Query Routing
```
@windFarmAnalytics Give me an overview of the wind farm analysis results
```
**Expected Routing**:
- Intent: `general`
- Notebook: Multiple (quick reference)
- Should provide general analysis guidance

## Quick VS Code Agent Test Commands

**Note**: Use the syntax that matches your VS Code MCP integration setup.

## Immediate Test Queries

### Test 1: Data Foundation (Notebook 01)
**Direct Access**:
```
What's the data completeness rate for wind speed measurements?
```

**With Participant** (if available):
```
@windFarmAnalytics What's the data completeness rate for wind speed measurements?
```
**Expected Response**: Should mention `01_data_foundation.ipynb` and provide guidance about missing values analysis.

### Test 2: Wind Physics (Notebook 02)  
**Direct Access**:
```
What's the capacity factor for wind farm wf3?
```

**With Participant** (if available):
```
@windFarmAnalytics What's the capacity factor for wind farm wf3?
```
**Expected Response**: Should mention `02_wind_physics_analysis.ipynb`, extract `wf3` entity, and provide power curve guidance.

### Test 3: Multi-Intent Routing
**Direct Access**:
```
Compare capacity factors and check data quality for wf1 and wf3
```

**With Participant** (if available):
```
@windFarmAnalytics Compare capacity factors and check data quality for wf1 and wf3
```
**Expected Response**: Should mention both notebooks 01 and 02, extract both wind farms, provide combined workflow.

### Test 4: Business Impact
**Direct Access**:
```
What's the CO2 impact of improving forecast accuracy by 20%?
```

**With Participant** (if available):
```
@windFarmAnalytics What's the CO2 impact of improving forecast accuracy by 20%?
```
**Expected Response**: Should mention `12_business_impact.ipynb`, extract `20%`, provide CO2 calculation guidance.

### Test 5: Routing Verification
**Direct Access**: (May not work with direct access)
```
Check wind farm analytics server status
```

**With Participant** (if available):
```
@windFarmAnalytics server_status
```
**Expected Response**: Should show server is operational with "Prompt-Guided Analysis (Approach 3)".

## What to Look For in Responses

### 1. Correct Intent Detection
The LLM should demonstrate it understood the query type:
- "Based on your power curve analysis request..."
- "For data quality assessment..."
- "To evaluate model performance..."

### 2. Appropriate Notebook References
Responses should mention the correct notebooks:
- "Looking at notebook 01_data_foundation.ipynb..."
- "The power curve analysis in notebook 02..."
- "Model evaluation results in notebook 10..."

### 3. Entity-Specific Guidance
For queries with entities, responses should be targeted:
- "For wind farm wf3 specifically..."
- "Focusing on 24-hour forecast horizons..."
- "Applying 20% improvement scenarios..."

### 4. Business Context Integration
Responses should include business relevance:
- "This capacity factor indicates..."
- "The CO2 impact translates to..."
- "For grid integration, this means..."

### 5. Structured Response Format
Responses should follow the template:
1. **Direct Answer**: Specific finding
2. **Source**: Notebook reference
3. **Methodology**: How calculated
4. **Business Context**: Why it matters
5. **Confidence**: Data quality note
6. **Next Steps**: Related analyses

## Debugging Routing Issues

If routing doesn't work as expected:

1. **Check Server Status**:
```
@windFarmAnalytics server_status
```

2. **Test Basic Functionality**:
```
@windFarmAnalytics list_available_wind_farms
```

3. **Check Intent Classification**:
Use simple, single-intent queries first before complex multi-intent ones

4. **Verify Entity Extraction**:
Use queries with clear entities (wf1, wf2, etc.)

## Success Indicators

✅ **Routing Working Correctly**:
- LLM mentions specific notebooks
- Provides targeted analysis guidance
- Extracts entities correctly
- Gives business-relevant context
- Follows response template

❌ **Routing Issues**:
- Generic responses without notebook references
- Incorrect notebook suggestions
- Missing entity recognition
- No business context
- Unstructured responses

## MCP Integration Patterns Explained

### How MCP Works in VS Code

The Wind Farm Analytics MCP server can be accessed in different ways depending on your VS Code setup:

#### 1. **Direct MCP Tool Access** (Most Common)
- VS Code chat directly accesses MCP tools in the background
- You ask natural language questions
- VS Code automatically calls the appropriate MCP tools
- **Example**: "What's the capacity factor for wf3?" → VS Code calls `analyze_pattern` tool

#### 2. **VS Code Participant** (If Implemented)
- A custom `@windFarmAnalytics` participant would need to be created
- This would explicitly route to the MCP server
- **Example**: "@windFarmAnalytics What's the capacity factor for wf3?"

#### 3. **MCP Client Extension**
- Direct MCP protocol client in VS Code
- Tools appear in command palette or interface
- Manual tool selection and parameter entry

### Current Implementation: Approach 3 (Prompt-Guided)

Our implementation is designed for **Pattern #1 (Direct Access)**:

1. **User asks question** in VS Code chat
2. **VS Code recognizes** it needs wind farm analysis
3. **VS Code calls** our MCP `analyze_pattern` tool
4. **Tool returns** structured guidance prompts
5. **VS Code LLM uses prompts** to analyze notebooks and respond

### Why @windFarmAnalytics in Examples?

I included `@windFarmAnalytics` syntax as a **hypothetical participant name** to:
- **Clearly identify** which queries test the routing
- **Distinguish** MCP-routed queries from general VS Code chat
- **Provide flexibility** for different integration approaches

### Actual Usage Will Likely Be:

```
# User types natural questions:
"What's the capacity factor for wind farm wf3?"

# VS Code automatically:
1. Detects this is about wind farm analysis
2. Calls analyze_pattern("What's the capacity factor for wind farm wf3?")
3. Gets routing guidance from MCP server
4. Uses guidance to analyze notebooks
5. Responds with structured answer
```

### Testing Both Patterns

In the examples below, I provide both syntaxes:
- **Direct**: Natural language questions
- **@windFarmAnalytics**: Explicit participant routing (if available)

Use whichever pattern matches your VS Code MCP integration setup.
