#!/usr/bin/env python3
"""
Wind Farm Analytics MCP Server with Automatic Prompt Selection

This server provides wind power forecasting analysis capabilities through
the Model Context Protocol (MCP). It uses a prompt-guided approach to analyze
existing Jupyter notebooks without modifying their code.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastmcp import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("windpower-mcp")

# Initialize FastMCP server
mcp = FastMCP("Wind Farm Analytics with Smart Routing")

class QueryRouter:
    """Intelligent query routing and prompt selection"""
    
    def __init__(self):
        self.intent_patterns = {
            'performance': [
                'rmse', 'mae', 'accuracy', 'performance', 'error', 'forecast quality',
                'baseline', 'model comparison', 'best model', 'worst model'
            ],
            'power_curve': [
                'power curve', 'capacity factor', 'cut-in', 'rated speed', 'wind speed',
                'turbine', 'power output', 'cut-out', 'rated power'
            ],
            'temporal': [
                'hourly', 'daily', 'seasonal', 'pattern', 'trend', 'diurnal', 'ramp',
                'time', 'temporal', 'autocorrelation', 'lag'
            ],
            'business': [
                'co2', 'carbon', 'economic', 'value', 'savings', 'cost', 'environmental',
                'sustainability', 'grid', 'penetration', 'revenue'
            ],
            'uncertainty': [
                'confidence', 'interval', 'uncertainty', 'risk', 'reliability', 'bounds',
                'prediction interval', 'quantile'
            ],
            'error_analysis': [
                'bias', 'overpredict', 'underpredict', 'error pattern', 'residual',
                'systematic', 'diagnostic'
            ],
            'comparison': [
                'compare', 'versus', 'better', 'which model', 'trade-off', 'best', 'worst',
                'rank', 'ranking'
            ],
            'data_quality': [
                'missing', 'outlier', 'quality', 'completeness', 'validation', 'clean'
            ],
            'feature_analysis': [
                'feature importance', 'important features', 'feature ranking',
                'variable importance', 'shap', 'permutation importance'
            ]
        }
        
        self.prompt_files = {
            'master_router': '00_master_router.md',
            'notebook_navigation': '01_notebook_navigation.md', 
            'power_curve_analysis': '02_power_curve_analysis.md',
            'forecast_performance': '03_forecast_performance.md',
            'business_impact': '04_business_impact.md',
            'quick_reference': '05_quick_reference.md'
        }
        
        # Load prompts at initialization
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load all prompt files"""
        prompts = {}
        prompts_dir = Path(__file__).parent / "prompts"
        
        for name, filename in self.prompt_files.items():
            file_path = prompts_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    prompts[name] = f.read()
            else:
                logger.warning(f"Prompt file not found: {file_path}")
                prompts[name] = f"# {name.title()} prompt not found"
        
        return prompts
    
    def classify_query(self, query: str) -> List[str]:
        """Classify query into one or more intent categories"""
        query_lower = query.lower()
        detected_intents = []
        
        for intent, keywords in self.intent_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_intents.append(intent)
        
        # Default to general if no specific intent
        if not detected_intents:
            detected_intents = ['general']
            
        return detected_intents
    
    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract specific entities from query"""
        entities = {}
        query_lower = query.lower()
        
        # Extract wind farm IDs
        farm_pattern = r'wf[1-7]|wind farm [1-7]'
        farms = re.findall(farm_pattern, query_lower)
        if farms:
            entities['wind_farms'] = farms
        
        # Extract time horizons
        horizon_pattern = r'(\d+)[\s-]?hours?'
        horizons = re.findall(horizon_pattern, query_lower)
        if horizons:
            entities['horizons'] = [int(h) for h in horizons]
        
        # Extract percentages
        percent_pattern = r'(\d+)%'
        percentages = re.findall(percent_pattern, query)
        if percentages:
            entities['percentages'] = [int(p) for p in percentages]
        
        # Extract model names
        model_keywords = ['persistence', 'random forest', 'xgboost', 'lstm', 'ensemble']
        models = [model for model in model_keywords if model in query_lower]
        if models:
            entities['models'] = models
        
        return entities
    
    def get_prompt_combination(self, intents: List[str], entities: Dict[str, Any]) -> str:
        """Generate combined prompts based on detected intents"""
        
        # Always start with navigation
        combined_prompt = self.prompts.get('notebook_navigation', '') + "\n\n"
        
        # Add intent-specific prompts
        for intent in intents:
            if intent == 'performance':
                combined_prompt += "## FORECAST PERFORMANCE ANALYSIS\n"
                combined_prompt += self.prompts.get('forecast_performance', '') + "\n\n"
            
            elif intent == 'power_curve':
                combined_prompt += "## POWER CURVE ANALYSIS\n"
                combined_prompt += self.prompts.get('power_curve_analysis', '') + "\n\n"
            
            elif intent == 'business':
                combined_prompt += "## BUSINESS IMPACT ANALYSIS\n"
                combined_prompt += self.prompts.get('business_impact', '') + "\n\n"
            
            elif intent == 'comparison':
                combined_prompt += "## MODEL COMPARISON ANALYSIS\n"
                combined_prompt += self.prompts.get('forecast_performance', '') + "\n\n"
            
            elif intent in ['general', 'data_quality']:
                combined_prompt += "## GENERAL ANALYSIS\n"
                combined_prompt += self.prompts.get('quick_reference', '') + "\n\n"
        
        # Add entity-specific guidance
        if entities:
            combined_prompt += "## ENTITY-SPECIFIC GUIDANCE\n"
            if entities.get('wind_farms'):
                combined_prompt += f"Focus specifically on: {', '.join(entities['wind_farms'])}\n"
            if entities.get('horizons'):
                combined_prompt += f"Analyze forecast horizons: {', '.join(map(str, entities['horizons']))} hours\n"
            if entities.get('percentages'):
                combined_prompt += f"Apply improvement percentages: {', '.join(map(str, entities['percentages']))}%\n"
            if entities.get('models'):
                combined_prompt += f"Focus on models: {', '.join(entities['models'])}\n"
            combined_prompt += "\n"
        
        # Add response template
        combined_prompt += """## RESPONSE TEMPLATE
