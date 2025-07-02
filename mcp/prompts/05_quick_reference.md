# Quick Reference Analysis Guide

For general queries and overview questions:

## Common Query Types and Locations

### Performance Overview
- **"What's the best model?"** → notebooks 07-10, model comparison sections
- **"How accurate are forecasts?"** → notebooks 06-10, RMSE results
- **"Improvement over baseline?"** → notebook 06 baseline establishment, then 07-10 comparisons

### Physical Characteristics  
- **"Capacity factors by farm?"** → notebook 02, summary statistics
- **"Power curve parameters?"** → notebook 02, curve fitting results
- **"Wind resource quality?"** → notebook 02, capacity factor analysis

### Business Value
- **"CO2 impact?"** → notebook 02 initial calculations, notebook 12 comprehensive analysis
- **"Economic benefits?"** → notebook 02 forecast improvement value, notebook 12 detailed cost-benefit
- **"Grid integration value?"** → notebook 12, penetration analysis

### Data Quality
- **"Data completeness?"** → notebook 01, missing value analysis
- **"Outlier detection?"** → notebook 01, data quality assessment
- **"Temporal coverage?"** → notebook 01, time series overview

## Key Project Constants
- **Training Period**: July 2009 - June 2012 (Training: 2009-2010, Test: 2011-2012)
- **Wind Farms**: 7 farms (wp1-wp7, also referenced as wf1-wf7)
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
