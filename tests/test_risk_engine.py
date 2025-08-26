"""Test risk engine logic."""
import pytest
from app.services.risk_engine import risk_score

def test_risk_score_basic(monkeypatch):
    # Patch Kadena adapters and scamdb to deterministic values
    monkeypatch.setattr("app.adapters.kadena.get_tx_count", lambda addr: 5)
    monkeypatch.setattr("app.adapters.kadena.get_address_age_days", lambda addr: 100)
    monkeypatch.setattr("app.adapters.scamdb.check_scam", lambda addr: False)
    monkeypatch.setattr("app.services.model_loader.load_model", lambda: type("M", (), {"predict": lambda self, X: [0.5]})())
    score, flags, rwa = risk_score("kadena", "address123")
    assert 0 <= score <= 1
    assert rwa == {}
    assert "scamdb" not in flags