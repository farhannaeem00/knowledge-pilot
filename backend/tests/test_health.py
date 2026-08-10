"""
Smoke tests for the health/readiness endpoints. This is the first test
in the suite — every later step adds its own tests here, and `make test`
runs all of them together.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready() -> None:
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["database"] == "ok"


def test_request_id_header_present() -> None:
    response = client.get("/api/v1/health")
    assert "x-request-id" in response.headers
