# Wind Power Forecasting Domain Knowledge

## Physical Relationships
Wind power generation follows well-established physics:

### Power Curve Characteristics
- **Power equation**: P = 0.5 × ρ × A × Cp × v³
  - ρ: air density (~1.225 kg/m³ at sea level)
  - A: rotor swept area
  - Cp: power coefficient (~0.35-0.45 for modern turbines)
  - v: wind speed

### Critical Wind Speed Thresholds
- **Cut-in speed**: ~3-4 m/s (turbine starts generating)
- **Rated speed**: ~12-15 m/s (maximum power output)
- **Cut-out speed**: ~25 m/s (turbine shuts down for safety)

### Power Curve Shape
- **Low winds (3-12 m/s)**: Cubic relationship dominates
- **Rated region (12-25 m/s)**: Constant power output
- **Extreme winds (>25 m/s)**: Zero output (safety shutdown)

## Meteorological Factors

### Wind Speed Variability
- **Diurnal patterns**: Typically stronger during day due to thermal effects
- **Seasonal variations**: Higher in winter months in most regions
- **Terrain effects**: Surface roughness, obstacles, topography
- **Atmospheric stability**: Stable vs unstable conditions

### Wind Direction Impact
- **Turbine yaw**: Modern turbines auto-align with wind direction
- **Wake effects**: Downstream turbines receive reduced, turbulent wind
- **Site-specific patterns**: Prevailing wind directions vary by location

## Forecasting Challenges

### Technical Challenges
- **Non-linearity**: Cubic power relationship creates high sensitivity
- **Temporal dependencies**: Weather patterns evolve on multiple timescales
- **Spatial correlations**: Wind farms separated by kilometers show correlation
- **Extreme events**: Hurricane, storm shutdowns difficult to predict
- **Ramp events**: Rapid power changes (>50% in <10 minutes)

### Data Quality Issues
- **Sensor failures**: Anemometer icing, maintenance outages
- **Curtailment**: Grid operator forced reductions not weather-related
- **Missing data**: Communication failures, data logger issues

## Business Context

### Grid Operations
- **Balancing requirements**: Supply must equal demand instantaneously
- **Reserve margins**: Extra capacity needed due to forecast uncertainty
- **Ramping capability**: Conventional plants must compensate for wind variability
- **Transmission constraints**: Power must flow through limited grid capacity

### Economic Impact
- **Forecast value**: 10% RMSE improvement = $1-5M annual savings per 100MW
- **Imbalance penalties**: Grid operators charge for forecast errors
- **Market participation**: Day-ahead and real-time energy markets
- **Renewable integration**: Better forecasts enable higher renewable penetration

### Environmental Benefits
- **CO2 displacement**: Each MWh of wind displaces ~0.4-0.7 tons CO2
- **Grid stability**: Accurate forecasts reduce need for fossil backup
- **Planning efficiency**: Long-term forecasts support transmission investment

## GEF2012 Dataset Specifics

### Wind Farms Characteristics
- **7 different wind farms** (wf1-wf7) with varying:
  - Installed capacity
  - Turbine technology
  - Geographic location
  - Local wind climatology

### Data Structure
- **Training period**: 2009/07/01 - 2010/12/31 (18 months)
- **Test period**: 2011/01/01 - 2012/06/28 (18 months)
- **Forecast horizons**: 1-48 hours ahead
- **Update frequency**: Every 6 hours (00, 06, 12, 18 UTC)
- **Temporal resolution**: Hourly values

### Available Variables
- **Wind speed**: 10m and 100m height forecasts
- **Wind direction**: 10m and 100m height forecasts  
- **Power output**: Historical generation (target variable)
- **Forecast lead time**: 1-48 hours ahead

### Known Data Challenges
- **Missing values**: Some periods have incomplete weather forecasts
- **Outliers**: Extreme weather events, maintenance shutdowns
- **Seasonality**: Strong seasonal patterns in wind resource
- **Forecast accuracy degradation**: Longer horizons have higher uncertainty

## Modeling Considerations

### Feature Engineering Opportunities
- **Lagged power**: Recent generation patterns
- **Rolling statistics**: Moving averages, volatility measures
- **Temporal encoding**: Hour, day, month cyclical features
- **Weather derivatives**: Wind speed cubed, directional components
- **Regime indicators**: High/low wind periods, seasonal flags

### Model Architecture Insights
- **Ensemble benefits**: Different models excel in different conditions
- **Temporal models**: LSTM/GRU for sequential dependencies
- **Non-linear models**: Random Forest, XGBoost for power curve
- **Probabilistic models**: Quantile regression for uncertainty

Remember: Wind forecasting is ultimately about predicting chaotic atmospheric behavior - perfect accuracy is impossible, but systematic improvement is valuable.
