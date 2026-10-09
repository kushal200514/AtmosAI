# 🌍 AtmosAi
**Built by Team TechinX for AWS Environmental Hacks 2026**

AtmosAi is an intelligent environmental early-warning system designed to predict localized air quality surges. By combining live telemetry, machine learning, and generative AI, AtmosAi moves beyond simple pollution indices to deliver contextual, location-specific mitigation actions for vulnerable demographics.

## 🚀 Features
*   **Predictive Intelligence:** Evaluates rolling 3-hour meteorological and PM2.5 trends to predict severe pollution events using LightGBM.
*   **Actionable AI:** Utilizes Anthropic Claude Sonnet 5 via AWS Bedrock to translate risk vectors into targeted, demographic-specific advice.
*   **Live Data Pipeline:** Integrates seamlessly with Open-Meteo and OpenAQ for real-time environmental context.
*   **FastAPI Backend:** A robust, modular web API handling route definitions, DynamoDB integration, and machine learning orchestration.
*   **IoT Hardware Simulation:** Includes a custom MQTT simulator to broadcast diurnal pollution patterns, mimicking hardware nodes deployed across Bengaluru.

## 📂 Repository Structure

```text
AtmosAi/
├── backend/                  # FastAPI web server and API layer
│   ├── app/
│   │   ├── routes/           # Endpoints (forecast.py, telemetry.py, alerts.py)
│   │   ├── schemas/          # Pydantic data validation models
│   │   ├── services/         # Business logic (dynamodb.py, ml_predictor.py)
│   │   ├── config.py         # Environment configurations
│   │   └── main.py           # Application entry point
│   ├── Dockerfile            # Containerization for deployment
│   ├── requirements.txt      # Backend dependencies
│   └── simulate_telemetry.py # Backend test script
│
├── ml-team-repo/             # Core Machine Learning & AI Intelligence Engine
│   ├── ml/
│   │   ├── models/           
│   │   │   └── model.joblib  # Trained LightGBM artifact
│   │   ├── accuracy.json     # Backtesting evaluation metrics
│   │   ├── bedrock_service.py# Claude Sonnet 5 integration & fallback templates
│   │   ├── features.py       # Data schema and feature engineering
│   │   ├── ingest.py         # Open-Meteo / OpenAQ API data fetcher
│   │   ├── predict.py        # ML inference engine
│   │   └── train.py          # Pipeline training script
│   └── simulator/
│       └── sensor_simulator.py # MQTT IoT data broadcast script (Dry-run capable)
│
└── frontend/                
⚙️ Getting Started
1. Run the Backend API
Navigate to the backend directory and start the FastAPI server:

Bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
The API will be available at http://localhost:8000. View the Swagger documentation at http://localhost:8000/docs.

2. AWS Credentials (For Bedrock AI)
To enable the Claude 3.5 Sonnet explanations, ensure your local environment has AWS credentials configured:

Bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-east-1"
3. Run the IoT Simulator
To simulate live hardware sensors broadcasting localized Bengaluru telemetry:

Bash
cd ml-team-repo
python simulator/sensor_simulator.py
👥 Team TechinX
Krishna: 
