# MCP Service Implementation Guide

Build a production-ready MCP service with these components:

## 1. Service Architecture
```python
# FastAPI-based service structure:
# - /predict - Wind power predictions
# - /metadata - Dataset and model information
# - /health - Service health check
# - /metrics - Performance monitoring
```

## 2. Request/Response Schema
```python
# Design schema after model finalization:
# - Include only features used by final model
# - Support model versioning for schema evolution
# - Provide feature discovery endpoint

# Example request (to be refined based on final model):
{
    "farm_id": "wf1",
    "forecast_horizon": 48,
    "features": {
        # Only include features required by deployed model
        "weather": {
            "wind_speed": [...],
            "wind_direction": [...]
        },
        "temporal": {
            "timestamp": "2024-01-01T00:00:00Z"
        },
        # Additional features based on model requirements
    }
}

# Example response:
{
    "predictions": [...],
    "uncertainty_bounds": {"lower": [...], "upper": [...]},
    "metadata": {
        "model_version": "1.0",
        "computation_time_ms": 150,
        "feature_importance": {
            # Dynamic based on model
        }
    }
}
```

## 3. Features API Endpoint
```python
# Add a features endpoint to dynamically discover required inputs
@app.get("/features")
def get_features():
    return {
        "required_features": model.get_feature_names(),
        "optional_features": [...],
        "feature_constraints": {...},
        "examples": [...]
    }
```

## 4. Metadata Requirements
- Dataset provenance (source, date range, quality metrics)
- Model information (type, training date, performance)
- Feature importance rankings
- Update frequency and last refresh time

## 5. Production Considerations
- Model versioning and A/B testing
- Request caching for efficiency
- Logging and monitoring
- Graceful degradation strategies

## 6. Environmental Impact Metrics
- CO2 savings from improved forecasts
- Grid stability improvement metrics
- Renewable integration capacity increase
