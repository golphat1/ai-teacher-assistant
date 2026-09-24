from fastapi.testclient import TestClient
from app.main import app  # Fixed import path

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_health_check_db():
    response = client.get("/health/db")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"  # Fixed logic error
    assert body["database"] == "connected"