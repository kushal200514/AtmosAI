
import httpx
from datetime import datetime
from zoneinfo import ZoneInfo


LOCATIONS = {
    "peenya": {"lat": 13.0285, "lon": 77.5197},
    "silk_board": {"lat": 12.9172, "lon": 77.6228},
    "yelahanka": {"lat": 13.1007, "lon": 77.5963},
}


async def fetch_current_telemetry(location_id: str) -> dict:
    """Fetch current air-quality and weather data plus hourly PM2.5."""

    if location_id not in LOCATIONS:
        raise ValueError(f"Unsupported location: {location_id}")

    coords = LOCATIONS[location_id]

    air_quality_url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={coords['lat']}&longitude={coords['lon']}"
        "&current=pm2_5,pm10"
        "&hourly=pm2_5"
        "&timezone=Asia%2FKolkata"
        "&past_days=2"
        "&forecast_days=1"
    )

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={coords['lat']}&longitude={coords['lon']}"
        "&current=temperature_2m,relative_humidity_2m,"
        "wind_speed_10m,wind_direction_10m"
        "&timezone=Asia%2FKolkata"
    )

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            aq_res = await client.get(air_quality_url)
            aq_res.raise_for_status()

            weather_res = await client.get(weather_url)
            weather_res.raise_for_status()

            aq_json = aq_res.json()
            weather_json = weather_res.json()

            aq_current = aq_json.get("current", {})
            aq_hourly = aq_json.get("hourly", {})
            weather_current = weather_json.get("current", {})

            if aq_current.get("pm2_5") is None:
                raise ValueError("Current PM2.5 is unavailable.")

            if not aq_hourly.get("time") or not aq_hourly.get("pm2_5"):
                raise ValueError("Hourly PM2.5 history is unavailable.")

            if len(aq_hourly["time"]) != len(aq_hourly["pm2_5"]):
                raise ValueError("Hourly timestamps and PM2.5 values do not match.")

            hourly_observations = [
                {
                    "timestamp": timestamp,
                    "pm25": float(value),
                }
                for timestamp, value in zip(
                    aq_hourly["time"],
                    aq_hourly["pm2_5"],
                )
                if value is not None
            ]

            return {
                "location": location_id,
                "timestamp": datetime.now(
                    ZoneInfo("Asia/Kolkata")
                ).isoformat(),
                "pm25": float(aq_current["pm2_5"]),
                "pm10": (
                    float(aq_current["pm10"])
                    if aq_current.get("pm10") is not None
                    else None
                ),
                "temperature": weather_current.get("temperature_2m"),
                "humidity": weather_current.get("relative_humidity_2m"),
                "wind_speed": weather_current.get("wind_speed_10m"),
                "wind_direction": weather_current.get("wind_direction_10m"),
                "source": "Open-Meteo",
                "hourly_source": "Open-Meteo modelled hourly data",
                "hourly_timestamps": [
                    item["timestamp"] for item in hourly_observations
                ],
                "hourly_pm25": [
                    item["pm25"] for item in hourly_observations
                ],
                "hourly_observations": hourly_observations,
            }

        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            raise RuntimeError(
                f"Unable to retrieve valid telemetry for {location_id}: {exc}"
            ) from exc
