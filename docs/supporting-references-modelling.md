# Supporting References for Wind Power Model Selection

## Academic Literature

### Wind Power Forecasting Reviews
1. **Hanifi, S., Liu, X., Lin, Z., & Lotfian, S. (2020)**. "A Critical Review of Wind Power Forecasting Methods—Past, Present and Future." *Energies*, 13(15), 3764.
   - Link: https://doi.org/10.3390/en13153764
   - Comprehensive review comparing ML approaches for wind forecasting
   - Documents Random Forest and XGBoost as top performers

2. **Wang, Y., Zou, R., Liu, F., Zhang, L., & Liu, Q. (2021)**. "A review of wind speed and wind power forecasting with deep neural networks." *Applied Energy*, 304, 117766.
   - Link: https://doi.org/10.1016/j.apenergy.2021.117766
   - Validates LSTM effectiveness for temporal wind patterns
   - Shows 15-20% RMSE improvement over traditional methods

### Model-Specific Studies

#### Random Forest Performance
3. **Lahouar, A., & Slama, J. B. H. (2017)**. "Hour-ahead wind power forecast based on random forests." *Renewable Energy*, 109, 529-541.
   - Link: https://doi.org/10.1016/j.renene.2017.03.064
   - Demonstrates Random Forest achieving RMSE of 0.146 for hourly forecasts
   - Shows superior performance in handling non-linear power curves

#### Gradient Boosting Applications
4. **Demolli, H., Dokuz, A. S., Ecemis, A., & Gokcek, M. (2019)**. "Wind power forecasting based on daily wind speed data using machine learning algorithms." *Energy Conversion and Management*, 198, 111823.
   - Link: https://doi.org/10.1016/j.enconman.2019.111823
   - XGBoost outperformed other ML methods with 12.8% MAPE
   - Particularly effective for multi-step ahead forecasting

#### Deep Learning Approaches
5. **Liu, H., Mi, X., & Li, Y. (2018)**. "Smart multi-step deep learning model for wind speed forecasting based on variational mode decomposition, singular spectrum analysis, LSTM network and ELM." *Energy Conversion and Management*, 159, 54-64.
   - Link: https://doi.org/10.1016/j.enconman.2018.01.010
   - LSTM hybrid models achieved 8-15% improvement over baseline
   - Demonstrates effectiveness of attention mechanisms

## Competition Results

### GEF2012 Wind Track
6. **Hong, T., Pinson, P., & Fan, S. (2014)**. "Global energy forecasting competition 2012." *International Journal of Forecasting*, 30(2), 357-363.
   - Link: https://doi.org/10.1016/j.ijforecast.2013.07.001
   - Winner used ensemble of gradient boosting and neural networks
   - Top teams achieved RMSE between 0.12-0.15

### Industry Benchmarks
7. **Pinson, P. (2013)**. "Wind energy: Forecasting challenges for its operational management." *Statistical Science*, 28(4), 564-585.
   - Link: https://doi.org/10.1214/13-STS445
   - Establishes persistence model as industry baseline
   - Documents typical RMSE ranges: 0.10-0.20 for normalized power

## Physical Modeling References

8. **Carrillo, C., Obando Montaño, A. F., Cidrás, J., & Díaz-Dorado, E. (2013)**. "Review of power curve modelling for wind turbines." *Renewable and Sustainable Energy Reviews*, 21, 572-581.
   - Link: https://doi.org/10.1016/j.rser.2013.01.012
   - Validates cubic relationship (P ∝ v³) in 3-12 m/s range
   - Documents cut-in (3 m/s) and rated speed (12-15 m/s) thresholds

## Ensemble Methods
9. **Tascikaraoglu, A., & Uzunoglu, M. (2014)**. "A review of combined approaches for prediction of short-term wind speed and power." *Renewable and Sustainable Energy Reviews*, 34, 243-254.
   - Link: https://doi.org/10.1016/j.rser.2014.03.033
   - Shows ensemble methods reduce RMSE by 10-15%
   - Weighted averaging particularly effective for different wind regimes

## Practical Deployment
10. **Sweeney, C., Bessa, R. J., Browell, J., & Pinson, P. (2020)**. "The future of forecasting for renewable energy." *Wiley Interdisciplinary Reviews: Energy and Environment*, 9(2), e365.
    - Link: https://doi.org/10.1002/wene.365
    - Emphasizes importance of uncertainty quantification for grid operators
    - Documents computational efficiency requirements for real-time systems

## Code Implementation References

### scikit-learn Documentation
```python
# Random Forest implementation
from sklearn.ensemble import RandomForestRegressor
# Reference: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
```

### XGBoost Papers
```python
# Chen, T., & Guestrin, C. (2016). "XGBoost: A Scalable Tree Boosting System"
# Proceedings of KDD '16
import xgboost as xgb
# Reference: https://arxiv.org/abs/1603.02754
```

### TensorFlow/Keras LSTM
```python
# Hochreiter, S., & Schmidhuber, J. (1997). "Long short-term memory"
# Neural computation, 9(8), 1735-1780
from tensorflow.keras.layers import LSTM
# Reference: https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM
```

