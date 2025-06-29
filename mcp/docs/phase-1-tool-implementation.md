# Phase 1 Implementation Plan: Simple MCP Tool Wrappers for Wind Power Forecasting

## Overview
This document provides detailed implementation instructions for creating 8 explicit MCP tool wrappers that internally use the existing smart routing system. These tools will provide a domain-specific API for wind power forecasting while maintaining the flexibility of the current prompt-guided approach.

## Implementation Context
- **Target File**: [`mcp/server_new.py`](mcp/server_new.py )
- **Timeline**: 1-2 days
- **Dependencies**: Existing `analyze_pattern()` function and `QueryRouter` class
- **Goal**: Create professional, discoverable MCP tools without modifying the underlying smart routing logic

## Tool Implementation Order and Details

### 1. Power Curve Analysis Tool
```python
@mcp.tool()
def analyze_power_curves(
    wind_farm: str = None,
    include_metrics: list = None
) -> Dict[str, Any]:
    """
    Analyze power curve characteristics and turbine performance.
    
    Extracts key operational parameters including cut-in speed, rated speed,
    cut-out speed, and capacity factors from wind speed-power relationships.
    
    Args:
        wind_farm: Specific farm ID (e.g., 'wf1', 'wf2') or None for all farms
        include_metrics: List of specific metrics to include. Options:
                        ['capacity_factor', 'cut_in_speed', 'rated_speed', 
                         'cut_out_speed', 'power_coefficient']
    
    Returns:
        Dictionary containing:
        - Power curve parameters for requested wind farm(s)
        - Capacity factors and efficiency metrics
        - Data quality indicators (R², scatter)
        - Relevant notebook references
    
    Example:
        >>> analyze_power_curves("wf3", ["capacity_factor", "rated_speed"])
    """
    # Build natural language query
    query_parts = ["Analyze power curves"]
    
    if wind_farm:
        # Normalize wind farm ID
        farm_id = wind_farm.lower().strip()
        if not farm_id.startswith('wf'):
            farm_id = f'wf{farm_id}'
        query_parts.append(f"for wind farm {farm_id}")
    else:
        query_parts.append("for all wind farms")
    
    if include_metrics:
        query_parts.append(f"including {', '.join(include_metrics)}")
    else:
        query_parts.append("including all standard metrics")
    
    # Route to smart system with power_curve pattern
    return analyze_pattern(" ".join(query_parts), pattern_type="power_curve")
```

### 2. Forecast Performance Evaluation Tool
```python
@mcp.tool()
def evaluate_forecast_performance(
    model_type: str = None,
    forecast_horizon: int = None,
    metric: str = "RMSE",
    wind_regime: str = None
) -> Dict[str, Any]:
    """
    Evaluate wind power forecast performance across different conditions.
    
    Assesses model accuracy using standard metrics, with breakdown by
    forecast horizon, wind conditions, and seasonal patterns.
    
    Args:
        model_type: Specific model to evaluate. Options:
                   'persistence', 'random_forest', 'xgboost', 'lstm', 'ensemble'
        forecast_horizon: Hours ahead (1-48) or None for all horizons
        metric: Performance metric. Options: 'RMSE', 'MAE', 'MAPE', 'skill_score'
        wind_regime: Filter by wind conditions. Options: 'low', 'medium', 'high'
    
    Returns:
        Dictionary containing:
        - Performance metrics for specified conditions
        - Comparison against persistence baseline
        - Horizon-dependent accuracy degradation
        - Seasonal performance variations
    
    Example:
        >>> evaluate_forecast_performance("ensemble", 24, "RMSE", "high")
    """
    # Build query with all parameters
    query_parts = ["Evaluate forecast performance"]
    
    if model_type:
        query_parts.append(f"for {model_type} model")
    
    if forecast_horizon:
        if 1 <= forecast_horizon <= 48:
            query_parts.append(f"at {forecast_horizon} hour ahead horizon")
        else:
            query_parts.append("across all horizons")
    
    query_parts.append(f"using {metric} metric")
    
    if wind_regime:
        query_parts.append(f"in {wind_regime} wind conditions")
    
    # Route to performance analysis
    return analyze_pattern(" ".join(query_parts), pattern_type="performance")
```

