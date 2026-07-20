from fastapi.testclient import TestClient

from app.generation import GeneratedReflection, ReflectionGenerator
from app.main import app
from app.retrieval import Retriever


def test_health_reports_loaded_corpus():
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["verses"] > 30_000


def test_reflection_returns_server_owned_sources():
    with TestClient(app) as client:
        response = client.post(
            "/api/reflections",
            json={
                "situation": "A friend lied to me and I want to respond honestly without being cruel.",
                "language": "en",
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["sources"]
    assert 1 <= len(body["sources"]) <= 3
    assert all(source["explanation"] for source in body["sources"])
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
            json={
                "situation": "I am in immediate danger because someone threatened to kill me.",
                "language": "en",
            },
        )
    assert response.status_code == 200
    assert "emergency services" in response.json()["safety_message"]


def test_polish_is_default_and_returns_polish_scripture():
    with TestClient(app) as client:
        response = client.post(
            "/api/reflections",
            json={"situation": "Kolega mnie okłamał i nie wiem, jak odpowiedzieć uczciwie i spokojnie."},
        )
    assert response.status_code == 200
    body = response.json()
    assert "Biblijna droga" in body["summary"]
    assert "Uwspółcześniona Biblia Gdańska" in body["sources"][0]["translation"]
    assert any(character in body["sources"][0]["quotation"] for character in "ąćęłńóśźż")


def test_model_can_reduce_candidates_to_one_explained_source(monkeypatch):
    async def select_one(self, situation, results, language):
        source_id = Retriever.source_id(results[0].passage)
        return GeneratedReflection(
            summary="One passage is enough here.",
            actions=["Consider its application carefully."],
            mode="hugging-face:test-model",
            source_ids=(source_id,),
            explanations={source_id: "This explains the passage in context and its limited application."},
        )

    monkeypatch.setattr(ReflectionGenerator, "generate", select_one)
    with TestClient(app) as client:
        response = client.post(
            "/api/reflections",
            json={
                "situation": "Someone treated me badly and I want to respond without seeking revenge.",
                "language": "en",
            },
        )
    assert response.status_code == 200
    assert len(response.json()["sources"]) == 1
    assert "limited application" in response.json()["sources"][0]["explanation"]
