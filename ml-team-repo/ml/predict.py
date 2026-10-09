import os
import joblib
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "model.joblib")

class Predictor:
    def __init__(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            self.model = None

    def predict(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates risk classification and trajectory from feature vector.
        Follows the strict ML -> Backend interface specification.
        """
        current_pm25 = float(feature_dict.get("pm25_current", 80.0))
        wind_speed = float(feature_dict.get("wind_speed", 2.0))
        trend = float(feature_dict.get("pm25_trend_3h", 10.0))

        if self.model:
            df = pd.DataFrame([feature_dict])
            prob = float(self.model.predict_proba(df)[0][1])
        else:
            # Deterministic mathematical fallback
            prob = min(0.95, max(0.1, (current_pm25 / 150.0) + (trend / 50.0)))

        # Forecast window calculations
        now = datetime.now()
        start_hour = (now + timedelta(hours=3)).strftime("%H:00")
        end_hour = (now + timedelta(hours=6)).strftime("%H:00")

        # Projected peak PM2.5 calculation
        projected_pm25 = round(current_pm25 + (trend * 1.5) + (15.0 if wind_speed < 2.0 else -5.0), 1)

        # Categorize risk levels
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