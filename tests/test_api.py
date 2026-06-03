from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_get_existing_key() -> None:
    response = client.get("/api/get/hello")
    assert response.status_code == 200
    assert response.json() == {"key": "hello", "value": "world"}


def test_api_get_missing_key() -> None:
    response = client.get("/api/get/__nonexistent_key__")
    assert response.status_code == 404
    assert response.json() == {"key": "__nonexistent_key__", "error": "not found"}


def test_web_home() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
