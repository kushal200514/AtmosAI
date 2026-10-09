
from datetime import datetime

from pydantic import BaseModel, Field


class TelemetryCreate(BaseModel):
    node_id: str = Field(min_length=1, max_length=100)
    timestamp: datetime
    pm25: float = Field(ge=0, le=2000)
    pm10: float | None = Field(default=None, ge=0, le=2000)
    temperature: float | None = Field(default=None, ge=-80, le=80)
    humidity: float | None = Field(default=None, ge=0, le=100)


class TelemetryResponse(BaseModel):
    message: str
    saved: bool
    node_id: str
    timestamp: str
