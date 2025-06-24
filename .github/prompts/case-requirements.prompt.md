# Temus Case Study Requirements

## Core Deliverables
You must complete ALL the following components for submission:

### 1. Exploratory Data Analysis
- **Data quality assessment**: Missing values, outliers, temporal gaps
- **Feature-target relationships**: Wind speed-power curves, directional effects
- **Temporal patterns**: Hourly, daily, seasonal variations in wind generation
- **Cross-farm correlations**: Spatial dependencies between wind farms

### 2. Model Development
- **Multiple model approaches**: 
  - Baseline models (persistence, seasonal naive)
  - Machine learning models (Random Forest, XGBoost)
  - Deep learning models (LSTM, Transformer)
- **Performance comparison**: RMSE, MAE by forecast horizon
- **Model selection rationale**: Business context-driven choice

### 3. Model Risk Management
- **Uncertainty quantification**: Prediction intervals, confidence bounds
- **Performance monitoring strategy**: Real-time drift detection
- **Failure mode analysis**: Edge cases, graceful degradation
- **Validation framework**: Out-of-time testing, stress scenarios

### 4. MCP Service Deployment
- **RESTful API**: Standardized endpoints for predictions
- **Metadata tracking**: Dataset provenance, model versions
- **Real-time inference**: < 200ms response time target
- **Production monitoring**: Health checks, performance metrics

### 5. Business Presentation (45 minutes)
- **Problem identification**: Clear business case
- **Solution approach**: Technical methodology
- **Measurable impact metrics**: CO2 reduction, cost savings
- **Deployment roadmap**: Practical implementation plan

## Success Criteria
- **Forecast accuracy**: Improve upon persistence baseline by >30%
- **Benchmark performance**: Achieve competitive results vs. GEF2012 leaderboard
- **Consistent results**: Demonstrate stable performance across seasons
- **Service performance**: Response time < 200ms, 99.9% uptime
- **Environmental impact**: Quantified CO2 reduction potential
- **Innovation**: Creative approaches while maintaining rigor
- **Business relevance**: Clear path to real-world deployment

## Evaluation Focus Areas
1. **Technical depth**: ML modeling expertise
2. **Business acumen**: Understanding of energy sector challenges
3. **Production readiness**: Scalable, maintainable solutions
4. **Communication**: Clear presentation of complex concepts
5. **Innovation**: Novel approaches to sustainability challenges

## Timeline Expectations
- **EDA completion**: 2-3 days
- **Model development**: 3-4 days  
- **MCP service**: 2-3 days
- **Presentation prep**: 1-2 days
- **Total**: ~10 working days

Remember: This is a McKinsey case study - balance technical excellence with business pragmatism.