### 3. Temporal Pattern Assessment Tool
```python
@mcp.tool()
def assess_temporal_patterns(
    pattern_type: str = "all",
    aggregation_level: str = "hourly",
    include_seasonality: bool = True
) -> Dict[str, Any]:
    """
    Examine temporal dependencies and patterns in wind generation.
    
    Analyzes time-based patterns including diurnal cycles, seasonal variations,
    autocorrelations, and ramp events that impact forecast accuracy.
    
    Args:
        pattern_type: Type of pattern to analyze. Options:
                     'diurnal', 'seasonal', 'ramp_events', 'autocorrelation', 'all'
        aggregation_level: Time resolution. Options: 'hourly', 'daily', 'monthly'
        include_seasonality: Whether to include seasonal decomposition
    
    Returns:
        Dictionary containing:
        - Identified temporal patterns and their strength
        - Autocorrelation structure and lags
        - Ramp event statistics and timing
        - Seasonal decomposition components
    
    Example:
        >>> assess_temporal_patterns("ramp_events", "hourly", True)
    """
    # Construct temporal analysis query
    query_parts = ["Analyze temporal patterns"]
    
    if pattern_type != "all":
        query_parts.append(f"focusing on {pattern_type}")
    else:
        query_parts.append("including all temporal characteristics")
    
    query_parts.append(f"at {aggregation_level} resolution")
    
    if include_seasonality:
        query_parts.append("with seasonal decomposition")
    
    # Route to temporal analysis
    return analyze_pattern(" ".join(query_parts), pattern_type="temporal")
```

### 4. Uncertainty Quantification Tool
```python
@mcp.tool()
def quantify_uncertainty(
    confidence_level: float = 0.95,
    forecast_horizon: int = 24,
    aggregation_level: str = "portfolio"
) -> Dict[str, Any]:
    """
    Quantify prediction uncertainty and confidence intervals.
    
    Calculates prediction intervals, uncertainty bounds, and reliability
    metrics for wind power forecasts at different aggregation levels.
    
    Args:
        confidence_level: Confidence level for intervals (0.5-0.99)
        forecast_horizon: Hours ahead for uncertainty analysis (1-48)
        aggregation_level: Level of aggregation. Options:
                          'turbine', 'farm', 'portfolio'
    
    Returns:
        Dictionary containing:
        - Prediction intervals at specified confidence
        - Uncertainty growth with forecast horizon
        - Reliability diagrams and calibration metrics
        - Portfolio diversification benefits
    
    Example:
        >>> quantify_uncertainty(0.90, 12, "farm")
    """
    # Validate confidence level
    if not 0.5 <= confidence_level <= 0.99:
        confidence_level = 0.95  # Use default if invalid
    
    # Build uncertainty query
    query_parts = [
        f"Quantify forecast uncertainty at {int(confidence_level*100)}% confidence",
        f"for {forecast_horizon} hour ahead predictions",
        f"aggregated at {aggregation_level} level"
    ]
    
    # Route to uncertainty analysis
    return analyze_pattern(" ".join(query_parts), pattern_type="uncertainty")
```

### 5. Business Impact Calculator Tool
```python
@mcp.tool()
def calculate_business_impact(
    accuracy_improvement: float,
    installed_capacity_mw: float = 100,
    carbon_intensity: float = 0.5
) -> Dict[str, Any]:
    """
    Calculate business and environmental impact of forecast improvements.
    
    Quantifies the economic value and CO2 reduction potential from
    improved wind power forecast accuracy.
    
    Args:
        accuracy_improvement: Percentage improvement in forecast accuracy (0-100)
        installed_capacity_mw: Wind farm capacity in MW
        carbon_intensity: Grid carbon intensity in tons CO2/MWh
    
    Returns:
        Dictionary containing:
        - Annual economic value from improved forecasts
        - CO2 emissions reduction potential
        - Grid integration benefits
        - Required accuracy to meet sustainability targets
    
    Example:
        >>> calculate_business_impact(15.5, 250, 0.45)
    """
    # Validate inputs
    if not 0 <= accuracy_improvement <= 100:
        accuracy_improvement = max(0, min(100, accuracy_improvement))
    
    # Build business impact query
    query_parts = [
        f"Calculate business impact of {accuracy_improvement}% forecast improvement",
        f"for {installed_capacity_mw}MW wind farm",
        f"with {carbon_intensity} tons CO2/MWh grid displacement"
    ]
    
    # Route to business analysis
    return analyze_pattern(" ".join(query_parts), pattern_type="business")
```

