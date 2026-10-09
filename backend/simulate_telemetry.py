
import random
import time
from datetime import datetime, timezone

import requests


API_URL = "http://127.0.0.1:8000/api/telemetry"
NODE_ID = "simulator-001"
INTERVAL_SECONDS = 10


def generate_reading():
    """Generate sample data for development and testing."""
    return {
        "node_id": NODE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pm25": round(random.uniform(15, 120), 2),
        "pm10": round(random.uniform(25, 180), 2),
        "temperature": round(random.uniform(24, 36), 1),
        "humidity": round(random.uniform(35, 90), 1),
    }


def main():
    print("AtmosAI Telemetry Simulator")
    print(f"Sending readings to: {API_URL}")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            reading = generate_reading()

            try:
                response = requests.post(
                    API_URL,
                    json=reading,
                    timeout=10,
                )
                response.raise_for_status()

                print(
                    f"[SAVED] {reading['timestamp']} | "
                    f"PM2.5: {reading['pm25']} | "
                    f"PM10: {reading['pm10']}"
                )

            except requests.RequestException as exc:
                print(f"[ERROR] Could not send reading: {exc}")

            time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")


if __name__ == "__main__":
    main()
