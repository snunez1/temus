# Notebook Navigation Guide

You are analyzing wind power forecasting notebooks for the Temus/McKinsey case study. When responding to queries:

## Notebook Structure
- **01_data_foundation.ipynb**: Data quality, missing values, initial exploration, basic statistics
- **02_wind_physics_analysis.ipynb**: Power curves, cut-in/rated speeds, capacity factors, physics validation
- **03_temporal_patterns.ipynb**: Hourly/seasonal patterns, autocorrelations, ramp events
- **04_spatial_analysis.ipynb**: Cross-farm correlations, geographic patterns
- **05_feature_engineering.ipynb**: Feature creation, importance rankings, lag analysis
- **06_baseline_models.ipynb**: Persistence and seasonal naive baselines
- **07_ml_models.ipynb**: Random Forest and XGBoost implementations
- **08_deep_learning.ipynb**: LSTM models for temporal dependencies
- **09_ensemble_uncertainty.ipynb**: Model combination, prediction intervals
- **10_model_evaluation.ipynb**: Performance metrics, error analysis, comparisons
- **11_mcp_service.ipynb**: Production deployment code
- **12_business_impact.ipynb**: CO2 calculations, economic value, grid benefits

## Analysis Context
- **Dataset**: GEF2012 Wind Forecasting Competition
- **Period**: July 2009 - December 2010 (18 months training)
- **Wind Farms**: 7 farms (wf1-wf7) with varying characteristics
- **Forecast Horizons**: 1-48 hours ahead
- **Update Frequency**: Every 6 hours (00, 06, 12, 18 UTC)
- **Target**: Improve upon persistence baseline by >30%

## Response Framework
1. Identify the relevant notebook(s) for the query
2. Look for specific code patterns and results
3. Extract quantitative metrics with business context
4. Provide confidence level in findings
5. Suggest follow-up analyses if relevant

## Key File Locations
- Raw data: `/data/raw/gef2012_wind/`
- Processed results: `/data/processed/`
- Analysis notebooks: `/notebooks/`
