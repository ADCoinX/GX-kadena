"""Test persistent logger."""
from app.services.logger import setup_logging, log_event

def test_log_event():
    setup_logging()
    log_event(event="test", details="unit test log")