Structure your response as:

1. **Direct Answer**: Specific metric or finding
2. **Source**: Which notebook and section
3. **Methodology**: How the result was calculated
4. **Business Context**: Why this matters for sustainability
5. **Confidence Level**: High/Medium/Low based on data quality
6. **Next Steps**: Related analyses to consider

Remember: Focus on actionable insights for the McKinsey case study presentation.
"""
        
        return combined_prompt

# Initialize router
query_router = QueryRouter()

# Internal function for pattern analysis (not decorated)
def _analyze_pattern_internal(
    query: str, 
    pattern_type: str = "general"
) -> Dict[str, Any]:
    """
    Internal pattern analysis function for use by other tools.
    
    Args:
        query: User's analysis question
        pattern_type: Type of analysis pattern (auto-detected if 'general')
    
    Returns:
        Dictionary containing analysis guidance and search recommendations
    """
    logger.info(f"Pattern analysis request: {query}")
    
    try:
        # Automatically classify the query if pattern_type is general
        if pattern_type == "general":
            intents = query_router.classify_query(query)
        else:
            intents = [pattern_type]
        
        # Extract entities from query
        entities = query_router.extract_entities(query)
        
        # Generate combined prompt guidance
        analysis_prompt = query_router.get_prompt_combination(intents, entities)
        
        # Create workflow based on intents
        workflow_steps = []
        notebook_recommendations = []
        
        if 'power_curve' in intents:
            workflow_steps.append({
                "step": 1,
                "action": "Analyze power curve characteristics",
                "notebooks": ["02_wind_physics_analysis.ipynb"],
                "look_for": ["power_curve", "capacity_factor", "cut_in_speed"],
                "extract": "Turbine operational parameters"
            })
            notebook_recommendations.extend(["02_wind_physics_analysis.ipynb"])
        
        if 'performance' in intents:
            workflow_steps.append({
                "step": len(workflow_steps) + 1,
                "action": "Evaluate forecast performance",
                "notebooks": ["10_model_evaluation.ipynb", "06_baseline_models.ipynb"],
                "look_for": ["rmse", "mae", "model_comparison"],
                "extract": "Performance metrics by model and horizon"
            })
            notebook_recommendations.extend(["10_model_evaluation.ipynb"])
        
        if 'business' in intents:
            workflow_steps.append({
                "step": len(workflow_steps) + 1,
                "action": "Calculate business impact",
                "notebooks": ["12_business_impact.ipynb"],
                "look_for": ["co2_displacement", "economic_value"],
                "extract": "Environmental and economic benefits"
            })
            notebook_recommendations.extend(["12_business_impact.ipynb"])
        
        if 'data_quality' in intents:
            workflow_steps.append({
                "step": len(workflow_steps) + 1,
                "action": "Assess data quality",
                "notebooks": ["01_data_foundation.ipynb"],
                "look_for": ["missing_values", "outliers", "data_quality"],
                "extract": "Data completeness and quality metrics"
            })
            notebook_recommendations.extend(["01_data_foundation.ipynb"])
        
        # Remove duplicates while preserving order
        notebook_recommendations = list(dict.fromkeys(notebook_recommendations))
        
        return {
            "query": query,
            "detected_intents": intents,
            "extracted_entities": entities,
            "analysis_prompt": analysis_prompt,
            "workflow_steps": workflow_steps,
            "recommended_notebooks": notebook_recommendations,
            "guidance": {
                "primary_focus": intents[0] if intents else "general",
                "notebooks_to_examine": notebook_recommendations,
                "key_patterns_to_find": _get_patterns_for_intents(intents),
                "response_structure": "Follow the template in analysis_prompt"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in pattern analysis: {str(e)}")
        return {
            "error": f"Analysis failed: {str(e)}",
            "fallback_guidance": "Please check notebooks 01_data_foundation.ipynb and 02_wind_physics_analysis.ipynb for basic analysis"
        }

# MCP Tools with intelligent routing
@mcp.tool()
def analyze_pattern(
    query: str, 
    pattern_type: str = "general"
) -> Dict[str, Any]:
    """
    Provide analysis guidance based on common wind power analysis patterns.
    
    Args:
        query: User's analysis question
        pattern_type: Type of analysis pattern (auto-detected if 'general')
    
    Returns:
        Dictionary containing analysis guidance and search recommendations
    """
    return _analyze_pattern_internal(query, pattern_type)

def _get_patterns_for_intents(intents: List[str]) -> List[str]:
    """Get code patterns to look for based on intents"""
    patterns = []
    
    if 'power_curve' in intents:
        patterns.extend(['groupby', 'capacity_factor', 'power_curve', 'cut_in_speed'])
    if 'performance' in intents:
        patterns.extend(['rmse', 'mae', 'model.evaluate', 'test_results'])
    if 'business' in intents:
        patterns.extend(['co2_displacement', 'economic_value', 'annual_generation'])
    if 'data_quality' in intents:
        patterns.extend(['missing_values', 'outliers', 'describe()', 'info()'])
    
    return list(set(patterns))  # Remove duplicates

# Phase 1: Domain-Specific MCP Tools
# These tools provide explicit APIs for wind power forecasting while internally using smart routing

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
    return _analyze_pattern_internal(" ".join(query_parts), pattern_type="power_curve")

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
    return _analyze_pattern_internal(" ".join(query_parts), pattern_type="performance")

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
    return _analyze_pattern_internal(" ".join(query_parts), pattern_type="temporal")

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
    return _analyze_pattern_internal(" ".join(query_parts), pattern_type="uncertainty")

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
    return _analyze_pattern_internal(" ".join(query_parts), pattern_type="business")

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
    return _analyze_pattern_internal(" ".join(query_parts), pattern_type="comparison")

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
    return _analyze_pattern_internal(" ".join(query_parts), pattern_type="feature_analysis")

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
    return _analyze_pattern_internal(" ".join(query_parts), pattern_type="error_analysis")

# Legacy tools for backward compatibility
@mcp.tool()
def summarize_wind_farm(farm_id: str = "wf1") -> Dict[str, Any]:
    """
    Summarize statistics for a specific wind farm from the GEF2012 dataset.
    
    Args:
        farm_id: Wind farm identifier (wf1-wf7)
        
    Returns:
        Dictionary containing wind farm statistics
    """
    # Route to pattern analysis with specific query
    query = f"What are the statistics and capacity factor for wind farm {farm_id}?"
    return _analyze_pattern_internal(query, "power_curve")

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
    if farm_ids:
        query = f"Compare capacity factors and performance for wind farms {farm_ids}"
    else:
        query = "Compare capacity factors and performance across all wind farms"
    
    return _analyze_pattern_internal(query, "comparison")

@mcp.tool()
def search_notebooks(
    query: str,
    analysis_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search notebooks for relevant analysis based on query terms.
    
    Args:
        query: Search terms to find relevant analysis
        analysis_type: Optional type hint for better search
    
    Returns:
        Dictionary containing relevant notebooks and analysis guidance
    """
    return _analyze_pattern_internal(query, analysis_type or "general")

