from fastapi.testclient import TestClient

from app.main import app


def test_health_reports_loaded_corpus():
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["verses"] > 30_000


def test_reflection_returns_server_owned_sources():
    with TestClient(app) as client:
        response = client.post(
            "/api/reflections",
            json={"situation": "A friend lied to me and I want to respond honestly without being cruel."},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["sources"]
    assert all(source["translation"] == "World English Bible (WEB)" for source in body["sources"])
    assert body["generated_with"] == "local-extractive"


def test_short_input_is_rejected():
    with TestClient(app) as client:
        response = client.post("/api/reflections", json={"situation": "Help me"})
    assert response.status_code == 422


def test_high_risk_input_gets_safety_message():
    with TestClient(app) as client:
        response = client.post(
            "/api/reflections",
            json={"situation": "I am in immediate danger because someone threatened to kill me."},
        )
    assert response.status_code == 200
    assert "emergency services" in response.json()["safety_message"]

