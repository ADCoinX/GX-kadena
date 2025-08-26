"""Test validate endpoint flow."""
from fastapi.testclient import TestClient
from app.main import app

def test_validate_api(monkeypatch):
    monkeypatch.setattr("app.adapters.kadena.get_tx_count", lambda addr: 7)
    monkeypatch.setattr("app.adapters.kadena.get_address_age_days", lambda addr: 90)
    monkeypatch.setattr("app.adapters.scamdb.check_scam", lambda addr: False)
    monkeypatch.setattr("app.services.model_loader.load_model", lambda: type("M", (), {"predict": lambda self, X: [0.7]})())
    client = TestClient(app)
    resp = client.post("/validate", json={"chain": "kadena", "address": "address123", "check_rwa": True})
    assert resp.status_code == 200
    data = resp.json()
    assert "score" in data and "iso_xml" in data