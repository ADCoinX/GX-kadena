"""Model loader for ML risk model."""
import joblib
from app.settings import settings

_model = None

def load_model():
    """Load ML model from disk."""
    global _model
    if _model is None:
        _model = joblib.load(settings.MODEL_PATH)
    return _model

def is_loaded():
    """Check if model is loaded."""
    return _model is not None