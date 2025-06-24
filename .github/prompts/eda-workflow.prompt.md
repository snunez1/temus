# Wind Power EDA Workflow

Generate comprehensive exploratory data analysis following this structure:

## Data Documentation Reference
Before beginning analysis, review the data description files:
- [`data/raw/gef2012_wind/data-description.md`](data/raw/gef2012_wind/data-description.md)
- [`data/raw/gef2012_load/data-description.md`](data/raw/gef2012_load/data-description.md)
- [`data/raw/world_sustainability/data-description.md`](data/raw/world_sustainability/data-description.md)
- [`data/raw/world_sustainability/data-dictionary.csv`](data/raw/world_sustainability/data-dictionary.csv)

## 1. Progressive Data Loading Strategy
```python
# Step 1: Check file size to determine approach
file_sizes = {
    'train': os.path.getsize('data/raw/train.csv') / (1024**2),  # MB
    'test': os.path.getsize('data/raw/test.csv') / (1024**2)     # MB
}

# Step 2: Preview structure with small sample
train_preview = pd.read_csv('data/raw/train.csv', nrows=5)
print(f"Columns available: {train_preview.columns.tolist()}")

# Step 3: Size-based loading strategy
if file_sizes['train'] < 50:  # If < 50MB
    # Load everything for initial exploration
    train_data = pd.read_csv('data/raw/train.csv', parse_dates=['TIMESTAMP'])
else:
    # Start with essential columns based on documentation
    essential_cols = ['TIMESTAMP', 'WIND_FARM', 'POWER']
    train_data = pd.read_csv('data/raw/train.csv', usecols=essential_cols)
    
# Step 4: Column categorization framework
column_categories = {
    'essential': ['TIMESTAMP', 'WIND_FARM', 'POWER'],  # Always needed
    'primary_features': ['WS_10', 'WS_100', 'WD_10', 'WD_100'],  # Core weather
    'secondary_features': [],  # To be determined during EDA
    'metadata': [],  # Administrative columns
    'derived': []  # Will be created during analysis
}

# Step 5: Iterative column addition
# As important columns are identified, add them to the dataset:
for feature in column_categories['primary_features']:
    if feature not in train_data.columns:
        temp_df = pd.read_csv('data/raw/train.csv', usecols=[feature])
        train_data[feature] = temp_df[feature]
```

## 2. Data Loading and Quality Check

### Key Quality Metrics to Report
- Missing data percentage by wind farm
- Temporal coverage completeness
- Outlier counts and patterns
- Data consistency across farms

### Data Dictionary Validation
Validate data against expectations from data-description.md files:

```python
# Check variable presence and types based on data documentation
expected_columns = {
    'train_data': ['TIMESTAMP', 'WIND_FARM', 'POWER'],
    'wind_forecasts': ['TIMESTAMP', 'WS_10', 'WS_100', 'WD_10', 'WD_100', 'HCAST'],
    'test_data': ['TIMESTAMP', 'WIND_FARM']
}

# Validate against data description specifications
for dataset_name, expected_cols in expected_columns.items():
    dataset = eval(dataset_name) if dataset_name != 'wind_forecasts' else wind_forecasts[0]
    missing_cols = set(expected_cols) - set(dataset.columns)
    extra_cols = set(dataset.columns) - set(expected_cols)
    
    print(f"{dataset_name}:")
    print(f"  Missing expected columns: {missing_cols}")
    print(f"  Additional columns: {extra_cols}")
    
# Cross-reference with data-description.md for:
# - Units: Power (MW), Wind Speed (m/s), Wind Direction (degrees) 
# - Temporal resolution: Hourly measurements
# - Forecast horizons: 1-48 hours ahead
# - Update frequency: Every 6 hours (00, 06, 12, 18 UTC)
```

## 3. Statistical Summary Analysis

