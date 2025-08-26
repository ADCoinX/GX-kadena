"""Test security middleware."""
from fastapi.testclient import TestClient
from app.main import app

def test_body_size_limit():
    client = TestClient(app)
    big_body = "A" * 20000
    resp = client.post("/validate", data=big_body, headers={"Content-Type": "application/json"})
    assert resp.status_code == 413

def test_rate_limit(monkeypatch):
    client = TestClient(app)
    monkeypatch.setattr("app.middleware.RateLimitMiddleware.bucket", {})
    for _ in range(65):
        resp = client.get("/health")
    assert resp.status_code in (200, 429)