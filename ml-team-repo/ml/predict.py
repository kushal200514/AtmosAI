import os
import joblib
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
from features import FEATURE_COLUMNS

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "model.joblib")

class Predictor:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

    def _build_feature_row(self, raw_input: Dict[str, Any]) -> pd.DataFrame:
        """Constructs the complete 15-column vector required by LightGBM."""
        now = datetime.now()
        current_pm25 = float(raw_input.get("pm25_current", raw_input.get("pm25", 70.0)))
        trend = float(raw_input.get("pm25_trend_3h", 8.0))
        hour = raw_input.get("hour", now.hour)
        day_of_week = raw_input.get("day_of_week", now.weekday())

        row = {
            "pm25_current": current_pm25,
            "pm25_lag_1h": float(raw_input.get("pm25_lag_1h", current_pm25 - (trend / 3.0))),
            "pm25_lag_3h": float(raw_input.get("pm25_lag_3h", current_pm25 - trend)),
            "pm25_lag_6h": float(raw_input.get("pm25_lag_6h", max(20.0, current_pm25 - (trend * 1.5)))),
            "pm25_trend_3h": trend,
            "pm25_rolling_mean_6h": float(raw_input.get("pm25_rolling_mean_6h", current_pm25)),
            "temperature": float(raw_input.get("temperature", 26.0)),
            "humidity": float(raw_input.get("humidity", 65.0)),
            "wind_speed": float(raw_input.get("wind_speed", 2.0)),
            "wind_direction": float(raw_input.get("wind_direction", 180.0)),
            "hour": hour,
            "is_rush_hour": int((8 <= hour <= 11) or (17 <= hour <= 21)),
            "day_of_week": day_of_week,
            "is_weekend": int(day_of_week >= 5),
            "fire_count": int(raw_input.get("fire_count", 0))
        }

        # Guarantees exact column ordering and shape (1, 15)
        return pd.DataFrame([row])[FEATURE_COLUMNS]

    def predict(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        current_pm25 = float(feature_dict.get("pm25_current", feature_dict.get("pm25", 80.0)))
        wind_speed = float(feature_dict.get("wind_speed", 2.0))
        trend = float(feature_dict.get("pm25_trend_3h", 10.0))

        if self.model:
            df = self._build_feature_row(feature_dict)
            prob = float(self.model.predict_proba(df)[0][1])
        else:
            prob = min(0.95, max(0.1, (current_pm25 / 150.0) + (trend / 50.0)))

        now = datetime.now()
        start_hour = (now + timedelta(hours=3)).strftime("%H:00")
        end_hour = (now + timedelta(hours=6)).strftime("%H:00")

        projected_pm25 = round(current_pm25 + (trend * 1.4) + (12.0 if wind_speed < 2.0 else -4.0), 1)

        if projected_pm25 >= 121.0 or prob >= 0.80:
            risk = "VERY_HIGH"
        elif projected_pm25 >= 90.0 or prob >= 0.60:
            risk = "HIGH"
        elif projected_pm25 >= 60.0:
            risk = "MODERATE"
        else:
            risk = "LOW"

        return {
            "risk": risk,
            "probability": round(prob, 2),
            "predicted_pm25": projected_pm25,
            "forecast_window": f"{start_hour}-{end_hour}",
            "model_version": "lgbm-v1.0"
        }

predictor = Predictor()