```python
# Descriptive statistics by wind farm
summary_stats = train_data.groupby('WIND_FARM').agg({
    'POWER': ['count', 'mean', 'std', 'min', 'max', 'skew', 'kurt'],
    'WS_10': ['mean', 'std', 'max'],
    'WS_100': ['mean', 'std', 'max'],
    'WD_10': ['mean', 'std']
})

# Cross-farm correlation analysis
power_correlations = train_data.pivot_table(
    values='POWER', index='TIMESTAMP', columns='WIND_FARM'
).corr()
```

### Statistical Insights to Highlight
- Capacity factors by wind farm (mean power / max power)
- Wind resource quality (mean wind speeds, variability)
- Inter-farm correlations (geographic clustering effects)
- Distribution shapes and outlier patterns

## 4. Temporal Pattern Analysis

### Hourly Patterns
```python
@create_figure
def plot_hourly_patterns(data):
    hourly_avg = data.groupby([data['TIMESTAMP'].dt.hour, 'WIND_FARM'])['POWER'].mean()
    # Line plot showing diurnal cycles by farm
    # Highlight differences in peak generation times
```

### Seasonal Analysis
```python
@create_figure 
def plot_seasonal_patterns(data):
    monthly_avg = data.groupby([data['TIMESTAMP'].dt.month, 'WIND_FARM'])['POWER'].mean()
    # Show seasonal resource variations
    # Identify high/low wind months
```

### Autocorrelation Analysis
```python
# Calculate autocorrelation for different lags
lags = [1, 6, 12, 24, 48, 168]  # 1h to 1 week
autocorr_results = {}
for farm in wind_farms:
    farm_data = data[data['WIND_FARM'] == farm]['POWER']
    autocorr_results[farm] = [farm_data.autocorr(lag=lag) for lag in lags]
```

### Temporal Insights to Extract
- Diurnal generation patterns (day vs night)
- Weekly cycles (weekday vs weekend differences)
- Seasonal resource availability
- Persistence characteristics (autocorrelation decay)
- Ramping event frequency and magnitude

## 5. Wind-Power Relationship Analysis

### Power Curve Visualization
```python
@create_figure
def plot_power_curves(data):
    # Scatter plot: wind speed vs power for each farm
    # Overlay theoretical power curve
    # Highlight cut-in, rated, cut-out speeds
    # Color by wind direction or season
```

### Binned Analysis
```python
# Create wind speed bins for cleaner analysis
wind_bins = np.arange(0, 25, 1)  # 1 m/s bins
binned_analysis = data.groupby([
    pd.cut(data['WS_100'], wind_bins), 
    'WIND_FARM'
])['POWER'].agg(['mean', 'std', 'count'])
```

### Direction Effects
```python
@create_figure
def plot_direction_effects(data):
    # Wind rose plots showing power by direction
    # Identify optimal wind directions per farm
    # Show directional variability in power output
```

### Wind-Power Insights to Document
- Cut-in speeds by wind farm (when power generation starts)
- Rated speeds and capacities (maximum power plateaus)  
- Power curve efficiency variations between farms
- Directional effects on power generation
- Scatter in power curves (measurement noise, turbulence)

## 6. Forecast Performance Analysis

### Historical Forecast Accuracy
```python
# Merge forecast data with actual power generation
forecast_eval = pd.merge(
    actual_power, wind_forecasts, 
    on=['TIMESTAMP', 'WIND_FARM'], 
    suffixes=('_actual', '_forecast')
)

# Calculate forecast errors by horizon
forecast_errors = {}
for horizon in range(1, 49):
    errors = forecast_eval[f'WS_100_h{horizon}'] - forecast_eval['WS_100_actual']
    forecast_errors[horizon] = {
        'bias': errors.mean(),
        'mae': errors.abs().mean(), 
        'rmse': np.sqrt((errors**2).mean())
    }
```

### Forecast Quality Insights
- Error growth with forecast horizon
- Seasonal bias patterns in forecasts
- Farm-specific forecast accuracy differences
- Weather regime dependent performance

## 7. Feature Engineering Insights

