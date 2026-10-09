
import sys
from pathlib import Path

# Locate Person 3's existing ML repository.
ML_ROOT = Path(r"D:\AtmosAi\ml-team-repo\ml")

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from predict import predictor


def get_predictor():
    """Return the loaded LightGBM predictor."""
    if predictor.model is None:
        raise RuntimeError("The AtmosAI ML model could not be loaded.")

    return predictor


def predict_forecast(features: dict) -> dict:
    """Run the existing team's prediction logic."""
    model_predictor = get_predictor()
    return model_predictor.predict(features)
