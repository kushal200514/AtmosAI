import sys
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.dynamodb import get_telemetry_table


router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"],
)


class TelemetryCreate(BaseModel):
    node_id: str = Field(..., min_length=1, max_length=100)
    timestamp: datetime
    pm25: float = Field(..., ge=0)
    pm10: float = Field(..., ge=0)
    temperature: Optional[float] = None
    humidity: Optional[float] = Field(default=None, ge=0, le=100)


@router.post("")
def create_telemetry(data: TelemetryCreate):
    """Save an air-quality reading to DynamoDB."""

    table = get_telemetry_table()

    if table is None:
        raise HTTPException(
            status_code=503,
            detail="DynamoDB is disabled or unavailable.",
        )

    timestamp = data.timestamp

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    item = {
        "node_id": data.node_id,
        "timestamp": timestamp.isoformat(),
        "pm25": Decimal(str(data.pm25)),
        "pm10": Decimal(str(data.pm10)),
    }

    if data.temperature is not None:
        item["temperature"] = Decimal(str(data.temperature))

    if data.humidity is not None:
        item["humidity"] = Decimal(str(data.humidity))

    try:
        table.put_item(Item=item)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to save telemetry to DynamoDB.",
        ) from exc

    return {
        "status": "success",
        "saved": True,
        "node_id": data.node_id,
        "timestamp": timestamp.isoformat(),
        "message": "Telemetry saved successfully.",
    }

@router.get("/{node_id}")
def get_telemetry(
    node_id: str,
    limit: int = Query(default=10, ge=1, le=100),
):
    """Retrieve telemetry readings for a sensor."""

    table = get_telemetry_table()

    if table is None:
        raise HTTPException(
            status_code=503,
            detail="DynamoDB is disabled or unavailable.",
        )

    try:
        response = table.query(
            KeyConditionExpression="node_id = :node",
            ExpressionAttributeValues={
                ":node": node_id,
            },
            ScanIndexForward=False,
            Limit=limit,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve telemetry from DynamoDB.",
        ) from exc

    readings = response.get("Items", [])

    return {
        "node_id": node_id,
        "count": len(readings),
        "readings": readings,
    }
# Connect to Person 3's ML repository ingestion module.
ML_ROOT = Path(r"D:\AtmosAi\ml-team-repo\ml")

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from ingest import fetch_current_telemetry


@router.get("/live")
async def get_live_telemetry(
    location: str = Query(default="yelahanka"),
):
    """Fetch current air-quality and weather data."""

    allowed_locations = {"peenya", "silk_board", "yelahanka"}

    if location not in allowed_locations:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported location. Choose from: {sorted(allowed_locations)}",
        )

    data = await fetch_current_telemetry(location)

    return {
        "location": location,
        **data,
    }