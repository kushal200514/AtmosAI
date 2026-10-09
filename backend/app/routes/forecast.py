

from fastapi import APIRouter, HTTPException, Query

from app.schemas.forecast import ForecastResponse
from app.services.prediction import get_mock_forecast
from app.services.ml_predictor import predict_forecast
from app.services.forecast_pipeline import generate_live_forecast


# --------------------------------------------------
# Router configuration
# --------------------------------------------------

router = APIRouter(
    prefix="/forecast",
    tags=["Forecast"],
)


# --------------------------------------------------
# Existing mock forecast endpoint
# GET /api/forecast
# --------------------------------------------------

@router.get("", response_model=ForecastResponse)
def get_forecast(
    location: str = "bengaluru",
    profile: str = "general",
):
    """Return the existing mock forecast."""

    return get_mock_forecast(
        location=location,
        profile=profile,
    )


# --------------------------------------------------
# Existing ML prediction endpoint
# GET /api/forecast/predict
# --------------------------------------------------

@router.get("/predict")
def get_ml_forecast(
    pm25_current: float = Query(..., ge=0),
    pm25_lag_1h: float = Query(..., ge=0),
    pm25_lag_3h: float = Query(..., ge=0),
    pm25_lag_6h: float = Query(..., ge=0),
    pm25_rolling_mean_6h: float = Query(..., ge=0),
    temperature: float = Query(...),
    humidity: float = Query(..., ge=0, le=100),
    wind_speed: float = Query(..., ge=0),
    wind_direction: float = Query(..., ge=0, le=360),
    hour: int = Query(..., ge=0, le=23),
    day_of_week: int = Query(..., ge=0, le=6),
    fire_count: int = Query(default=0, ge=0),
):
    """Generate a prediction using the team's LightGBM model."""

    features = {
        "pm25_current": pm25_current,
        "pm25_lag_1h": pm25_lag_1h,
        "pm25_lag_3h": pm25_lag_3h,
        "pm25_lag_6h": pm25_lag_6h,
        "pm25_trend_3h": pm25_current - pm25_lag_3h,
        "pm25_rolling_mean_6h": pm25_rolling_mean_6h,
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "wind_direction": wind_direction,
        "hour": hour,
        "is_rush_hour": int(
            (8 <= hour <= 11) or (17 <= hour <= 21)
        ),
        "day_of_week": day_of_week,
        "is_weekend": int(day_of_week >= 5),
        "fire_count": fire_count,
    }

    try:
        result = predict_forecast(features)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="The ML forecast could not be generated.",
        ) from exc

    return {
        **result,
        "location": "bengaluru",
        "profile": "general",
        "prediction_source": "Person 3 LightGBM model",
        "features_used": features,
    }


# --------------------------------------------------
# Live telemetry endpoint
# GET /api/forecast/live
# --------------------------------------------------

