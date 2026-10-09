
import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.ml_predictor import predict_forecast
from app.services.historical_features import build_hourly_features


ML_ROOT = Path(r"D:\AtmosAi\ml-team-repo\ml")

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from ingest import fetch_current_telemetry


IST = ZoneInfo("Asia/Kolkata")


async def generate_live_forecast(location: str) -> dict:
    """Build all 15 model features and generate a live forecast."""

    telemetry = await fetch_current_telemetry(location)

    historical_features = build_hourly_features(
        telemetry["hourly_observations"]
    )

    now = datetime.now(IST)
    hour = now.hour
    day_of_week = now.weekday()

    required_weather = [
        "temperature",
        "humidity",
        "wind_speed",
        "wind_direction",
    ]

    missing_weather = [
        key
        for key in required_weather
        if telemetry.get(key) is None
    ]

    if missing_weather:
        raise ValueError(
            "Missing current weather features: "
            + ", ".join(missing_weather)
        )

    features = {
        **historical_features,
        "temperature": float(telemetry["temperature"]),
        "humidity": float(telemetry["humidity"]),
        "wind_speed": float(telemetry["wind_speed"]),
        "wind_direction": float(telemetry["wind_direction"]),
        "hour": hour,
        "is_rush_hour": int(
            (8 <= hour <= 11) or (17 <= hour <= 21)
        ),
        "day_of_week": day_of_week,
        "is_weekend": int(day_of_week >= 5),
        "fire_count": 0,
    }

    expected_features = [
        "pm25_current",
        "pm25_lag_1h",
        "pm25_lag_3h",
        "pm25_lag_6h",
        "pm25_trend_3h",
        "pm25_rolling_mean_6h",
        "temperature",
        "humidity",
        "wind_speed",
        "wind_direction",
        "hour",
        "is_rush_hour",
        "day_of_week",
        "is_weekend",
        "fire_count",
    ]

    if set(features) != set(expected_features):
        raise ValueError("The generated model features do not match.")

    result = predict_forecast(features)

    return {
        **result,
        "location": location,
        "prediction_source": "LightGBM",
        "telemetry_source": telemetry["source"],
        "historical_data_source": telemetry["hourly_source"],
        "features_used": features,
    }