### 6. Model Architecture Comparison Tool
```python
@mcp.tool()
def compare_model_architectures(
    models: list = None,
    comparison_criteria: list = None
) -> Dict[str, Any]:
    """
    Compare different model architectures for wind power forecasting.
    
    Evaluates trade-offs between model complexity, accuracy, and 
    computational requirements across different architectures.
    
    Args:
        models: List of models to compare. Options:
               ['persistence', 'arima', 'random_forest', 'xgboost', 
                'lstm', 'transformer', 'ensemble']
        comparison_criteria: Aspects to compare. Options:
                           ['accuracy', 'complexity', 'training_time', 
                            'inference_speed', 'interpretability']
    
    Returns:
        Dictionary containing:
        - Head-to-head model performance comparison
        - Computational resource requirements
        - Strengths/weaknesses by wind regime
        - Recommendation matrix by use case
    
    Example:
        >>> compare_model_architectures(['lstm', 'xgboost'], ['accuracy', 'speed'])
    """
    # Default models if none specified
    if not models:
        models = ['persistence', 'random_forest', 'lstm']
    
    # Default criteria if none specified
    if not comparison_criteria:
        comparison_criteria = ['accuracy', 'complexity']
    
    # Build comparison query
    query_parts = [
        f"Compare {', '.join(models)} models",
        f"based on {', '.join(comparison_criteria)}"
    ]
    
    # Route to comparison analysis
    return analyze_pattern(" ".join(query_parts), pattern_type="comparison")
```

### 7. Feature Importance Analysis Tool
```python
@mcp.tool()
def analyze_feature_importance(
    model_type: str = "ensemble",
    top_n_features: int = 10,
    by_horizon: bool = True
) -> Dict[str, Any]:
    """
    Analyze feature importance for wind power forecasting models.
    
    Identifies which input features contribute most to forecast accuracy,
    helping optimize data collection and model complexity.
    
    Args:
        model_type: Model to analyze. Options:
                   'random_forest', 'xgboost', 'ensemble'
        top_n_features: Number of top features to return
        by_horizon: Break down importance by forecast horizon
    
    Returns:
        Dictionary containing:
        - Ranked feature importance scores
        - Feature importance by forecast horizon
        - Meteorological vs temporal feature contributions
        - Recommendations for feature engineering
    
    Example:
        >>> analyze_feature_importance("xgboost", 15, True)
    """
    # Build feature analysis query
    query_parts = [
        f"Analyze feature importance for {model_type} model",
        f"showing top {top_n_features} features"
    ]
    
    if by_horizon:
        query_parts.append("broken down by forecast horizon")
    
    # Route to feature analysis
    return analyze_pattern(" ".join(query_parts), pattern_type="feature_analysis")
```

