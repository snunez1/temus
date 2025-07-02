#!/usr/bin/env python3
"""
Parquet Data Reader for Wind Farm Analytics MCP Server

This module provides a unified interface to read and normalize data from
pre-processed parquet files, avoiding dynamic notebook execution while
serving structured power curve and forecasting data.
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import json

logger = logging.getLogger(__name__)

class ParquetDataReader:
    """
    Unified data access layer for pre-processed wind farm analysis results.
    
    Reads from parquet files in /data/processed/ and provides normalized
    access to power curve parameters, forecast metrics, and analysis results.
    """
    
    def __init__(self, data_dir: str = "/workspaces/temus/data/processed"):
        """
        Initialize the data reader with the processed data directory.
        
        Args:
            data_dir: Path to directory containing processed parquet files
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")
        
        # Map of data types to their corresponding files
        self.file_mapping = {
            'power_curves': [
                'baseline_power_curve_parameters.parquet',
                'power_curve_parameters.parquet',
                '02_wind_physics_analysis.parquet',
                'combined_power_wind.parquet'
            ],
            'forecast_performance': [
                '07_ml_models_results.parquet',
                '08_deep_learning_results.parquet',
                '06_baseline_models_results.parquet',
                'baseline_modeling_completion.parquet',
                '07_ml_models_48h_results.parquet',
                '07_ml_models_presentation_results.parquet'
            ],
            'temporal_patterns': [
                '03_temporal_patterns_results.parquet',
                '03_temporal_features_enriched.parquet'
            ],
            'spatial_analysis': [
                '04_spatial_analysis_results.parquet',
                '04_spatial_analysis_integrated_results.parquet'
            ],
            'business_impact': [
                '02_wind_physics_analysis.parquet'  # Contains business metrics
            ],
            'comprehensive_results': [
                '01_comprehensive_eda_results.parquet',
                '01_data_foundation_results.parquet'
            ]
        }
        
        # Cache for loaded data to avoid repeated file reads
        self._cache = {}
        
        logger.info(f"ParquetDataReader initialized with data directory: {data_dir}")
    
    def _load_file(self, filename: str) -> Optional[pd.DataFrame]:
        """
        Load a parquet file with error handling and caching.
        
        Args:
            filename: Name of the parquet file to load
            
        Returns:
            DataFrame if successful, None if file not found or error
        """
        if filename in self._cache:
            return self._cache[filename]
        
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
        
        try:
            df = pd.read_parquet(file_path)
            self._cache[filename] = df
            logger.debug(f"Loaded {filename}: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
            return None
    
    def get_power_curve_data(self, wind_farm: str = None) -> Dict[str, Any]:
        """
        Extract power curve parameters for specified wind farm(s).
        
        Args:
            wind_farm: Specific farm ID (e.g., 'wf1', 'wp1') or None for all farms
            
        Returns:
            Dictionary containing power curve parameters and metadata
        """
        results = {
            'wind_farm': wind_farm,
            'power_curve_parameters': {},
            'capacity_factors': {},
            'data_quality': {},
            'source_files': [],
            'metadata': {}
        }
        
        # Load power curve related files
        for filename in self.file_mapping['power_curves']:
            df = self._load_file(filename)
            if df is not None:
                results['source_files'].append(filename)
                
                # Extract power curve parameters based on file structure
                if 'power_curve_parameters' in filename:
                    results['power_curve_parameters'].update(
                        self._extract_power_curve_params(df, wind_farm)
                    )
                elif 'wind_physics' in filename:
                    results['capacity_factors'].update(
                        self._extract_capacity_factors(df, wind_farm)
                    )
                    results['data_quality'].update(
                        self._extract_data_quality(df, wind_farm)
                    )
        
        # Add metadata
        results['metadata'] = {
            'extraction_method': 'parquet_direct_read',
            'files_processed': len(results['source_files']),
            'wind_farms_available': self._get_available_wind_farms()
        }
        
        return results
    
    def get_forecast_performance(self, model_type: str = None, 
                               horizon: int = None) -> Dict[str, Any]:
        """
        Extract forecast performance metrics for specified conditions.
        
        Args:
            model_type: Specific model name or None for all models
            horizon: Forecast horizon or None for all horizons
            
        Returns:
            Dictionary containing performance metrics and comparisons
        """
        results = {
            'model_type': model_type,
            'forecast_horizon': horizon,
            'performance_metrics': {},
            'model_comparisons': {},
            'horizon_analysis': {},
            'source_files': [],
            'metadata': {}
        }
        
        # Load forecast performance files
        for filename in self.file_mapping['forecast_performance']:
            df = self._load_file(filename)
            if df is not None:
                results['source_files'].append(filename)
                
                # Extract performance metrics based on file structure
                if 'ml_models' in filename:
                    results['performance_metrics'].update(
                        self._extract_ml_performance(df, model_type, horizon)
                    )
                elif 'baseline' in filename:
                    results['model_comparisons'].update(
                        self._extract_baseline_comparison(df)
                    )
                elif 'deep_learning' in filename:
                    results['performance_metrics'].update(
                        self._extract_dl_performance(df, model_type, horizon)
                    )
        
        return results
    
    def get_business_metrics(self, accuracy_improvement: float = None) -> Dict[str, Any]:
        """
        Extract business impact metrics including CO2 displacement and economic value.
        
        Args:
            accuracy_improvement: Percentage improvement to calculate impact for
            
        Returns:
            Dictionary containing business impact calculations
        """
        results = {
            'accuracy_improvement': accuracy_improvement,
            'co2_displacement': {},
            'economic_value': {},
            'grid_integration': {},
            'source_files': [],
            'metadata': {}
        }
        
        # Load business impact data
        for filename in self.file_mapping['business_impact']:
            df = self._load_file(filename)
            if df is not None:
                results['source_files'].append(filename)
                results.update(self._extract_business_metrics(df, accuracy_improvement))
        
        return results
    
    def search_data(self, query_terms: List[str], 
                   data_types: List[str] = None) -> Dict[str, Any]:
        """
        Search across all data files for terms matching the query.
        
        Args:
            query_terms: List of terms to search for in column names and values
            data_types: List of data types to search in, or None for all types
            
        Returns:
            Dictionary containing search results and recommendations
        """
        if data_types is None:
            data_types = list(self.file_mapping.keys())
        
        results = {
            'query_terms': query_terms,
            'search_results': {},
            'recommendations': [],
            'source_files': []
        }
        
        # Search across specified data types
        for data_type in data_types:
            if data_type in self.file_mapping:
                for filename in self.file_mapping[data_type]:
                    df = self._load_file(filename)
                    if df is not None:
                        matches = self._search_dataframe(df, query_terms)
                        if matches:
                            results['search_results'][filename] = matches
                            results['source_files'].append(filename)
        
        # Generate recommendations based on search results
        results['recommendations'] = self._generate_search_recommendations(
            results['search_results'], query_terms
        )
        
        return results
    
    def _extract_power_curve_params(self, df: pd.DataFrame, 
                                   wind_farm: str = None) -> Dict[str, Any]:
        """Extract power curve parameters from dataframe."""
        params = {}
        
        try:
            # Filter by wind farm if specified
            if wind_farm and 'wind_farm' in df.columns:
                # Normalize wind farm ID
                wind_farm_normalized = self._normalize_wind_farm_id(wind_farm)
                df_filtered = df[df['wind_farm'].str.contains(wind_farm_normalized, case=False, na=False)]
            else:
                df_filtered = df
            
            # Extract common power curve parameters
            param_columns = [
                'cut_in_speed', 'rated_speed', 'cut_out_speed', 
                'rated_power', 'capacity_factor', 'power_coefficient'
            ]
            
            for col in param_columns:
                if col in df_filtered.columns:
                    params[col] = df_filtered[col].to_dict() if len(df_filtered) > 1 else df_filtered[col].iloc[0] if len(df_filtered) > 0 else None
            
        except Exception as e:
            logger.error(f"Error extracting power curve parameters: {str(e)}")
            params['error'] = str(e)
        
        return params
    
    def _extract_capacity_factors(self, df: pd.DataFrame, 
                                 wind_farm: str = None) -> Dict[str, Any]:
        """Extract capacity factor data from dataframe."""
        capacity_data = {}
        
        try:
            # Look for capacity factor columns
            cf_columns = [col for col in df.columns if 'capacity' in col.lower() or 'cf' in col.lower()]
            
            if wind_farm and 'wind_farm' in df.columns:
                wind_farm_normalized = self._normalize_wind_farm_id(wind_farm)
                df_filtered = df[df['wind_farm'].str.contains(wind_farm_normalized, case=False, na=False)]
            else:
                df_filtered = df
            
            for col in cf_columns:
                capacity_data[col] = df_filtered[col].to_dict() if len(df_filtered) > 1 else df_filtered[col].iloc[0] if len(df_filtered) > 0 else None
                
        except Exception as e:
            logger.error(f"Error extracting capacity factors: {str(e)}")
            capacity_data['error'] = str(e)
        
        return capacity_data
    
    def _extract_data_quality(self, df: pd.DataFrame, 
                             wind_farm: str = None) -> Dict[str, Any]:
        """Extract data quality metrics from dataframe."""
        quality_data = {}
        
        try:
            # Look for data quality indicators
            quality_columns = [col for col in df.columns if any(term in col.lower() 
                             for term in ['missing', 'outlier', 'quality', 'r2', 'correlation'])]
            
            if wind_farm and 'wind_farm' in df.columns:
                wind_farm_normalized = self._normalize_wind_farm_id(wind_farm)
                df_filtered = df[df['wind_farm'].str.contains(wind_farm_normalized, case=False, na=False)]
            else:
                df_filtered = df
            
            for col in quality_columns:
                quality_data[col] = df_filtered[col].to_dict() if len(df_filtered) > 1 else df_filtered[col].iloc[0] if len(df_filtered) > 0 else None
                
        except Exception as e:
            logger.error(f"Error extracting data quality: {str(e)}")
            quality_data['error'] = str(e)
        
        return quality_data
    
    def _extract_ml_performance(self, df: pd.DataFrame, model_type: str = None, 
                               horizon: int = None) -> Dict[str, Any]:
        """Extract ML model performance metrics."""
        performance = {}
        
        try:
            # Filter by model type if specified
            if model_type and 'model' in df.columns:
                df_filtered = df[df['model'].str.contains(model_type, case=False, na=False)]
            else:
                df_filtered = df
            
            # Filter by horizon if specified
            if horizon and 'horizon' in df_filtered.columns:
                df_filtered = df_filtered[df_filtered['horizon'] == horizon]
            
            # Extract performance metrics
            metric_columns = [col for col in df_filtered.columns if any(term in col.lower() 
                            for term in ['rmse', 'mae', 'mape', 'r2', 'skill'])]
            
            for col in metric_columns:
                performance[col] = df_filtered[col].to_dict() if len(df_filtered) > 1 else df_filtered[col].iloc[0] if len(df_filtered) > 0 else None
                
        except Exception as e:
            logger.error(f"Error extracting ML performance: {str(e)}")
            performance['error'] = str(e)
        
        return performance
    
    def _extract_dl_performance(self, df: pd.DataFrame, model_type: str = None, 
                               horizon: int = None) -> Dict[str, Any]:
        """Extract deep learning model performance metrics."""
        # Similar to ML performance but for deep learning models
        return self._extract_ml_performance(df, model_type, horizon)
    
    def _extract_baseline_comparison(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract baseline model comparison data."""
        comparison = {}
        
        try:
            # Look for baseline comparison metrics
            baseline_columns = [col for col in df.columns if any(term in col.lower() 
                              for term in ['baseline', 'persistence', 'naive', 'skill_score'])]
            
            for col in baseline_columns:
                comparison[col] = df[col].to_dict() if len(df) > 1 else df[col].iloc[0] if len(df) > 0 else None
                
        except Exception as e:
            logger.error(f"Error extracting baseline comparison: {str(e)}")
            comparison['error'] = str(e)
        
        return comparison
    
    def _extract_business_metrics(self, df: pd.DataFrame, 
                                 accuracy_improvement: float = None) -> Dict[str, Any]:
        """Extract business impact metrics from dataframe."""
        business_data = {}
        
        try:
            # Look for business-related columns
            business_columns = [col for col in df.columns if any(term in col.lower() 
                              for term in ['co2', 'carbon', 'economic', 'value', 'cost', 'revenue'])]
            
            for col in business_columns:
                business_data[col] = df[col].to_dict() if len(df) > 1 else df[col].iloc[0] if len(df) > 0 else None
            
            # Calculate scaled metrics if accuracy improvement provided
            if accuracy_improvement and business_data:
                business_data['scaled_metrics'] = self._scale_business_metrics(
                    business_data, accuracy_improvement
                )
                
        except Exception as e:
            logger.error(f"Error extracting business metrics: {str(e)}")
            business_data['error'] = str(e)
        
        return business_data
    
    def _search_dataframe(self, df: pd.DataFrame, 
                         query_terms: List[str]) -> Dict[str, Any]:
        """Search dataframe for query terms in columns and values."""
        matches = {
            'column_matches': [],
            'value_matches': {},
            'summary_stats': {}
        }
        
        try:
            # Search column names
            for term in query_terms:
                matching_cols = [col for col in df.columns if term.lower() in col.lower()]
                if matching_cols:
                    matches['column_matches'].extend(matching_cols)
            
            # Search values in text columns
            for col in df.columns:
                if df[col].dtype == 'object':  # Text columns
                    for term in query_terms:
                        matching_rows = df[df[col].astype(str).str.contains(term, case=False, na=False)]
                        if len(matching_rows) > 0:
                            matches['value_matches'][f"{col}_{term}"] = len(matching_rows)
            
            # Add summary statistics for matching columns
            for col in matches['column_matches']:
                if col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        matches['summary_stats'][col] = {
                            'mean': df[col].mean(),
                            'std': df[col].std(),
                            'min': df[col].min(),
                            'max': df[col].max()
                        }
                    else:
                        matches['summary_stats'][col] = {
                            'unique_values': df[col].nunique(),
                            'most_common': df[col].mode().iloc[0] if len(df[col].mode()) > 0 else None
                        }
                        
        except Exception as e:
            logger.error(f"Error searching dataframe: {str(e)}")
            matches['error'] = str(e)
        
        return matches if (matches['column_matches'] or matches['value_matches']) else {}
    
    def _generate_search_recommendations(self, search_results: Dict[str, Any], 
                                       query_terms: List[str]) -> List[str]:
        """Generate analysis recommendations based on search results."""
        recommendations = []
        
        # Analyze search patterns and suggest next steps
        if any('power' in str(results) for results in search_results.values()):
            recommendations.append("Consider analyzing power curve characteristics using analyze_power_curves()")
        
        if any('forecast' in str(results) or 'rmse' in str(results) for results in search_results.values()):
            recommendations.append("Evaluate forecast performance using evaluate_forecast_performance()")
        
        if any('temporal' in str(results) or 'time' in str(results) for results in search_results.values()):
            recommendations.append("Assess temporal patterns using assess_temporal_patterns()")
        
        if any('business' in str(results) or 'co2' in str(results) for results in search_results.values()):
            recommendations.append("Calculate business impact using calculate_business_impact()")
        
        return recommendations
    
    # Public convenience methods
    def normalize_wind_farm_id(self, wind_farm: str) -> str:
        """
        Normalize wind farm ID to a consistent format.
        
        Args:
            wind_farm: Wind farm ID in any format (wf1, wp1, 1, etc.)
            
        Returns:
            Normalized wind farm ID in wp format
        """
        return self._normalize_wind_farm_id(wind_farm)
    
    def get_available_wind_farms(self) -> List[str]:
        """
        Get list of available wind farms from the data.
        
        Returns:
            List of available wind farm IDs
        """
        return self._get_available_wind_farms()
    
    def get_capacity_factors(self, wind_farm: str = None) -> Dict[str, Any]:
        """
        Get capacity factors for specified wind farm(s).
        
        Args:
            wind_farm: Specific farm ID or None for all farms
            
        Returns:
            Dictionary containing capacity factor data
        """
        return self.get_power_curve_data(wind_farm).get('capacity_factors', {})
    
    def get_data_quality_metrics(self, wind_farm: str = None) -> Dict[str, Any]:
        """
        Get data quality metrics for specified wind farm(s).
        
        Args:
            wind_farm: Specific farm ID or None for all farms
            
        Returns:
            Dictionary containing data quality metrics
        """
        return self.get_power_curve_data(wind_farm).get('data_quality', {})
    
    def get_wind_farm_summary(self, wind_farm: str = None) -> Dict[str, Any]:
        """
        Get comprehensive summary for specified wind farm(s).
        
        Args:
            wind_farm: Specific farm ID or None for all farms
            
        Returns:
            Dictionary containing comprehensive wind farm summary
        """
        # Combine power curve and performance data
        power_data = self.get_power_curve_data(wind_farm)
        performance_data = self.get_forecast_performance()
        
        return {
            'wind_farm': wind_farm,
            'power_curves': power_data.get('power_curve_parameters', {}),
            'capacity_factors': power_data.get('capacity_factors', {}),
            'data_quality': power_data.get('data_quality', {}),
            'forecast_performance': performance_data.get('performance_summary', {}),
            'metadata': {
                'data_sources': power_data.get('source_files', []),
                'available_farms': self.get_available_wind_farms()
            }
        }
    
    # Private helper methods
    def _normalize_wind_farm_id(self, wind_farm: str) -> str:
        """Normalize wind farm ID to a consistent format."""
        wind_farm = wind_farm.lower().strip()
        
        # Handle various formats: wf1, wp1, wind_farm_1, etc.
        if wind_farm.startswith('wf'):
            return wind_farm.replace('wf', 'wp')
        elif not wind_farm.startswith('wp'):
            # Extract number and create wp format
            import re
            numbers = re.findall(r'\d+', wind_farm)
            if numbers:
                return f'wp{numbers[0]}'
        
        return wind_farm
    
    def _get_available_wind_farms(self) -> List[str]:
        """Get list of available wind farms from the data."""
        wind_farms = set()
        
        # Check all files for wind farm identifiers
        for file_list in self.file_mapping.values():
            for filename in file_list:
                df = self._load_file(filename)
                if df is not None and 'wind_farm' in df.columns:
                    wind_farms.update(df['wind_farm'].unique())
        
        return sorted(list(wind_farms))
    
    def _scale_business_metrics(self, metrics: Dict[str, Any], 
                               improvement: float) -> Dict[str, Any]:
        """Scale business metrics based on forecast accuracy improvement."""
        scaled = {}
        
        try:
            # Scale metrics proportionally to improvement
            for key, value in metrics.items():
                if isinstance(value, (int, float)) and value > 0:
                    scaled[f"{key}_scaled"] = value * (improvement / 100.0)
                    
        except Exception as e:
            logger.error(f"Error scaling business metrics: {str(e)}")
            scaled['error'] = str(e)
        
        return scaled
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of all available data files and their contents."""
        summary = {
            'total_files': 0,
            'file_details': {},
            'data_types': list(self.file_mapping.keys()),
            'available_wind_farms': self._get_available_wind_farms(),
            'file_status': {}
        }
        
        # Check each file's status and basic info
        for data_type, file_list in self.file_mapping.items():
            summary['file_details'][data_type] = []
            
            for filename in file_list:
                file_path = self.data_dir / filename
                file_info = {
                    'filename': filename,
                    'exists': file_path.exists(),
                    'size_mb': None,
                    'shape': None,
                    'columns': None
                }
                
                if file_path.exists():
                    try:
                        file_info['size_mb'] = round(file_path.stat().st_size / (1024 * 1024), 2)
                        df = self._load_file(filename)
                        if df is not None:
                            file_info['shape'] = df.shape
                            file_info['columns'] = list(df.columns)
                            summary['total_files'] += 1
                    except Exception as e:
                        file_info['error'] = str(e)
                
                summary['file_details'][data_type].append(file_info)
        
        return summary
