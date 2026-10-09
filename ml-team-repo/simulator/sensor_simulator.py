import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

# --- AWS IoT Core Configuration ---
# Person 2 will fill these in after creating the "Thing" in AWS
AWS_ENDPOINT = "YOUR_ENDPOINT-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "breatheahead-simulator"
TOPIC = "breatheahead/telemetry"

# Paths to the AWS X.509 certificates (Provided by Person 2 later)
PATH_TO_CERT = "certs/certificate.pem.crt"
PATH_TO_KEY = "certs/private.pem.key"
PATH_TO_ROOT = "certs/AmazonRootCA1.pem"

LOCATIONS = ["peenya", "silk_board", "yelahanka"]

def generate_telemetry(location_id: str) -> dict:
    """Simulates realistic telemetry with diurnal rush-hour surges for testing."""
    hour = datetime.now().hour
    
    # Baseline pollution
    base_pm25 = 45.0 + random.uniform(-5.0, 5.0)
    
    # Rush hour surge simulation (Bengaluru traffic patterns)
    if (8 <= hour <= 11) or (17 <= hour <= 21):
        base_pm25 += random.uniform(25.0, 45.0)
        
    # Peenya industrial penalty
    if location_id == "peenya":
        base_pm25 += 15.0
        
    return {
        "node": location_id,
        "timestamp": datetime.now().isoformat(),
        "pm25_current": round(base_pm25, 1),
        "temperature": round(25.0 + random.uniform(-2, 2), 1),
        "humidity": round(60.0 + random.uniform(-10, 10), 1),
        "wind_speed": round(random.uniform(0.5, 3.5), 1),
        "wind_direction": random.randint(0, 360),
        "pm25_trend_3h": round(random.uniform(5.0, 15.0), 1) # Simulated rolling trend
    }

def main():
    print("🚀 Initializing BreatheAhead IoT Sensor Simulator...")
    
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, CLIENT_ID)
    aws_connected = False
    
    try:
        # Attempt secure AWS IoT Core connection
        client.tls_set(ca_certs=PATH_TO_ROOT, certfile=PATH_TO_CERT, keyfile=PATH_TO_KEY)
        client.connect(AWS_ENDPOINT, 8883, 60)
        client.loop_start()
        aws_connected = True
        print(f"✅ Connected securely to AWS IoT Core at {AWS_ENDPOINT}")
    except Exception:
        print("⚠️  AWS IoT Certificates not found or missing endpoint.")
        print("💡 Running in LOCAL DRY-RUN MODE. Hand off to Person 2 to add certificates.\n")

    try:
        while True:
            for loc in LOCATIONS:
                payload = generate_telemetry(loc)
                json_payload = json.dumps(payload)
                
                if aws_connected:
                    client.publish(TOPIC, json_payload, qos=1)
                    print(f"📡 Published to {TOPIC} [{loc}]: PM2.5 = {payload['pm25_current']}")
                else:
                    print(f"💻 [DRY RUN] Would publish -> {loc}: PM2.5 = {payload['pm25_current']}")
                    
                time.sleep(1.5) # Stagger transmissions
            
            print("⏳ Waiting 10 seconds for next sensor polling cycle...\n")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped.")
        if aws_connected:
            client.loop_stop()
            client.disconnect()

if __name__ == "__main__":
    main()