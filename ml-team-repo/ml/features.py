import pandas as pd
import numpy as np
from datetime import datetime

# Mandatory feature columns for LightGBM training and inference
FEATURE_COLUMNS = [
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
    "fire_count"
]

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms raw time-series into ML-ready features.
    Input df must contain: ['timestamp', 'pm25', 'temperature', 'humidity', 'wind_speed', 'wind_direction']
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # 1. Pollution Lags & Rolling Trends
    df["pm25_current"] = df["pm25"]
    df["pm25_lag_1h"] = df["pm25"].shift(1)
    df["pm25_lag_3h"] = df["pm25"].shift(3)
    df["pm25_lag_6h"] = df["pm25"].shift(6)
    
    # Rate of change over 3 hours
    df["pm25_trend_3h"] = df["pm25_current"] - df["pm25_lag_3h"]
    df["pm25_rolling_mean_6h"] = df["pm25"].rolling(window=6, min_periods=1).mean()

    # 2. Time & Calendar Context (Bengaluru IST Traffic Patterns)
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].apply(lambda d: 1 if d >= 5 else 0)
    # Peak traffic windows: 08:30-11:30 and 17:30-21:00
    df["is_rush_hour"] = df["hour"].apply(lambda h: 1 if (8 <= h <= 11) or (17 <= h <= 21) else 0)

    # 3. Environmental Fallbacks (FIRMS)
    if "fire_count" not in df.columns:
        df["fire_count"] = 0

    # Clean initial shifted rows
    df = df.bfill().ffill()
    return df