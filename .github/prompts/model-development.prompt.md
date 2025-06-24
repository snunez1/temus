# Wind Power Model Development Guide

Follow this systematic approach for developing wind power forecasting models:

## 1. Baseline Models Implementation

Establish performance benchmarks before complex modeling:

```python
class BaselineModels:
    """Collection of simple baseline forecasting models"""
    
    def persistence_forecast(self, last_power, horizon):
        """Use last known power value for all horizons"""
        return np.repeat(last_power, horizon)
    
    def seasonal_naive_forecast(self, historical_power, current_time, horizon):
        """Use same hour from previous week"""
        week_ago = current_time - pd.Timedelta(days=7)
        # Return power values from same hours one week ago
        
    def linear_power_curve(self, wind_speed, turbine_params):
        """Simple linear approximation of power curve"""
        # Implement piecewise linear model with cut-in, rated, cut-out
```

### Baseline Performance Targets
- Persistence model: Benchmark for short horizons (1-6h)
- Seasonal naive: Benchmark for diurnal patterns (12-48h)
- Linear power curve: Physics-based lower bound

## 2. Feature Engineering Pipeline

Create comprehensive feature sets systematically:

```python
class WindPowerFeatureEngineer:
    """Systematic feature creation for wind power forecasting"""
    
    def create_temporal_features(self, df):
        """Cyclical encoding of time components"""
        # Hour of day (0-23)
        df['hour_sin'] = np.sin(2 * np.pi * df.index.hour / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df.index.hour / 24)
        
        # Day of year (1-365)
        df['day_sin'] = np.sin(2 * np.pi * df.index.dayofyear / 365)
        df['day_cos'] = np.cos(2 * np.pi * df.index.dayofyear / 365)
        
        # Day of week (0-6)
        df['dow_sin'] = np.sin(2 * np.pi * df.index.dayofweek / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df.index.dayofweek / 7)
        
    def create_wind_features(self, df):
        """Wind-specific feature transformations"""
        # Cubic transformation (physics-based)
        df['ws_100_cubed'] = df['WS_100'] ** 3
        
        # Wind direction components
        df['wd_sin'] = np.sin(np.radians(df['WD_100']))
        df['wd_cos'] = np.cos(np.radians(df['WD_100']))
        
        # Wind speed binning (regime identification)
        df['wind_regime'] = pd.cut(df['WS_100'], 
                                  bins=[0, 3, 12, 25, 50], 
                                  labels=['calm', 'operating', 'rated', 'extreme'])
        
    def create_lag_features(self, df, target_col='POWER'):
        """Lagged features for temporal dependencies"""
        lag_periods = [1, 3, 6, 12, 24, 48, 168]  # 1h to 1 week
        
        for lag in lag_periods:
            df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
            
    def create_rolling_features(self, df, target_col='POWER'):
        """Rolling statistics for trend capture"""
        windows = [3, 6, 12, 24]
        
        for window in windows:
            df[f'{target_col}_rolling_mean_{window}'] = df[target_col].rolling(window).mean()
            df[f'{target_col}_rolling_std_{window}'] = df[target_col].rolling(window).std()
            df[f'{target_col}_rolling_min_{window}'] = df[target_col].rolling(window).min()
            df[f'{target_col}_rolling_max_{window}'] = df[target_col].rolling(window).max()
```

## 3. Time Series Cross-Validation

Implement proper temporal validation to avoid data leakage:

```python
class TimeSeriesCrossValidator:
    """Time-aware cross-validation for forecasting models"""
    
    def __init__(self, initial_train_size, forecast_horizon, step_size):
        self.initial_train_size = initial_train_size
        self.forecast_horizon = forecast_horizon
        self.step_size = step_size
        
    def split(self, data):
        """Generate time-ordered train/validation splits"""
        n_samples = len(data)
        
        for i in range(self.initial_train_size, 
                      n_samples - self.forecast_horizon, 
                      self.step_size):
            
            train_idx = slice(0, i)
            val_idx = slice(i, i + self.forecast_horizon)
            
            yield train_idx, val_idx
```

## 4. Model Implementation Strategy

### 4.1 Random Forest for Non-linear Patterns
```python
class WindPowerRandomForest:
    """Random Forest optimized for wind power forecasting"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            bootstrap=True,
            oob_score=True,
            random_state=42,
            n_jobs=-1
        )
        
    def fit_with_cv(self, X, y, cv_splits):
        """Fit with cross-validation and hyperparameter tuning"""
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 15, 20],
            'min_samples_split': [2, 5, 10]
        }
        
        grid_search = GridSearchCV(
            self.model, param_grid, 
            cv=cv_splits, 
            scoring='neg_root_mean_squared_error',
            n_jobs=-1
        )
        
        grid_search.fit(X, y)
        self.model = grid_search.best_estimator_
        return grid_search.best_score_
```

### 4.2 XGBoost for Complex Interactions
```python
class WindPowerXGBoost:
    """XGBoost with early stopping and regularization"""
    
    def __init__(self):
        self.model = XGBRegressor(
            objective='reg:squarederror',
            n_estimators=1000,
            max_depth=6,
            learning_rate=0.01,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        
    def fit_with_early_stopping(self, X_train, y_train, X_val, y_val):
        """Training with early stopping to prevent overfitting"""
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=50,
            verbose=False
        )
        
        return self.model.best_score
```