@mcp.tool()
def list_available_wind_farms() -> Dict[str, Any]:
    """
    List all available wind farms in the GEF2012 dataset.
    
    Returns:
        Dictionary containing list of wind farm IDs and basic metadata
    """
    return {
        "wind_farms": ["wf1", "wf2", "wf3", "wf4", "wf5", "wf6", "wf7"],
        "dataset": "GEF2012 Wind Forecasting Competition",
        "period": "July 2009 - December 2010",
        "forecast_horizons": "1-48 hours",
        "guidance": {
            "notebooks_to_examine": ["01_data_foundation.ipynb", "02_wind_physics_analysis.ipynb"],
            "key_metrics": ["capacity_factor", "cut_in_speed", "rated_power", "data_quality"],
            "analysis_prompt": query_router.prompts.get('power_curve_analysis', '')
        }
    }

@mcp.tool()
def extract_notebook_results(
    notebook_path: str,
    result_type: str = "all"
) -> Dict[str, Any]:
    """
    Extract analysis results from a specific notebook.
    
    Args:
        notebook_path: Path to the notebook file (relative to notebooks directory)
        result_type: Type of results to extract ('dataframe', 'metrics', 'all')
    
    Returns:
        Dictionary containing extracted results from notebook cells
    """
    # Determine intent based on notebook path
    if "data_foundation" in notebook_path:
        intent = "data_quality"
    elif "wind_physics" in notebook_path:
        intent = "power_curve"
    elif "model_evaluation" in notebook_path:
        intent = "performance"
    elif "business_impact" in notebook_path:
        intent = "business"
    else:
        intent = "general"
    
    query = f"Extract {result_type} results from {notebook_path}"
    return _analyze_pattern_internal(query, intent)

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
        "approach": "Prompt-Guided Analysis (Approach 3)",
        "status": "operational",
        "capabilities": [
            "Automatic query intent detection",
            "Smart prompt combination",
            "Entity extraction",
            "Multi-intent handling",
            "Business context integration",
            "Domain-specific tool APIs"
        ],
        "available_tools": [
            "analyze_power_curves",
            "evaluate_forecast_performance", 
            "assess_temporal_patterns",
            "quantify_uncertainty",
            "calculate_business_impact",
            "compare_model_architectures",
            "analyze_feature_importance",
            "diagnose_forecast_errors",
            "analyze_pattern",
            "summarize_wind_farm",
            "compare_wind_farms",
            "search_notebooks",
            "list_available_wind_farms",
            "extract_notebook_results",
            "server_status"
        ],
        "supported_analyses": list(query_router.intent_patterns.keys()),
        "notebook_coverage": [
            "01_data_foundation.ipynb",
            "02_wind_physics_analysis.ipynb", 
            "03_temporal_patterns.ipynb",
            "04_spatial_analysis.ipynb",
            "05_feature_engineering.ipynb",
            "06_baseline_models.ipynb",
            "07_ml_models.ipynb",
            "08_deep_learning.ipynb",
            "09_ensemble_uncertainty.ipynb",
            "10_model_evaluation.ipynb",
            "11_mcp_service.ipynb",
            "12_business_impact.ipynb"
        ],
        "prompt_files_loaded": list(query_router.prompts.keys()),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # For testing purposes
    import uvicorn
    logger.info("Starting Wind Farm Analytics MCP Server with Smart Routing")
    mcp.run()
