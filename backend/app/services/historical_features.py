
from datetime import datetime, timedelta
from statistics import mean
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")


def build_hourly_features(hourly_observations: list[dict]) -> dict:
    """
    Build PM2.5 history features from timestamped hourly observations.

    Only observations at or before the current hour are used.
    Missing historical hours cause an error rather than being fabricated.
    """

    if not hourly_observations:
        raise ValueError("No hourly PM2.5 observations were provided.")

    hourly_pm25 = {}

    for item in hourly_observations:
        timestamp_text = item.get("timestamp")
        value = item.get("pm25")

        if timestamp_text is None or value is None:
            continue

        timestamp = datetime.fromisoformat(timestamp_text)

        # Open-Meteo timestamps use local time when timezone is requested.
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=IST)
        else:
            timestamp = timestamp.astimezone(IST)

        hour_start = timestamp.replace(
            minute=0, second=0, microsecond=0
        )

        hourly_pm25[hour_start] = float(value)

    if not hourly_pm25:
        raise ValueError("No valid hourly PM2.5 observations were found.")

    now = datetime.now(IST)
    current_hour = now.replace(minute=0, second=0, microsecond=0)

    # Ignore future forecast hours.
    hourly_pm25 = {
        timestamp: value
        for timestamp, value in hourly_pm25.items()
        if timestamp <= current_hour
    }

    required_hours = [
        current_hour - timedelta(hours=offset)
        for offset in range(7)
    ]

    missing_hours = [
        timestamp.isoformat()
        for timestamp in required_hours
        if timestamp not in hourly_pm25
    ]

    if missing_hours:
        raise ValueError(
            "Insufficient hourly PM2.5 history. Missing hours: "
            + ", ".join(missing_hours)
        )

    current = hourly_pm25[required_hours[0]]
    lag_1h = hourly_pm25[required_hours[1]]
    lag_3h = hourly_pm25[required_hours[3]]
    lag_6h = hourly_pm25[required_hours[6]]

    rolling_values = [
        hourly_pm25[required_hours[offset]]
        for offset in range(6)
    ]

    return {
        "pm25_current": current,
        "pm25_lag_1h": lag_1h,
        "pm25_lag_3h": lag_3h,
        "pm25_lag_6h": lag_6h,
        "pm25_trend_3h": current - lag_3h,
        "pm25_rolling_mean_6h": mean(rolling_values),
    }