### Lag Feature Analysis
```python
# Test different lag periods for power and wind
lag_periods = [1, 3, 6, 12, 24, 48]
lag_correlations = {}

for lag in lag_periods:
    lag_correlations[f'power_lag_{lag}'] = data['POWER'].corr(
        data['POWER'].shift(lag)
    )
```

### Rolling Statistics
```python
# Rolling averages and volatility measures
rolling_windows = [3, 6, 12, 24]
for window in rolling_windows:
    data[f'power_rolling_mean_{window}'] = data['POWER'].rolling(window).mean()
    data[f'power_rolling_std_{window}'] = data['POWER'].rolling(window).std()
```

### Temporal Encoding
```python
# Cyclical encoding for temporal features
data['hour_sin'] = np.sin(2 * np.pi * data['TIMESTAMP'].dt.hour / 24)
data['hour_cos'] = np.cos(2 * np.pi * data['TIMESTAMP'].dt.hour / 24)
data['day_sin'] = np.sin(2 * np.pi * data['TIMESTAMP'].dt.dayofyear / 365)
data['day_cos'] = np.cos(2 * np.pi * data['TIMESTAMP'].dt.dayofyear / 365)
```

## 8. Visualization Standards

### Use Decorator Pattern for All Plots
```python
def create_figure(func):
    """Decorator for consistent plot styling"""
    def wrapper(*args, **kwargs):
        fig, ax = plt.subplots(figsize=(12, 8))
        result = func(*args, ax=ax, **kwargs)
        ax.grid(True, alpha=0.3)
        ax.set_title(func.__name__.replace('_', ' ').title(), fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig, ax
    return wrapper
```

### Professional Styling Requirements
- Use consistent color palette (avoid rainbow colors)
- Include informative titles and axis labels
- Add grid lines for readability
- Use appropriate chart types for data relationships
- Include statistical annotations where relevant

## 9. Key Insights Documentation

Structure your EDA findings as actionable insights, referencing data documentation for context:

### Data Quality Summary (Reference: data-description.md files)
- Overall data completeness: X% complete
- Critical missing periods identified (cross-check with known collection issues)
- Outlier patterns requiring attention (validate against expected ranges in documentation)
- Data consistency with documented specifications

### Business Context Insights  
- Best performing wind farms (capacity factors) - compare with documented farm characteristics
- Seasonal generation patterns for planning - align with documented time periods
- Cross-farm correlations for portfolio effects - consider geographic information from data descriptions

### Data Documentation Alignment Check
Validate key findings against data-description.md specifications:

```python
# Cross-reference EDA findings with documented expectations
documented_insights = {
    'gef2012_wind': {
        'training_period': '2009/07/01 - 2010/12/31',
        'test_period': '2011/01/01 - 2012/06/28', 
        'forecast_horizons': '1-48 hours ahead',
        'update_frequency': 'Every 6 hours (00, 06, 12, 18 UTC)',
        'wind_farms': 7,
        'known_issues': 'Check data-description.md for documented data quality concerns'
    }
}

# Verify EDA results match documented dataset characteristics
print("Validating EDA findings against data documentation:")
print(f"Training period matches: {train_data.index.min()} to {train_data.index.max()}")
print(f"Number of wind farms found: {train_data['WIND_FARM'].nunique()}")
print(f"Forecast horizons available: {wind_forecasts[0]['HCAST'].min()} to {wind_forecasts[0]['HCAST'].max()}")
```

### Modeling Recommendations
- Optimal lag periods for temporal features (informed by documented collection frequency)
- Most predictive wind speed measurements (10m vs 100m based on data descriptions)
- Seasonal modeling considerations (aligned with documented time coverage)
- Farm-specific vs unified modeling approach (consider documented farm differences)

### Risk Factors Identified
- Data quality issues affecting model performance (cross-reference with documented limitations)
- Extreme weather patterns requiring special handling (validate against documented ranges)
- Forecast degradation patterns to monitor (align with documented forecast characteristics)

Always frame findings in terms of their implications for model development and business deployment. Each insight should lead to a specific modeling decision or risk mitigation strategy, validated against the comprehensive data documentation provided.
