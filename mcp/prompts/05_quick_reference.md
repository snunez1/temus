# Quick Reference Analysis Guide

For general queries and overview questions:

## Common Query Types and Locations

### Performance Overview
- **"What's the best model?"** → notebook 10, model comparison section
- **"How accurate are forecasts?"** → notebook 10, RMSE results
- **"Improvement over baseline?"** → notebook 06 vs 10 comparison

### Physical Characteristics  
- **"Capacity factors by farm?"** → notebook 02, summary statistics
- **"Power curve parameters?"** → notebook 02, curve fitting results
- **"Wind resource quality?"** → notebook 02, capacity factor analysis

### Business Value
- **"CO2 impact?"** → notebook 12, environmental calculations
- **"Economic benefits?"** → notebook 12, cost-benefit analysis
- **"Grid integration value?"** → notebook 12, penetration analysis

### Data Quality
- **"Data completeness?"** → notebook 01, missing value analysis
- **"Outlier detection?"** → notebook 01, data quality assessment
- **"Temporal coverage?"** → notebook 01, time series overview

## Key Project Constants
- **Training Period**: July 2009 - December 2010 (18 months)
- **Wind Farms**: 7 farms (wf1-wf7)
- **Forecast Horizons**: 1-48 hours ahead
- **Update Frequency**: Every 6 hours
- **Target Improvement**: >30% over persistence baseline
- **Deployment Target**: <200ms response time

## Standard Response Template
```
Based on [notebook X, section Y]:

**Finding**: [Specific metric/result]
**Context**: [Why this matters]
**Source**: [Notebook location]
**Confidence**: [High/Medium/Low based on validation]
**Business Relevance**: [Connection to sustainability goals]
```

## Escalation Patterns
If query is complex or multi-faceted:
1. **Break down** into component questions
2. **Route** to specific analysis prompts
3. **Synthesize** results into coherent response
4. **Highlight** key business implications
