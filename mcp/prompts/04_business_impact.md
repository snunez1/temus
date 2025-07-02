# Business Impact Calculation Guide

When calculating environmental and economic value:

## Key Parameters and Constants
- **CO2 Displacement**: 0.4-0.7 tons per MWh wind (use 0.5 tons/MWh as default)
- **Imbalance Cost**: $30-70 per MWh forecast error (use $50/MWh)
- **Grid Penetration**: Each 10% forecast accuracy improvement → 2% more renewables
- **Annual Hours**: 8,760 hours per year
- **Capacity Factor Baseline**: ~30% for wind farms

## Business Calculation Framework

### 1. Annual Generation Calculation
```
Annual_MWh = Installed_MW × Capacity_Factor × 8760_hours
```

### 2. Forecast Error Reduction
```
Error_Reduction_MWh = RMSE_improvement_% × Annual_MWh × Forecast_Update_Frequency
```

### 3. CO2 Savings
```
CO2_Savings_tons = Error_Reduction_MWh × 0.5_tons_per_MWh
```

### 4. Economic Value
```
Economic_Value = Error_Reduction_MWh × $50_imbalance_cost
```

## Find in Notebooks
- **Notebook 02_wind_physics_analysis.ipynb**: Initial business impact calculations and capacity factors
- **Notebook 12_business_impact.ipynb**: Comprehensive business analysis and presentation materials
- **Notebook 10_model_evaluation.ipynb**: Performance improvements for business case
- Look for sections on "BUSINESS IMPACT ANALYSIS" and "FORECAST IMPROVEMENT VALUE"

## Analysis Patterns to Look For
- `co2_displacement` calculations
- `economic_value` assessments  
- `grid_stability` improvements
- `renewable_penetration` increases
- `annual_generation` projections
- `cost_benefit` analysis

## McKinsey-Style Business Metrics

### Environmental Impact
- "X% accuracy improvement enables Y tons additional CO2 displacement annually"
- "Equivalent to removing Z cars from roads for one year"
- "Supports national decarbonization goals"

### Economic Value
- "$X million annual savings from reduced balancing costs"
- "Y% improvement in project IRR"
- "Z-year payback period for forecasting investment"

### Grid Integration Benefits
- "Enables X% higher renewable penetration"
- "Reduces need for Y MW fossil backup capacity"
- "Improves grid stability by Z%"

## Response Structure
1. **Quantified Impact**: Lead with specific numbers
2. **Calculation Method**: Show the methodology used
3. **Scaling Potential**: Project to fleet or national level
4. **Strategic Value**: Connect to sustainability goals
5. **Implementation Pathway**: Practical steps to realize benefits

## Confidence and Validation
- Reference peer-reviewed studies for CO2 factors
- Use conservative estimates for business case
- Note assumptions and sensitivity analysis
- Provide ranges rather than point estimates
