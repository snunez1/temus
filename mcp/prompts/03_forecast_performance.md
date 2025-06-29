# Forecast Performance Analysis Guide

When evaluating model performance and forecast accuracy:

## Code Patterns to Identify
- `rmse`, `mae`, `mape` calculations
- `model.evaluate()` or `score()` methods
- Performance comparison tables/dataframes
- Horizon-specific error calculations: `errors_by_horizon`
- Cross-validation results: `cv_scores`, `validation_results`

## Key Metrics by Model Type

### Baseline Models (notebook 06_baseline_models.ipynb)
- **Persistence**: `y_pred = y_lag_1` (copy last observation)
- **Seasonal naive**: `y_pred = y_lag_168` (weekly seasonal)
- Look for baseline RMSE typically 0.15-0.20

### ML Models (notebook 07_ml_models.ipynb)
- **Random Forest**: Look for `RandomForestRegressor`
- **XGBoost**: Look for `XGBRegressor` or `xgb.train()`
- Feature importance plots and rankings

### Deep Learning (notebook 08_deep_learning.ipynb)
- **LSTM**: Sequential models with LSTM layers
- Training history plots: `history.history['loss']`
- Validation curves and overfitting analysis

## Performance Extraction Steps
1. **Navigate to notebook 10_model_evaluation.ipynb** for comprehensive results
2. Find test set evaluation sections
3. Extract RMSE/MAE by forecast horizon (1-48 hours)
4. Calculate improvement over persistence baseline
5. Note performance degradation with longer horizons
6. Identify best model for each horizon range

## Business Performance Metrics
- **Target RMSE**: < 0.15 for operational deployment
- **Improvement threshold**: 30% better than persistence
- **Forecast value**: 10% RMSE improvement = $1-5M annual savings per 100MW
- **Grid integration**: Better forecasts enable 2% higher renewable penetration per 10% accuracy gain

## Expected Results Patterns
Look for results tables showing:
- Model comparison matrix (RMSE by model and horizon)
- Percentage improvement over baseline
- Statistical significance tests
- Seasonal performance variations
- Farm-specific model performance

## Response Structure
1. **Best Model**: State top performer and its RMSE
2. **Baseline Comparison**: Improvement percentage over persistence
3. **Horizon Analysis**: How accuracy degrades over time
4. **Business Value**: Translate to economic/environmental impact
5. **Confidence**: Note statistical significance and validation approach
