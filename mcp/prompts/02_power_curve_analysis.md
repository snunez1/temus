# Power Curve Analysis Guide

When analyzing power curves and physical characteristics:

## Key Code Patterns to Find
- `groupby(['WIND_FARM', 'wind_bin'])` or `groupby(['farm', 'ws_bin'])`
- `power_curve` variable assignments and calculations
- LOWESS or polynomial fitting code: `lowess()`, `polyfit()`
- Scatter plots of wind speed vs power: `plt.scatter(wind_speed, power)`
- Capacity factor calculations: `mean(power) / rated_capacity`

## Metrics to Extract
1. **Cut-in speed**: Where power output first exceeds 0 (typically 3-4 m/s)
2. **Rated speed**: Where power plateaus at maximum (typically 12-15 m/s)
3. **Cut-out speed**: Where power drops to 0 for safety (typically 25 m/s)
4. **Capacity factor**: Mean(power) / rated_capacity
5. **Power coefficient**: Efficiency of wind-to-power conversion
6. **Power curve smoothness**: R² or correlation metrics

## Analysis Steps for Notebooks
1. **Navigate to notebook 02_wind_physics_analysis.ipynb**
2. Look for wind speed binning logic (usually 0.5 or 1 m/s bins)
3. Find power curve fitting sections with visualization
4. Extract fitted curve parameters and statistics
5. Note any farm-specific differences in turbine characteristics
6. Calculate capacity factors from normalized power output

## Business Context Interpretation
- **Capacity factor > 35%**: Excellent wind resource, suitable for development
- **Capacity factor 25-35%**: Good wind resource, commercially viable
- **Capacity factor < 25%**: Marginal wind resource, requires optimization
- **Cut-in speeds < 3 m/s**: Efficient turbine design, captures low winds
- **Smooth power curves**: Good data quality, reliable turbine operation
- **High rated power**: Optimal turbine sizing for wind resource

## Expected Results in Notebooks
Look for tables or dataframes containing:
- Wind farm capacity factors by farm ID
- Cut-in and rated wind speeds per farm
- Power curve R² values or goodness of fit
- Seasonal capacity factor variations
- Turbine efficiency comparisons

## Response Format
Structure findings as:
1. **Key Metric**: State the specific value (e.g., "Capacity factor: 31.2%")
2. **Source**: Reference notebook section or cell
3. **Comparison**: How this compares to industry standards
4. **Business Implication**: What this means for project viability