### 8. Forecast Error Diagnosis Tool
```python
@mcp.tool()
def diagnose_forecast_errors(
    error_type: str = "all",
    wind_farm: str = None,
    time_period: str = None
) -> Dict[str, Any]:
    """
    Diagnose systematic patterns in forecast errors.
    
    Identifies bias, error patterns, and root causes of forecast
    inaccuracies to guide model improvements.
    
    Args:
        error_type: Type of error analysis. Options:
                   'bias', 'variance', 'extreme_events', 'seasonal', 'all'
        wind_farm: Specific farm to analyze or None for portfolio
        time_period: Period to analyze. Options:
                    'morning', 'afternoon', 'night', 'summer', 'winter'
    
    Returns:
        Dictionary containing:
        - Error distribution statistics and patterns
        - Systematic bias identification
        - Extreme event performance analysis
        - Recommendations for model improvements
    
    Example:
        >>> diagnose_forecast_errors("extreme_events", "wf5", "winter")
    """
    # Build diagnostic query
    query_parts = ["Diagnose forecast errors"]
    
    if error_type != "all":
        query_parts.append(f"focusing on {error_type}")
    
    if wind_farm:
        farm_id = wind_farm.lower().strip()
        if not farm_id.startswith('wf'):
            farm_id = f'wf{farm_id}'
        query_parts.append(f"for {farm_id}")
    
    if time_period:
        query_parts.append(f"during {time_period} periods")
    
    # Route to error analysis
    return analyze_pattern(" ".join(query_parts), pattern_type="error_analysis")
```

## Implementation Steps

### Step 1: Backup Current Implementation
```bash
cp /workspaces/temus/mcp/server_new.py /workspaces/temus/mcp/server_new_backup.py
```

### Step 2: Add Tool Implementations
1. Open [`mcp/server_new.py`](mcp/server_new.py ) in VS Code
2. Locate the section after the `analyze_pattern` function
3. Add all 8 tool implementations in the order specified above
4. Ensure proper indentation and imports

### Step 3: Update QueryRouter Intent Patterns
Add a new intent pattern for feature analysis if missing:
```python
'feature_analysis': [
    'feature importance', 'important features', 'feature ranking',
    'variable importance', 'shap', 'permutation importance'
]
```

### Step 4: Test Each Tool
Create a test script to verify each tool:
```python
# Test script: /workspaces/temus/mcp/test_phase1_tools.py
from server_new import (
    analyze_power_curves, evaluate_forecast_performance,
    assess_temporal_patterns, quantify_uncertainty,
    calculate_business_impact, compare_model_architectures,
    analyze_feature_importance, diagnose_forecast_errors
)

# Test each tool with basic parameters
print("Testing analyze_power_curves...")
result = analyze_power_curves("wf1")
assert "analysis_guidance" in result

print("Testing evaluate_forecast_performance...")
result = evaluate_forecast_performance("ensemble", 24)
assert "analysis_guidance" in result

# Continue for all 8 tools...
```

### Step 5: Update Server Status
Modify the `server_status()` function to list all 8 new tools:
```python
"available_tools": [
    "analyze_power_curves",
    "evaluate_forecast_performance", 
    "assess_temporal_patterns",
    "quantify_uncertainty",
    "calculate_business_impact",
    "compare_model_architectures",
    "analyze_feature_importance",
    "diagnose_forecast_errors",
    # ... existing tools
]
```

## Validation Checklist

- [ ] All 8 tools implemented with proper signatures
- [ ] Each tool has comprehensive docstring with examples
- [ ] Parameter names follow Python conventions (snake_case)
- [ ] All tools route to `analyze_pattern` with appropriate pattern_type
- [ ] Natural language queries constructed logically
- [ ] No syntax errors or import issues
- [ ] Server starts successfully with new tools
- [ ] Each tool callable via MCP protocol

## Expected Outcomes

After Phase 1 implementation:
1. MCP service will expose 8 domain-specific tools
2. Each tool will have clear parameters and documentation
3. All tools will internally use smart routing for flexibility
4. No changes required to notebooks or prompts
5. Total implementation time: 4-6 hours

## Next Steps

Once Phase 1 is complete:
1. Test all tools via MCP client
2. Document any edge cases discovered
3. Prepare demonstration queries for McKinsey presentation
4. Consider Phase 2 enhancements for critical tools
5. Update [`README.md`](README.md ) with new tool descriptions

## Important Notes

- Keep all existing functions intact for backward compatibility
- Use consistent error handling patterns
- Maintain the flexible nature of smart routing
- Focus on clarity over complexity in Phase 1
- Document any assumptions made during implementation

This plan provides everything needed for successful Phase 1 implementation of the 8 MCP tools for wind power forecasting.