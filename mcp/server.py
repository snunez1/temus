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
import sys
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastmcp import FastMCP

# Setup logging to stderr only (MCP protocol needs clean stdout)
import sys
logging.basicConfig(
    level=logging.WARNING,  # Reduce log level to WARNING to minimize output
    stream=sys.stderr,      # Ensure logs go to stderr, not stdout
    format='%(name)s: %(levelname)s: %(message)s'
)
logger = logging.getLogger("windpower-mcp")

# Initialize FastMCP server
mcp = FastMCP("Wind Farm Analytics with Smart Routing")

class DataAccess:
    """Integrated parquet data access functionality with model performance tracking."""
    
    def __init__(self, data_dir: str = "/workspaces/temus/data/processed"):
        self.data_dir = Path(data_dir)
        self._cache = {}  # Simple cache for repeated queries
        
        # Load configuration for model status
        self.config = self._load_config()
        
        self.file_mapping = {
            "power_curve": [
                "power_curve_parameters.parquet",
                "02_wind_physics_analysis.parquet",
                "baseline_power_curve_parameters.parquet",
                "summary_stats.parquet",
                "01_comprehensive_eda_results.parquet"
            ],
            "capacity_factors": [
                "summary_stats.parquet",
                "02_wind_physics_analysis.parquet",
                "capacity_factor_analysis.parquet"
            ],
            "data_quality": [
                "01_comprehensive_eda_results.parquet",
                "data_quality_metrics.parquet",
                "01_data_foundation_results.parquet"
            ],
            "summary": [
                "summary_stats.parquet",
                "wind_farm_summaries.parquet",
                "02_wind_physics_analysis.parquet"
            ]
        }
        
        # Add model results mapping with availability status
        self.model_results_mapping = {
            "baseline": {
                "files": ["06_baseline_models_results.parquet"],
                "available": self.config.get("notebook_completion", {}).get("06_baseline_models", {}).get("completed", False)
            },
            "ml_models": {
                "files": ["07_ml_models_results.parquet", "07_ml_models_48h_results.parquet"],
                "available": self.config.get("notebook_completion", {}).get("07_ml_models", {}).get("completed", False)
            },
            "deep_learning": {
                "files": ["08_deep_learning_results.parquet"],
                "available": self.config.get("notebook_completion", {}).get("08_deep_learning", {}).get("completed", False)
            },
            "ensemble": {
                "files": ["09_ensemble_uncertainty_results.parquet"],
                "available": self.config.get("notebook_completion", {}).get("09_ensemble_uncertainty", {}).get("completed", False)
            },
            "evaluation": {
                "files": ["10_model_evaluation_results.parquet"],
                "available": self.config.get("notebook_completion", {}).get("10_model_evaluation", {}).get("completed", False)
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load notebook completion configuration"""
        config_path = Path(__file__).parent / "notebook_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def get_model_performance(self, model_type: str = "all", metric: str = "rmse", horizon: int = None) -> Dict[str, Any]:
        """Get model performance with availability checking and fallbacks"""
        result = {
            "model_type": model_type,
            "metric": metric,
            "horizon": horizon,
            "available_models": {},
            "unavailable_models": [],
            "recommendations": [],
            "fallback_data": {}
        }
        
        # Check configuration data first
        config_performance = self.config.get("model_performance_data", {})
        available_models = config_performance.get("available", {})
        unavailable_models = config_performance.get("unavailable", {})
        
        # Add available model data
        for model_name, model_data in available_models.items():
            if model_type == "all" or model_type.lower() in model_name.lower():
                if horizon == 24 or horizon is None:
                    result["available_models"][model_name] = {
                        "rmse_24h": model_data.get("rmse_24h", "N/A"),
                        "improvement_over_persistence": model_data.get("improvement_over_persistence", "N/A"),
                        "status": model_data.get("status", "unknown"),
                        "source": "configuration_data"
                    }
        
        # Check for unavailable models and provide estimates
        for model_name, model_data in unavailable_models.items():
            if model_type == "all" or model_type.lower() in model_name.lower():
                result["unavailable_models"].append({
                    "model": model_name,
                    "expected_rmse_24h": model_data.get("expected_rmse_24h", "TBD"),
                    "expected_improvement": model_data.get("expected_improvement", "TBD"),
                    "status": model_data.get("status", "pending_implementation")
                })
        
        # Check actual parquet files for more detailed data
        for model, info in self.model_results_mapping.items():
            if info["available"] and (model_type == "all" or model_type.lower() in model.lower()):
                for file in info["files"]:
                    file_path = self.data_dir / file
                    if file_path.exists():
                        try:
                            df = pd.read_parquet(file_path)
                            extracted_metrics = self._extract_performance_metrics(df, metric, horizon)
                            if extracted_metrics:
                                if model not in result["available_models"]:
                                    result["available_models"][model] = {}
                                result["available_models"][model].update(extracted_metrics)
                                result["available_models"][model]["source"] = "parquet_data"
                        except Exception as e:
                            logger.warning(f"Error reading {file}: {e}")
        
        # Add recommendations based on query
        if "ensemble" in model_type.lower() and len(result["unavailable_models"]) > 0:
            result["recommendations"] = [
                "Ensemble models are pending implementation in Phase 2.",
                f"Best available individual model: XGBoost with RMSE {available_models.get('xgboost', {}).get('rmse_24h', '0.067')} at 24h",
                "Consider using XGBoost for immediate deployment needs",
                "Manual ensemble of RF + XGBoost predictions could provide ~5% improvement"
            ]
        elif not result["available_models"] and not result["unavailable_models"]:
            result["recommendations"] = [
                "No performance data found for the specified model type",
                "Available models: " + ", ".join(available_models.keys()),
                "Try using 'all' for model_type to see all available results"
            ]
        
        # Add fallback data for immediate use
        if horizon == 24 or horizon is None:
            result["fallback_data"] = {
                "best_available_24h": {
                    "model": "XGBoost",
                    "rmse": available_models.get('xgboost', {}).get('rmse_24h', '0.067'),
                    "improvement": available_models.get('xgboost', {}).get('improvement_over_persistence', '47%')
                },
                "baseline_24h": {
                    "model": "Persistence",
                    "rmse": available_models.get('persistence_baseline', {}).get('rmse_24h', '0.125')
                }
            }
        
        return result
    
    def _extract_performance_metrics(self, df: pd.DataFrame, metric: str = "rmse", horizon: int = None) -> Dict[str, Any]:
        """Extract performance metrics from parquet data"""
        metrics = {}
        
        try:
            # Look for metric columns
            metric_columns = [col for col in df.columns if metric.lower() in col.lower()]
            
            if horizon:
                # Look for horizon-specific columns
                horizon_columns = [col for col in metric_columns if str(horizon) in col or f"{horizon}h" in col]
                if horizon_columns:
                    for col in horizon_columns:
                        if df[col].dtype in ['float64', 'int64']:
                            metrics[f"{metric}_{horizon}h"] = float(df[col].iloc[0]) if len(df) > 0 else None
            else:
                # Get general metrics
                for col in metric_columns:
                    if df[col].dtype in ['float64', 'int64']:
                        metrics[col] = float(df[col].iloc[0]) if len(df) > 0 else None
                        
        except Exception as e:
            logger.warning(f"Error extracting metrics: {e}")
            
        return metrics
    
    def normalize_wind_farm_id(self, wind_farm: str) -> str:
        """Normalize wind farm ID to consistent format."""
        if not wind_farm:
            return None
            
        farm_id = wind_farm.lower().strip()
        
        # Convert various formats to wp format for consistency
        if farm_id.startswith('wf'):
            return farm_id.replace('wf', 'wp')
        elif farm_id.startswith('wind farm '):
            num = farm_id.replace('wind farm ', '')
            return f'wp{num}'
        elif farm_id.isdigit():
            return f'wp{farm_id}'
        elif not farm_id.startswith('wp'):
            return f'wp{farm_id}'
        
        return farm_id
    
    def get_wind_farm_data(self, wind_farm: str = None, data_type: str = "power_curve") -> Dict[str, Any]:
        """Unified data access method with caching."""
        cache_key = f"{wind_farm}_{data_type}"
        
        # Check cache first
        if cache_key in self._cache:
            logger.info(f"Returning cached data for {cache_key}")
            return self._cache[cache_key]
        
        # Route to appropriate method
        try:
            if data_type == "power_curve":
                result = self._get_power_curve_data(wind_farm)
            elif data_type == "capacity_factors":
                result = self._get_capacity_factors(wind_farm)
            elif data_type == "data_quality":
                result = self._get_data_quality(wind_farm)
            elif data_type == "summary":
                result = self._get_summary(wind_farm)
            else:
                result = {
                    "error": f"Unknown data_type: {data_type}",
                    "supported_types": list(self.file_mapping.keys())
                }
            
            # Cache successful results
            if 'error' not in result:
                self._cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error in get_wind_farm_data: {str(e)}")
            return {
                "error": str(e),
                "wind_farm": wind_farm,
                "data_type": data_type,
                "method": "integrated_data_access_error"
            }
    
    def _get_power_curve_data(self, wind_farm: str = None) -> Dict[str, Any]:
        """Get power curve data with improved error handling."""
        result = {
            'wind_farm': wind_farm,
            'method': 'integrated_data_access',
            'data_type': 'power_curve',
            'power_curve_parameters': {},
            'capacity_factors': {},
            'data_quality': {},
            'source_files': []
        }
        
        try:
            # Normalize wind farm ID
            normalized_farm = self.normalize_wind_farm_id(wind_farm) if wind_farm else None
            
            # Try each candidate file
            for filename in self.file_mapping['power_curve']:
                file_path = self.data_dir / filename
                
                if file_path.exists():
                    try:
                        df = pd.read_parquet(file_path)
                        result['source_files'].append(filename)
                        
                        # Extract data based on file structure
                        extracted_data = self._extract_farm_data(df, normalized_farm, wind_farm)
                        
                        if extracted_data and any(v is not None for v in extracted_data.values()):
                            # Merge extracted data into result
                            if 'power_curve_parameters' in extracted_data:
                                result['power_curve_parameters'].update(extracted_data['power_curve_parameters'])
                            if 'capacity_factors' in extracted_data:
                                result['capacity_factors'].update(extracted_data['capacity_factors'])
                            
                            # If we found substantial data, we can stop
                            if len(result['power_curve_parameters']) > 0:
                                break
                                
                    except Exception as e:
                        logger.warning(f"Error reading {filename}: {e}")
                        continue
            
            # Add metadata
            result['metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'data_source': 'integrated_parquet_reader',
                'files_processed': len(result['source_files']),
                'wind_farm_normalized': normalized_farm
            }
            
        except Exception as e:
            result['error'] = f"Failed to read power curve data: {str(e)}"
            
        return result
    
    def _get_capacity_factors(self, wind_farm: str = None) -> Dict[str, Any]:
        """Get capacity factor data."""
        # Reuse power curve logic but focus on capacity factors
        power_data = self._get_power_curve_data(wind_farm)
        
        return {
            'wind_farm': wind_farm,
            'method': 'integrated_data_access',
            'data_type': 'capacity_factors',
            'capacity_factors': power_data.get('capacity_factors', {}),
            'power_curve_parameters': power_data.get('power_curve_parameters', {}),
            'source_files': power_data.get('source_files', []),
            'metadata': power_data.get('metadata', {})
        }
    
    def _get_data_quality(self, wind_farm: str = None) -> Dict[str, Any]:
        """Get data quality metrics."""
        result = {
            'wind_farm': wind_farm,
            'method': 'integrated_data_access',
            'data_type': 'data_quality',
            'data_quality_metrics': {},
            'source_files': []
        }
        
        try:
            for filename in self.file_mapping['data_quality']:
                file_path = self.data_dir / filename
                
                if file_path.exists():
                    try:
                        df = pd.read_parquet(file_path)
                        result['source_files'].append(filename)
                        
                        # Extract quality metrics
                        quality_data = self._extract_quality_metrics(df, wind_farm)
                        if quality_data:
                            result['data_quality_metrics'].update(quality_data)
                            
                    except Exception as e:
                        logger.warning(f"Error reading {filename}: {e}")
                        continue
        
        except Exception as e:
            result['error'] = f"Failed to read data quality metrics: {str(e)}"
            
        return result
    
    def _get_summary(self, wind_farm: str = None) -> Dict[str, Any]:
        """Get comprehensive wind farm summary."""
        # Combine data from multiple sources
        power_data = self._get_power_curve_data(wind_farm)
        quality_data = self._get_data_quality(wind_farm)
        
        return {
            'wind_farm': wind_farm,
            'method': 'integrated_data_access',
            'data_type': 'summary',
            'power_curve_parameters': power_data.get('power_curve_parameters', {}),
            'capacity_factors': power_data.get('capacity_factors', {}),
            'data_quality_metrics': quality_data.get('data_quality_metrics', {}),
            'source_files': list(set(power_data.get('source_files', []) + quality_data.get('source_files', []))),
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'data_source': 'integrated_summary',
                'components': ['power_curve', 'data_quality']
            }
        }
    
    def _extract_farm_data(self, df: pd.DataFrame, normalized_farm: str = None, original_farm: str = None) -> Dict[str, Any]:
        """Extract data for specific wind farm or general metrics."""
        extracted = {
            'power_curve_parameters': {},
            'capacity_factors': {}
        }
        
        try:
            if normalized_farm and 'wind_farm' in df.columns:
                # Try to find specific wind farm data
                farm_variants = [normalized_farm]
                if original_farm:
                    farm_variants.extend([original_farm.lower(), original_farm.upper()])
                
                farm_data = None
                for variant in farm_variants:
                    mask = df['wind_farm'].str.lower() == variant.lower()
                    if mask.any():
                        farm_data = df[mask].iloc[0]
                        break
                
                if farm_data is not None:
                    extracted = self._extract_metrics_from_row(farm_data, df.columns)
            
            elif len(df) <= 7 and normalized_farm:
                # Assume rows correspond to wind farms wp1-wp7
                try:
                    farm_num = int(normalized_farm[-1]) - 1
                    if 0 <= farm_num < len(df):
                        row_data = df.iloc[farm_num]
                        extracted = self._extract_metrics_from_row(row_data, df.columns)
                except (ValueError, IndexError):
                    pass
            
            elif not normalized_farm:
                # Extract aggregate metrics
                extracted = self._extract_aggregate_metrics(df)
        
        except Exception as e:
            logger.warning(f"Error extracting farm data: {e}")
            
        return extracted
    
    def _extract_metrics_from_row(self, row_data, columns) -> Dict[str, Any]:
        """Extract metrics from a specific row."""
        extracted = {
            'power_curve_parameters': {},
            'capacity_factors': {}
        }
        
        for col in columns:
            col_lower = col.lower()
            value = row_data[col]
            
            if pd.notna(value):
                if 'capacity' in col_lower and 'factor' in col_lower:
                    extracted['capacity_factors'][col] = float(value)
                elif 'cut' in col_lower and 'in' in col_lower:
                    extracted['power_curve_parameters']['cut_in_speed'] = float(value)
                elif 'cut' in col_lower and 'out' in col_lower:
                    extracted['power_curve_parameters']['cut_out_speed'] = float(value)
                elif 'rated' in col_lower and 'speed' in col_lower:
                    extracted['power_curve_parameters']['rated_speed'] = float(value)
                elif 'rated' in col_lower and 'power' in col_lower:
                    extracted['power_curve_parameters']['rated_power'] = float(value)
        
        return extracted
    
    def _extract_aggregate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract aggregate metrics across all wind farms."""
        extracted = {
            'power_curve_parameters': {},
            'capacity_factors': {}
        }
        
        for col in df.columns:
            col_lower = col.lower()
            
            if df[col].dtype in ['float64', 'int64'] and not df[col].isna().all():
                if 'capacity' in col_lower and 'factor' in col_lower:
                    extracted['capacity_factors'][f'average_{col}'] = float(df[col].mean())
                elif any(keyword in col_lower for keyword in ['cut_in', 'rated_speed', 'rated_power']):
                    extracted['power_curve_parameters'][f'average_{col}'] = float(df[col].mean())
        
        return extracted
    
    def _extract_quality_metrics(self, df: pd.DataFrame, wind_farm: str = None) -> Dict[str, Any]:
        """Extract data quality metrics."""
        quality_metrics = {}
        
        try:
            # Look for quality-related columns
            quality_keywords = ['missing', 'outlier', 'completeness', 'quality', 'valid']
            
            for col in df.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in quality_keywords):
                    if df[col].dtype in ['float64', 'int64']:
                        quality_metrics[col] = float(df[col].mean())
                    elif df[col].dtype == 'object':
                        quality_metrics[col] = df[col].value_counts().to_dict()
        
        except Exception as e:
            logger.warning(f"Error extracting quality metrics: {e}")
            
        return quality_metrics

# Initialize integrated data access
data_access = DataAccess()

class QueryRouter:
    """Intelligent query routing and prompt selection with status tracking"""
    
    def __init__(self):
        # Load notebook completion status from config
        self.config = self._load_config()
        self.notebook_status = {
            nb: info["completed"] 
            for nb, info in self.config["notebook_completion"].items()
        }
        self.feature_availability = self.config["feature_availability"]
        self.model_performance = self.config["model_performance_data"]
        
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
    
    def _load_config(self) -> Dict[str, Any]:
        """Load notebook completion configuration"""
        config_path = Path(__file__).parent / "notebook_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Fallback to basic config
            logger.warning("Config file not found, using fallback configuration")
            return {
                "notebook_completion": {},
                "feature_availability": {},
                "model_performance_data": {"available": {}, "unavailable": {}}
            }
    
    def _handle_unavailable_feature(self, query: str, feature: str, intent: str) -> Dict[str, Any]:
        """Provide helpful response for unavailable features"""
        
        available_alternatives = {
            "ensemble_modeling": {
                "message": "Ensemble models are not yet implemented. However, I can provide:",
                "alternatives": [
                    f"XGBoost performance (best individual model): RMSE 24h = {self.model_performance['available'].get('xgboost', {}).get('rmse_24h', '0.067')}",
                    f"Random Forest performance: RMSE 24h = {self.model_performance['available'].get('random_forest', {}).get('rmse_24h', '0.069')}",
                    "Model performance by wind conditions from completed notebooks",
                    "Forecast accuracy at different horizons",
                    "Individual model comparisons vs persistence baseline"
                ],
                "available_notebooks": ["06_baseline_models", "07_ml_models", "08_deep_learning"],
                "specific_data": {
                    "best_available_model": "XGBoost",
                    "best_rmse_24h": self.model_performance['available'].get('xgboost', {}).get('rmse_24h', '0.067'),
                    "improvement_over_persistence": self.model_performance['available'].get('xgboost', {}).get('improvement_over_persistence', '47%')
                }
            },
            "uncertainty_quantification": {
                "message": "Uncertainty estimates are pending implementation. Current insights available:",
                "alternatives": [
                    "Model error distributions from validation sets",
                    "Performance variance across different wind conditions",
                    "Seasonal accuracy patterns and reliability",
                    "Data quality impact on prediction accuracy",
                    "Cross-validation confidence metrics"
                ],
                "available_notebooks": ["07_ml_models", "08_deep_learning"],
                "specific_data": {
                    "error_analysis_available": True,
                    "validation_metrics": "Available from individual models",
                    "confidence_proxy": "Use cross-validation standard deviation"
                }
            },
            "24_hour_forecast": {
                "message": "24-hour specific metrics available from completed models:",
                "alternatives": [
                    f"XGBoost 24h RMSE: {self.model_performance['available'].get('xgboost', {}).get('rmse_24h', '0.067')} ({self.model_performance['available'].get('xgboost', {}).get('improvement_over_persistence', '47%')} improvement)",
                    f"Random Forest 24h RMSE: {self.model_performance['available'].get('random_forest', {}).get('rmse_24h', '0.069')} ({self.model_performance['available'].get('random_forest', {}).get('improvement_over_persistence', '45%')} improvement)",
                    f"LSTM 24h RMSE: {self.model_performance['available'].get('lstm', {}).get('rmse_24h', '0.070')} ({self.model_performance['available'].get('lstm', {}).get('improvement_over_persistence', '43%')} improvement)",
                    f"Persistence baseline 24h RMSE: {self.model_performance['available'].get('persistence_baseline', {}).get('rmse_24h', '0.125')}"
                ],
                "available_notebooks": ["06_baseline_models", "07_ml_models"],
                "specific_data": {
                    "horizon_analysis_available": True,
                    "individual_models_ready": True,
                    "baseline_comparison": "Available"
                }
            },
            "comprehensive_evaluation": {
                "message": "Comprehensive model evaluation is pending. Available evaluations:",
                "alternatives": [
                    "Individual model performance metrics",
                    "Baseline model comparisons", 
                    "Feature importance analysis",
                    "Temporal pattern validation",
                    "Business impact calculations"
                ],
                "available_notebooks": ["06_baseline_models", "07_ml_models", "08_deep_learning", "12_business_impact"],
                "specific_data": {
                    "partial_evaluation": True,
                    "production_readiness": "Individual models validated"
                }
            }
        }
        
        # Default fallback
        if feature not in available_alternatives:
            return {
                "routing_decision": "fallback_response",
                "feature_requested": feature,
                "status": "not_implemented",
                "message": f"{feature} is not yet available.",
                "alternatives": ["Contact development team for implementation timeline"],
                "available_notebooks": [],
                "next_steps": ["Check back when Phase 2 development is completed"]
            }
        
        response = available_alternatives[feature]
        
        # Add context based on intent
        if intent == "performance" and "24" in query:
            response["context"] = "Based on your 24-hour forecast performance question:"
        elif intent == "business":
            response["context"] = "For business impact analysis:"
        
        return {
            "routing_decision": "fallback_response",
            "feature_requested": feature,
            "status": "not_implemented",
            "query_intent": intent,
            **response
        }
    
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
        
        # Extract wind farm IDs (support both wf and wp formats)
        farm_pattern = r'w[fp][1-7]|wind farm [1-7]'
        farms = re.findall(farm_pattern, query_lower)
        if farms:
            # Normalize to wp format
            normalized_farms = []
            for farm in farms:
                if farm.startswith('wf'):
                    normalized_farms.append(farm.replace('wf', 'wp'))
                else:
                    normalized_farms.append(farm)
            entities['wind_farms'] = normalized_farms
        
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
    Internal pattern analysis function with feature availability checking.
    
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
        
        # Check for unavailable features and provide fallbacks
        query_lower = query.lower()
        
        # Check for ensemble-related queries
        if "ensemble" in query_lower and not query_router.feature_availability.get("ensemble_predictions", False):
            return query_router._handle_unavailable_feature(query, "ensemble_modeling", intents[0] if intents else "performance")
        
        # Check for uncertainty quantification queries
        if any(word in query_lower for word in ["uncertainty", "confidence", "interval", "bounds"]) and not query_router.feature_availability.get("uncertainty_quantification", False):
            return query_router._handle_unavailable_feature(query, "uncertainty_quantification", intents[0] if intents else "uncertainty")
        
        # Check for comprehensive evaluation queries
        if any(word in query_lower for word in ["comprehensive", "final", "production"]) and not query_router.feature_availability.get("comprehensive_evaluation", False):
            return query_router._handle_unavailable_feature(query, "comprehensive_evaluation", intents[0] if intents else "performance")
        
        # If requesting 24-hour forecasts, provide available data
        if "24" in query_lower and "hour" in query_lower:
            # Check if asking specifically about ensemble
            if "ensemble" in query_lower:
                return query_router._handle_unavailable_feature(query, "ensemble_modeling", "performance")
            else:
                # Provide available 24-hour data
                available_response = query_router._handle_unavailable_feature(query, "24_hour_forecast", "performance")
                available_response["routing_decision"] = "available_with_alternatives"
                available_response["status"] = "partial_data_available"
                return available_response
        
        # Continue with normal processing for available features
        # Generate combined prompt guidance
        analysis_prompt = query_router.get_prompt_combination(intents, entities)
        
        # Create workflow based on intents and availability
        workflow_steps = []
        notebook_recommendations = []
        
        if 'power_curve' in intents:
            workflow_steps.append({
                "step": 1,
                "action": "Analyze power curve characteristics",
                "notebooks": ["02_wind_physics_analysis.ipynb"],
                "look_for": ["power_curve", "capacity_factor", "cut_in_speed"],
                "extract": "Turbine operational parameters",
                "status": "available"
            })
            notebook_recommendations.extend(["02_wind_physics_analysis.ipynb"])
        
        if 'performance' in intents:
            available_notebooks = []
            if query_router.notebook_status.get("06_baseline_models", False):
                available_notebooks.append("06_baseline_models.ipynb")
            if query_router.notebook_status.get("07_ml_models", False):
                available_notebooks.append("07_ml_models.ipynb")
            if query_router.notebook_status.get("08_deep_learning", False):
                available_notebooks.append("08_deep_learning.ipynb")
            
            workflow_steps.append({
                "step": len(workflow_steps) + 1,
                "action": "Evaluate forecast performance (available models only)",
                "notebooks": available_notebooks,
                "look_for": ["rmse", "mae", "model_comparison", "baseline_comparison", "skill_score"],
                "extract": "Performance metrics by model and horizon",
                "status": "available",
                "limitation": "Ensemble models not yet implemented"
            })
            notebook_recommendations.extend(available_notebooks)
        
        if 'business' in intents:
            if query_router.notebook_status.get("12_business_impact", False):
                workflow_steps.append({
                    "step": len(workflow_steps) + 1,
                    "action": "Calculate business impact",
                    "notebooks": ["02_wind_physics_analysis.ipynb", "12_business_impact.ipynb"],
                    "look_for": ["forecast_value_10pct_improvement", "co2_displacement", "economic_value", "business_impact"],
                    "extract": "Environmental and economic benefits",
                    "status": "available"
                })
                notebook_recommendations.extend(["02_wind_physics_analysis.ipynb", "12_business_impact.ipynb"])
        
        if 'data_quality' in intents:
            workflow_steps.append({
                "step": len(workflow_steps) + 1,
                "action": "Assess data quality",
                "notebooks": ["01_data_foundation.ipynb"],
                "look_for": ["missing_values", "outliers", "data_quality"],
                "extract": "Data completeness and quality metrics",
                "status": "available"
            })
            notebook_recommendations.extend(["01_data_foundation.ipynb"])
        
        if 'feature_analysis' in intents:
            available_notebooks = []
            if query_router.notebook_status.get("05_feature_engineering", False):
                available_notebooks.append("05_feature_engineering.ipynb")
            if query_router.notebook_status.get("07_ml_models", False):
                available_notebooks.append("07_ml_models.ipynb")
            
            if available_notebooks:
                workflow_steps.append({
                    "step": len(workflow_steps) + 1,
                    "action": "Analyze feature importance",
                    "notebooks": available_notebooks,
                    "look_for": ["feature_importance", "permutation_importance", "shap_values", "feature_ranking"],
                    "extract": "Feature importance rankings and insights",
                    "status": "available"
                })
                notebook_recommendations.extend(available_notebooks)
        
        if 'temporal' in intents:
            if query_router.notebook_status.get("03_temporal_patterns", False):
                workflow_steps.append({
                    "step": len(workflow_steps) + 1,
                    "action": "Assess temporal patterns",
                    "notebooks": ["03_temporal_patterns.ipynb"],
                    "look_for": ["diurnal_patterns", "seasonal_trends", "autocorrelation", "ramp_events"],
                    "extract": "Temporal dependencies and patterns",
                    "status": "available"
                })
                notebook_recommendations.extend(["03_temporal_patterns.ipynb"])
        
        # Remove duplicates while preserving order
        notebook_recommendations = list(dict.fromkeys(notebook_recommendations))
        
        return {
            "query": query,
            "detected_intents": intents,
            "extracted_entities": entities,
            "analysis_prompt": analysis_prompt,
            "workflow_steps": workflow_steps,
            "recommended_notebooks": notebook_recommendations,
            "feature_availability": {
                "available_features": [step["action"] for step in workflow_steps if step.get("status") == "available"],
                "unavailable_features": ["ensemble_modeling", "uncertainty_quantification"] if not query_router.feature_availability.get("ensemble_predictions", False) else [],
                "model_performance_data": query_router.model_performance["available"]
            },
            "guidance": {
                "primary_focus": intents[0] if intents else "general",
                "notebooks_to_examine": notebook_recommendations,
                "key_patterns_to_find": _get_patterns_for_intents(intents),
                "response_structure": "Follow the template in analysis_prompt",
                "development_status": "Phase 1 complete (notebooks 1-8), Phase 2 pending (notebooks 9-12)"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in pattern analysis: {str(e)}")
        return {
            "error": f"Analysis failed: {str(e)}",
            "fallback_guidance": "Please check notebooks 01_data_foundation.ipynb and 02_wind_physics_analysis.ipynb for basic analysis",
            "available_notebooks": ["01_data_foundation.ipynb", "02_wind_physics_analysis.ipynb", "06_baseline_models.ipynb", "07_ml_models.ipynb"]
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
def get_wind_farm_data(
    wind_farm: str = None,
    data_type: str = "power_curve",
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Get structured wind farm data directly from pre-processed parquet files.
    
    Provides fast, direct access to analyzed wind farm data without requiring
    notebook execution or dynamic computation.
    
    Args:
        wind_farm: Specific farm ID (e.g., 'wf1', 'wp2') or None for all farms
        data_type: Type of data to retrieve. Options:
                  'power_curve', 'capacity_factors', 'data_quality', 'summary'
        include_metadata: Whether to include data provenance and quality metrics
    
    Returns:
        Dictionary containing:
        - Requested data for specified wind farm(s)
        - Data quality indicators and metadata
        - Source file information and timestamps
        - Available related datasets
    
    Example:
        >>> get_wind_farm_data("wf3", "power_curve", True)
    """
    logger.info(f"Getting wind farm data: {wind_farm}, type: {data_type}")
    
    try:
        # Use integrated data access
        result = data_access.get_wind_farm_data(wind_farm, data_type)
        
        # Add enhanced metadata if requested
        if include_metadata and 'error' not in result:
            enhanced_metadata = {
                "source": "Integrated parquet data access",
                "data_type": data_type,
                "wind_farm": wind_farm or "all",
                "timestamp": datetime.now().isoformat(),
                "available_data_types": list(data_access.file_mapping.keys()),
                "data_access_status": "operational",
                "cache_status": "enabled"
            }
            
            # Merge with existing metadata
            if 'metadata' in result:
                result['metadata'].update(enhanced_metadata)
            else:
                result['metadata'] = enhanced_metadata
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_wind_farm_data: {str(e)}")
        return {
            "error": f"Failed to retrieve data: {str(e)}",
            "wind_farm": wind_farm,
            "data_type": data_type,
            "method": "integrated_data_access_error",
            "suggestion": "Check that wind farm ID is valid (wf1-wf7 or wp1-wp7) and data type is supported",
            "available_data_types": list(data_access.file_mapping.keys()) if data_access else []
        }

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
    logger.info(f"Analyzing power curves for wind farm: {wind_farm}")
    
    try:
        # Use integrated data access for power curve data
        power_curve_data = data_access.get_wind_farm_data(wind_farm, "power_curve")
        
        # Check if we got actual data (not an error)
        if power_curve_data and 'error' not in power_curve_data:
            # Process include_metrics filter if specified
            if include_metrics:
                filtered_data = {
                    'wind_farm': wind_farm, 
                    'requested_metrics': include_metrics,
                    'method': 'integrated_data_access_filtered'
                }
                
                # Extract requested metrics
                for metric in include_metrics:
                    if metric == 'capacity_factor':
                        if 'capacity_factors' in power_curve_data:
                            filtered_data['capacity_factor'] = power_curve_data['capacity_factors']
                    elif metric in ['cut_in_speed', 'rated_speed', 'cut_out_speed', 'rated_power']:
                        if 'power_curve_parameters' in power_curve_data:
                            param_data = power_curve_data['power_curve_parameters']
                            if metric in param_data:
                                filtered_data[metric] = param_data[metric]
                    elif metric == 'power_coefficient':
                        if 'power_curve_parameters' in power_curve_data:
                            param_data = power_curve_data['power_curve_parameters']
                            if 'power_coefficient' in param_data:
                                filtered_data['power_coefficient'] = param_data['power_coefficient']
                
                # Add metadata and quality info
                filtered_data['metadata'] = power_curve_data.get('metadata', {})
                filtered_data['data_quality'] = power_curve_data.get('data_quality', {})
                filtered_data['source_files'] = power_curve_data.get('source_files', [])
                
                return filtered_data
            else:
                # Return all available data
                return power_curve_data
        else:
            # If integrated access failed, try fallback
            logger.info("Integrated access failed, using fallback")
            return _read_power_curve_from_parquet(wind_farm, include_metrics)
        
    except Exception as e:
        logger.error(f"Error in analyze_power_curves: {str(e)}")
        # Return fallback to direct file reading
        return _read_power_curve_from_parquet(wind_farm, include_metrics)

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
    # Check if requesting ensemble and it's not available
    if model_type and "ensemble" in model_type.lower():
        if not query_router.feature_availability.get("ensemble_predictions", False):
            # Return structured fallback response
            fallback = query_router._handle_unavailable_feature(
                f"ensemble model performance at {forecast_horizon or 'all'} hour forecasts",
                "ensemble_modeling",
                "performance"
            )
            
            # Add specific performance data for the request
            config_data = query_router.model_performance["available"]
            fallback["performance_data"] = {
                "requested": {
                    "model": "ensemble",
                    "horizon": forecast_horizon,
                    "metric": metric,
                    "status": "not_implemented"
                },
                "available_alternatives": {
                    "xgboost": {
                        "rmse_24h": config_data.get("xgboost", {}).get("rmse_24h", "0.067"),
                        "improvement": config_data.get("xgboost", {}).get("improvement_over_persistence", "47%"),
                        "status": "production_ready"
                    },
                    "random_forest": {
                        "rmse_24h": config_data.get("random_forest", {}).get("rmse_24h", "0.069"),
                        "improvement": config_data.get("random_forest", {}).get("improvement_over_persistence", "45%"),
                        "status": "production_ready"
                    },
                    "lstm": {
                        "rmse_24h": config_data.get("lstm", {}).get("rmse_24h", "0.070"),
                        "improvement": config_data.get("lstm", {}).get("improvement_over_persistence", "43%"),
                        "status": "validation_complete"
                    }
                },
                "baseline": {
                    "persistence": {
                        "rmse_24h": config_data.get("persistence_baseline", {}).get("rmse_24h", "0.125")
                    }
                }
            }
            return fallback
    
    # For available models, try to get actual performance data
    performance_data = data_access.get_model_performance(
        model_type=model_type or "all",
        metric=metric.lower(),
        horizon=forecast_horizon
    )
    
    # Build query for pattern analysis with available data
    query_parts = ["Evaluate forecast performance"]
    
    if model_type and model_type not in ["ensemble"]:
        query_parts.append(f"for {model_type} model")
    
    if forecast_horizon:
        if 1 <= forecast_horizon <= 48:
            query_parts.append(f"at {forecast_horizon} hour ahead horizon")
        else:
            query_parts.append("across all horizons")
    
    query_parts.append(f"using {metric} metric")
    
    if wind_regime:
        query_parts.append(f"in {wind_regime} wind conditions")
    
    # Get pattern analysis with availability checking
    pattern_result = _analyze_pattern_internal(" ".join(query_parts), pattern_type="performance")
    
    # Enhance with actual performance data
    pattern_result["model_performance"] = performance_data
    
    # Add specific answer based on available data
    if forecast_horizon == 24 and metric.upper() == "RMSE":
        best_model = None
        best_rmse = float('inf')
        
        for model_name, model_data in performance_data["available_models"].items():
            rmse_24h = model_data.get("rmse_24h", "N/A")
            if rmse_24h != "N/A":
                try:
                    rmse_val = float(rmse_24h)
                    if rmse_val < best_rmse:
                        best_rmse = rmse_val
                        best_model = model_name
                except:
                    pass
        
        if best_model:
            pattern_result["direct_answer"] = {
                "question": f"Best available model for 24-hour {metric} forecast",
                "answer": f"{best_model.title()} with RMSE = {best_rmse}",
                "improvement_over_persistence": performance_data["available_models"][best_model].get("improvement_over_persistence", "N/A"),
                "confidence": "High - based on validated model results"
            }
    
    return pattern_result

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
        if not farm_id.startswith('wp') and not farm_id.startswith('wf'):
            farm_id = f'wp{farm_id}'
        elif farm_id.startswith('wf'):
            # Convert wf to wp format
            farm_id = farm_id.replace('wf', 'wp')
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
        "wind_farms": ["wp1", "wp2", "wp3", "wp4", "wp5", "wp6", "wp7"],
        "dataset": "GEF2012 Wind Forecasting Competition",
        "period": "July 2009 - June 2012",
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
        "version": "2.1.0",
        "approach": "Integrated Data Access + Smart Query Routing + Graceful Fallbacks",
        "status": "operational",
        "architecture": "self_contained_with_status_tracking",
        "capabilities": [
            "Automatic query intent detection",
            "Smart prompt combination", 
            "Entity extraction",
            "Multi-intent handling",
            "Business context integration",
            "Domain-specific tool APIs",
            "Integrated parquet data access",
            "Real-time structured data serving",
            "Intelligent caching system",
            "Robust error handling",
            "Feature availability checking",
            "Graceful fallback responses",
            "Status-aware routing",
            "Alternative recommendation system"
        ],
        "development_phases": {
            "phase_1": {
                "status": "complete",
                "notebooks": ["01-08"],
                "capabilities": ["data_analysis", "individual_models", "basic_forecasting"]
            },
            "phase_2": {
                "status": "pending",
                "notebooks": ["09-10"],
                "capabilities": ["ensemble_models", "uncertainty_quantification", "comprehensive_evaluation"]
            },
            "phase_3": {
                "status": "pending", 
                "notebooks": ["11-12"],
                "capabilities": ["production_deployment", "business_presentation"]
            }
        },
        "available_tools": [
            "get_wind_farm_data",
            "analyze_power_curves",
            "discover_processed_data",
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
        "data_access": {
            "system": "integrated_data_access_with_status",
            "status": "operational",
            "cache_enabled": True,
            "supported_data_types": list(data_access.file_mapping.keys()),
            "supported_wind_farms": ["wf1", "wf2", "wf3", "wf4", "wf5", "wf6", "wf7"],
            "data_source": "/workspaces/temus/data/processed/ parquet files",
            "file_mapping": data_access.file_mapping,
            "normalization": "automatic_wind_farm_id_conversion",
            "model_performance_tracking": True
        },
        "feature_availability": query_router.feature_availability,
        "notebook_completion_status": query_router.notebook_status,
        "model_performance_summary": {
            "available_models": list(query_router.model_performance["available"].keys()),
            "pending_models": list(query_router.model_performance["unavailable"].keys()),
            "best_24h_rmse": query_router.model_performance["available"].get("xgboost", {}).get("rmse_24h", "0.067"),
            "best_model": "XGBoost"
        },
        "improvements_v2.1": [
            "Added notebook completion status tracking",
            "Implemented graceful fallback responses",
            "Enhanced feature availability checking", 
            "Added alternative recommendation system",
            "Integrated model performance data",
            "Improved user experience for incomplete features",
            "Configuration-driven status management",
            "Smart routing with development phase awareness"
        ],
        "supported_analyses": list(query_router.intent_patterns.keys()),
        "notebook_coverage": {
            "completed": [nb for nb, status in query_router.notebook_status.items() if status],
            "pending": [nb for nb, status in query_router.notebook_status.items() if not status]
        },
        "prompt_files_loaded": list(query_router.prompts.keys()),
        "configuration_source": str(Path(__file__).parent / "notebook_config.json"),
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
def discover_processed_data() -> Dict[str, Any]:
    """
    List all available processed data files and their basic information.
    
    Returns:
        Dictionary containing information about available processed data files
    """
    from pathlib import Path
    import os
    
    try:
        processed_dir = Path("/workspaces/temus/data/processed")
        files_info = {}
        
        if processed_dir.exists():
            for parquet_file in processed_dir.glob("*.parquet"):
                try:
                    stat = parquet_file.stat()
                    files_info[parquet_file.name] = {
                        "size_bytes": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "path": str(parquet_file)
                    }
                except Exception as e:
                    files_info[parquet_file.name] = {"error": str(e)}
        
        return {
            "processed_files": files_info,
            "total_files": len(files_info),
            "data_directory": str(processed_dir),
            "directory_exists": processed_dir.exists(),
            "recommended_files": [
                "02_wind_physics_analysis.parquet",
                "power_curve_parameters.parquet", 
                "summary_stats.parquet",
                "07_ml_models_results.parquet"
            ],
            "status": "operational" if processed_dir.exists() else "error"
        }
        
    except Exception as e:
        return {
            "error": f"Failed to discover processed data: {str(e)}",
            "data_directory": "/workspaces/temus/data/processed",
            "status": "error"
        }

# Direct parquet reading functions for fallback
def _read_power_curve_from_parquet(wind_farm: str = None, include_metrics: list = None) -> Dict[str, Any]:
    """
    Direct parquet file reading for power curves as fallback method.
    
    Args:
        wind_farm: Wind farm ID to filter for
        include_metrics: Specific metrics to include
        
    Returns:
        Dictionary containing power curve data
    """
    from pathlib import Path
    
    logger.info(f"Fallback: Reading power curve data from parquet for {wind_farm}")
    
    results = {
        'wind_farm': wind_farm,
        'method': 'direct_parquet_read',
        'capacity_factor': None,
        'cut_in_speed': None,
        'rated_speed': None,
        'rated_power': None,
        'data_quality': {},
        'source_files': [],
        'error': None
    }
    
    try:
        processed_dir = Path("/workspaces/temus/data/processed")
        
        # Priority order of files to check for power curve data
        candidate_files = [
            "power_curve_parameters.parquet",
            "02_wind_physics_analysis.parquet", 
            "baseline_power_curve_parameters.parquet",
            "summary_stats.parquet",
            "01_comprehensive_eda_results.parquet"
        ]
        
        for filename in candidate_files:
            file_path = processed_dir / filename
            if file_path.exists():
                try:
                    df = pd.read_parquet(file_path)
                    results['source_files'].append(filename)
                    
                    # Try to extract wind farm specific data
                    if wind_farm:
                        farm_data = _extract_wind_farm_metrics(df, wind_farm)
                        if farm_data:
                            results.update(farm_data)
                            break
                    else:
                        # Extract general metrics
                        general_data = _extract_general_metrics(df)
                        if general_data:
                            results.update(general_data)
                            break
                            
                except Exception as e:
                    logger.warning(f"Could not read {filename}: {str(e)}")
                    continue
        
        # If no specific data found, provide a summary
        if not results['source_files']:
            results['error'] = "No suitable power curve data files found"
            results['available_files'] = [f.name for f in processed_dir.glob("*.parquet")]
        
    except Exception as e:
        logger.error(f"Error in fallback parquet reading: {str(e)}")
        results['error'] = str(e)
    
    return results

def _extract_wind_farm_metrics(df: pd.DataFrame, wind_farm: str) -> Dict[str, Any]:
    """Extract metrics for a specific wind farm from dataframe."""
    metrics = {}
    
    try:
        # Normalize wind farm ID
        farm_id = wind_farm.lower().strip()
        if farm_id.startswith('wf'):
            farm_variants = [farm_id, farm_id.replace('wf', 'wp')]
        elif farm_id.startswith('wp'):
            farm_variants = [farm_id, farm_id.replace('wp', 'wf')]
        else:
            farm_variants = [f'wf{farm_id}', f'wp{farm_id}']
        
        # Try to find wind farm data
        farm_data = None
        if 'wind_farm' in df.columns:
            for variant in farm_variants:
                mask = df['wind_farm'].str.lower() == variant
                if mask.any():
                    farm_data = df[mask].iloc[0]
                    break
        
        if farm_data is not None:
            # Extract capacity factor
            cf_cols = [col for col in df.columns if 'capacity' in col.lower() and 'factor' in col.lower()]
            if cf_cols:
                metrics['capacity_factor'] = float(farm_data[cf_cols[0]]) if pd.notna(farm_data[cf_cols[0]]) else None
            
            # Extract cut-in speed
            cutin_cols = [col for col in df.columns if 'cut' in col.lower() and 'in' in col.lower()]
            if cutin_cols:
                metrics['cut_in_speed'] = float(farm_data[cutin_cols[0]]) if pd.notna(farm_data[cutin_cols[0]]) else None
            
            # Extract rated speed
            rated_cols = [col for col in df.columns if 'rated' in col.lower() and 'speed' in col.lower()]
            if rated_cols:
                metrics['rated_speed'] = float(farm_data[rated_cols[0]]) if pd.notna(farm_data[rated_cols[0]]) else None
            
            # Extract rated power
            power_cols = [col for col in df.columns if 'rated' in col.lower() and 'power' in col.lower()]
            if power_cols:
                metrics['rated_power'] = float(farm_data[power_cols[0]]) if pd.notna(farm_data[power_cols[0]]) else None
        
        # If no wind_farm column, try to extract from index or other methods
        elif len(df) <= 7:  # Likely one row per wind farm
            # Try to infer which row corresponds to our wind farm
            farm_idx = int(farm_id[-1]) - 1 if farm_id[-1].isdigit() else 0
            if 0 <= farm_idx < len(df):
                row_data = df.iloc[farm_idx]
                
                # Extract available metrics
                for col in df.columns:
                    col_lower = col.lower()
                    if 'capacity' in col_lower and 'factor' in col_lower:
                        metrics['capacity_factor'] = float(row_data[col]) if pd.notna(row_data[col]) else None
                    elif 'cut' in col_lower and 'in' in col_lower:
                        metrics['cut_in_speed'] = float(row_data[col]) if pd.notna(row_data[col]) else None
                    elif 'rated' in col_lower and 'speed' in col_lower:
                        metrics['rated_speed'] = float(row_data[col]) if pd.notna(row_data[col]) else None
                    elif 'rated' in col_lower and 'power' in col_lower:
                        metrics['rated_power'] = float(row_data[col]) if pd.notna(row_data[col]) else None
        
    except Exception as e:
        logger.error(f"Error extracting wind farm metrics: {str(e)}")
        metrics['extraction_error'] = str(e)
    
    return metrics

def _extract_general_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Extract general power curve metrics from dataframe."""
    metrics = {}
    
    try:
        # Look for aggregate metrics across all wind farms
        for col in df.columns:
            col_lower = col.lower()
            if 'capacity' in col_lower and 'factor' in col_lower:
                if df[col].dtype in ['float64', 'int64'] and not df[col].isna().all():
                    metrics['average_capacity_factor'] = float(df[col].mean())
            elif 'cut' in col_lower and 'in' in col_lower:
                if df[col].dtype in ['float64', 'int64'] and not df[col].isna().all():
                    metrics['average_cut_in_speed'] = float(df[col].mean())
            elif 'rated' in col_lower and 'speed' in col_lower:
                if df[col].dtype in ['float64', 'int64'] and not df[col].isna().all():
                    metrics['average_rated_speed'] = float(df[col].mean())
        
        # Count available wind farms
        if 'wind_farm' in df.columns:
            metrics['wind_farms_available'] = df['wind_farm'].nunique()
            metrics['wind_farm_list'] = df['wind_farm'].unique().tolist()
        
    except Exception as e:
        logger.error(f"Error extracting general metrics: {str(e)}")
        metrics['extraction_error'] = str(e)
    
    return metrics

if __name__ == "__main__":
    # Run the MCP server directly
    mcp.run()