### 4.3 LSTM for Temporal Dependencies
```python
class WindPowerLSTM:
    """LSTM model for capturing temporal patterns"""
    
    def __init__(self, sequence_length=48, n_features=10):
        self.sequence_length = sequence_length
        self.model = Sequential([
            LSTM(128, return_sequences=True, input_shape=(sequence_length, n_features)),
            Dropout(0.2),
            LSTM(64, return_sequences=False),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(1)
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
    def prepare_sequences(self, data, target_col):
        """Convert time series to supervised learning sequences"""
        X, y = [], []
        
        for i in range(self.sequence_length, len(data)):
            X.append(data.iloc[i-self.sequence_length:i].values)
            y.append(data[target_col].iloc[i])
            
        return np.array(X), np.array(y)
```

### 4.4 Ensemble Model
```python
class WindPowerEnsemble:
    """Weighted ensemble of multiple models"""
    
    def __init__(self, models, weights=None):
        self.models = models
        self.weights = weights or [1/len(models)] * len(models)
        
    def fit(self, X, y):
        """Train all ensemble members"""
        for model in self.models:
            model.fit(X, y)
            
    def predict(self, X):
        """Weighted average prediction"""
        predictions = np.array([model.predict(X) for model in self.models])
        return np.average(predictions, axis=0, weights=self.weights)
        
    def optimize_weights(self, X_val, y_val):
        """Optimize ensemble weights on validation set"""
        val_predictions = np.array([model.predict(X_val) for model in self.models])
        
        def objective(weights):
            ensemble_pred = np.average(val_predictions, axis=0, weights=weights)
            return mean_squared_error(y_val, ensemble_pred)
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = [(0, 1) for _ in range(len(self.models))]
        
        result = minimize(objective, self.weights, 
                         method='SLSQP', bounds=bounds, constraints=constraints)
        
        self.weights = result.x
```

## 5. Evaluation Strategy

### Performance Metrics by Horizon
```python
def evaluate_by_horizon(y_true, y_pred, horizons):
    """Calculate metrics for different forecast horizons"""
    results = {}
    
    for h in horizons:
        h_true = y_true[:, h-1] if y_true.ndim > 1 else y_true
        h_pred = y_pred[:, h-1] if y_pred.ndim > 1 else y_pred
        
        results[f'horizon_{h}'] = {
            'rmse': np.sqrt(mean_squared_error(h_true, h_pred)),
            'mae': mean_absolute_error(h_true, h_pred),
            'mape': np.mean(np.abs((h_true - h_pred) / h_true)) * 100,
            'r2': r2_score(h_true, h_pred)
        }
    
    return results
```

### Wind Regime Performance
```python
def evaluate_by_wind_regime(y_true, y_pred, wind_speeds):
    """Performance analysis by wind conditions"""
    regimes = {
        'low_wind': wind_speeds < 6,
        'medium_wind': (wind_speeds >= 6) & (wind_speeds < 12),
        'high_wind': wind_speeds >= 12
    }
    
    results = {}
    for regime, mask in regimes.items():
        if np.sum(mask) > 0:
            results[regime] = {
                'rmse': np.sqrt(mean_squared_error(y_true[mask], y_pred[mask])),
                'count': np.sum(mask),
                'percentage': np.sum(mask) / len(mask) * 100
            }
    
    return results
```

## 6. Uncertainty Quantification

### Quantile Regression
```python
class QuantileForecaster:
    """Multi-quantile forecasting for uncertainty bounds"""
    
    def __init__(self, quantiles=[0.1, 0.25, 0.5, 0.75, 0.9]):
        self.quantiles = quantiles
        self.models = {}
        
    def fit(self, X, y):
        """Train separate models for each quantile"""
        for q in self.quantiles:
            self.models[q] = GradientBoostingRegressor(
                loss='quantile',
                alpha=q,
                n_estimators=200,
                max_depth=6,
                random_state=42
            )
            self.models[q].fit(X, y)
            
    def predict_intervals(self, X, confidence_level=0.8):
        """Generate prediction intervals"""
        lower_q = (1 - confidence_level) / 2
        upper_q = 1 - lower_q
        
        predictions = {}
        for q in self.quantiles:
            predictions[q] = self.models[q].predict(X)
            
        return {
            'median': predictions[0.5],
            'lower': predictions[lower_q],
            'upper': predictions[upper_q]
        }
```

## 7. Model Selection Criteria

### Business-Focused Evaluation
```python
def business_model_evaluation(models, validation_data):
    """Evaluate models based on business requirements"""
    results = {}
    
    for name, model in models.items():
        # Accuracy metrics
        rmse = calculate_rmse(model, validation_data)
        
        # Computational efficiency
        inference_time = measure_inference_time(model, sample_data)
        
        # Uncertainty quality
        interval_coverage = calculate_interval_coverage(model, validation_data)
        
        # Business value
        forecast_value = calculate_forecast_value(model, validation_data)
        
        results[name] = {
            'rmse': rmse,
            'inference_time_ms': inference_time * 1000,
            'interval_coverage': interval_coverage,
            'annual_value_usd': forecast_value,
            'deployability_score': calculate_deployability(model)
        }
````