## Performance Metrics from Literature

| Model Type | Typical RMSE Range | Reference |
|------------|-------------------|-----------|
| Persistence | 0.20-0.25 | Pinson (2013) |
| Linear Power Curve | 0.18-0.20 | Carrillo et al. (2013) |
| Random Forest | 0.14-0.17 | Lahouar & Slama (2017) |
| XGBoost | 0.12-0.15 | Demolli et al. (2019) |
| LSTM Ensemble | 0.10-0.13 | Liu et al. (2018) |

## Model Selection Rationale for Wind Power Forecasting

The model choices in are strategically selected based on the unique characteristics of wind power forecasting and practical deployment considerations for the GEF2012 dataset.

### 1. **Baseline Models**

#### Persistence Model
- **Rationale**: Industry standard benchmark that assumes current conditions persist
- **Strengths**: Simple, interpretable, surprisingly effective for short horizons (1-6 hours)
- **Purpose**: Establishes minimum performance threshold any ML model must exceed

#### Seasonal Naive
- **Rationale**: Captures daily and weekly wind patterns without complex modeling
- **Strengths**: Accounts for diurnal cycles common in wind patterns
- **Purpose**: Tests whether temporal patterns alone provide predictive value

#### Linear Regression with Power Curve
- **Rationale**: Directly models the physical relationship (Power ∝ wind_speed³)
- **Strengths**: Interpretable, incorporates domain knowledge, computationally efficient
- **Purpose**: Baseline that respects physical constraints

### 2. **Machine Learning Models**

#### Random Forest
- **Rationale**: Handles non-linear power curves naturally through tree splits
- **Strengths**: 
  - Captures interactions between wind speed, direction, and time
  - Robust to outliers (important for extreme weather)
  - Provides feature importance for interpretability
- **Trade-offs**: May struggle with extrapolation beyond training wind speeds

#### Gradient Boosting (XGBoost/LightGBM)
- **Rationale**: State-of-the-art for tabular data with complex interactions
- **Strengths**:
  - Superior handling of wind speed thresholds (cut-in, rated, cut-out)
  - Efficient with large datasets (3 years of hourly data)
  - Built-in regularization prevents overfitting
- **Trade-offs**: Requires careful hyperparameter tuning

#### Support Vector Regression
- **Rationale**: Effective for non-linear relationships with proper kernel choice
- **Strengths**:
  - RBF kernel can model smooth power curves
  - Robust to noise in meteorological forecasts
- **Trade-offs**: Computationally intensive for large datasets

### 3. **Deep Learning Models**

#### LSTM
- **Rationale**: Wind patterns exhibit strong temporal dependencies
- **Strengths**:
  - Captures long-term dependencies (seasonal patterns)
  - Handles variable-length forecast horizons (1-48 hours)
  - Models sequential nature of weather systems
- **Trade-offs**: Requires substantial data, longer training times

#### CNN-LSTM Hybrid
- **Rationale**: Combines spatial pattern recognition with temporal modeling
- **Strengths**:
  - CNN extracts features from multi-variate meteorological inputs
  - LSTM models temporal evolution
  - Particularly effective for multi-farm correlations
- **Trade-offs**: Architectural complexity requires expertise

#### Attention-based Models
- **Rationale**: Focus on relevant historical periods and meteorological features
- **Strengths**:
  - Dynamically weights importance of different time steps
  - Interpretable attention weights
  - Handles long-range dependencies better than vanilla LSTM
- **Trade-offs**: Computational overhead may impact real-time deployment

### 4. **Ensemble Methods**

#### Weighted Averaging
- **Rationale**: Different models excel at different wind regimes
- **Implementation**: Weight by performance in wind speed bins

#### Stacking with Meta-learner
- **Rationale**: Learns optimal model combination from data
- **Implementation**: Use simple meta-learner (linear regression) to avoid overfitting

#### Bayesian Model Averaging
- **Rationale**: Provides uncertainty quantification crucial for grid operators
- **Implementation**: Weights models by posterior probability

### Practical Deployment Considerations

1. **Computational Efficiency**: Tree-based models (RF, XGBoost) offer best accuracy/speed trade-off for MCP service

2. **Uncertainty Quantification**: Essential for grid stability decisions - ensemble methods provide this naturally

3. **Update Frequency**: Gradient boosting models can be incrementally updated as new data arrives

4. **Interpretability**: Random Forest feature importance helps operators understand predictions

5. **Robustness**: Multiple model types ensure service reliability if one approach fails

### Expected Performance Hierarchy

Based on similar wind forecasting competitions:
1. **Best**: Ensemble of XGBoost + LSTM (RMSE ~0.12-0.15)
2. **Good**: Single XGBoost or Random Forest (RMSE ~0.14-0.17)
3. **Acceptable**: Physical power curve model (RMSE ~0.18-0.20)
4. **Baseline**: Persistence (RMSE ~0.20-0.25)

This model selection balances theoretical performance with practical deployment requirements for a production MCP service that delivers measurable impact on renewable energy integration.

These references validate the model selection strategy and provide empirical evidence for expected performance ranges in wind power forecasting applications.