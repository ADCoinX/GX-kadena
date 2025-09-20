import pytest
from fastapi.testclient import TestClient
from gx_kadena.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_invalid_address():
    r = client.get("/validate/notanaddress")
    assert r.status_code == 400

def test_rate_limit(monkeypatch):
    # Simulate token bucket empty
    import gx_kadena.security_mw as smw
    monkeypatch.setattr(smw, "_tokens", 0)
    r = client.get("/validate/k:abcdef...")
    assert r.status_code == 429

# Add more tests for happy path with mock kadena_client if needed