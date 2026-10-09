from pydantic import BaseModel
from typing import Optional


class ForecastResponse(BaseModel):
    location: str
    profile: str

    current_pm25: float
    predicted_pm25: float

    risk_level: str

    forecast_start: str
    forecast_end: str

    confidence: Optional[float] = None

    recommended_action: str