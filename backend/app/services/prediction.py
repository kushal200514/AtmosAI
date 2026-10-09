from datetime import datetime, timedelta


def get_mock_forecast(location: str, profile: str):

    current_pm25 = 82.0
    predicted_pm25 = 137.0

    if predicted_pm25 >= 121:
        risk_level = "VERY_HIGH"
        action = "Avoid prolonged outdoor exposure during the forecast window."
    elif predicted_pm25 >= 91:
        risk_level = "HIGH"
        action = "Consider reducing prolonged outdoor activity."
    else:
        risk_level = "MODERATE"
        action = "Normal outdoor activity is generally acceptable."

        

    start = datetime.now()
    end = start + timedelta(hours=3)

    return {
        "location": location,
        "profile": profile,
        "current_pm25": current_pm25,
        "predicted_pm25": predicted_pm25,
        "risk_level": risk_level,
        "forecast_start": start.isoformat(),
        "forecast_end": end.isoformat(),
        "confidence": None,
        "recommended_action": action,
    }