import joblib
import os
import requests
from app.settings import settings

_model = None

def download_model_if_missing():
    # Check kalau file model tak ada, download dari MODEL_URL
    if not os.path.exists(settings.MODEL_PATH):
        print(f"Model not found at {settings.MODEL_PATH}, downloading from {settings.MODEL_URL}")
        os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
        r = requests.get(settings.MODEL_URL)
        if r.status_code == 200:
            with open(settings.MODEL_PATH, "wb") as f:
                f.write(r.content)
            print("Model downloaded and saved!")
        else:
            raise Exception(f"Failed to download model from {settings.MODEL_URL}")

def load_model():
    """Load ML model from disk, auto-download if missing."""
    global _model
    if _model is None:
        download_model_if_missing()
        _model = joblib.load(settings.MODEL_PATH)
    return _model

def is_loaded():
    """Check if model is loaded."""
    return _model is not None
