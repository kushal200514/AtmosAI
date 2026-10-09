# AtmosAi (BreatheAhead) - ML Team Service

An AI-driven air quality forecasting, explainability, and IoT telemetry early-warning system.

## 🌟 Overview
AtmosAi combines machine learning (LightGBM), real-time weather and pollution telemetry ingestion, AWS IoT Core simulation, and Amazon Bedrock explainability to provide actionable, profile-safe recommendations during high-pollution surges.

## 📁 Repository Structure
- `ml/`: Machine learning pipeline, feature engineering, ingestion, inference, and Bedrock explanation service.
  - `ingest.py`: Real-time telemetry ingestion from CAAQMS and weather APIs with hourly history.
  - `features.py`: Feature engineering pipeline and vector schema.
  - `train.py`: Model training script with LightGBM and evaluation metrics.
  - `predict.py`: Inference service with complete 15-feature alignment and surge forecasting.
  - `bedrock_service.py`: Generative explanation engine using Amazon Bedrock with deterministic fallbacks.
  - `models/`: Trained model binaries (`model.joblib`).
  - `accuracy.json`: Training and validation performance metrics.
- `simulator/`: IoT sensor simulation scripts.
  - `sensor_simulator.py`: Multi-station synthetic telemetry generator for AWS IoT Core MQTT streaming.

## 👥 Contributors
- **Krishna Tiwari** ([@Krishnatiwari1909](https://github.com/Krishnatiwari1909)) - ML Lead & Contributor
