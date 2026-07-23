from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import app.main as main_module
from app.generation import GeneratedReflection, ReflectionGenerator
from app.main import app
from app.models import ReflectionRequest, SharedReflectionRequest
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
    assert all(source["origin_context"] for source in body["sources"])
    assert all(source["original_meaning"] for source in body["sources"])
    assert all(source["situation_application"] for source in body["sources"])
    assert all("Catholic Edition" in source["translation"] for source in body["sources"])
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
    async def select_one(self, situation, results, language, contexts):
        source_id = Retriever.source_id(results[0].passage)
        return GeneratedReflection(
            summary="One passage is enough here.",
            actions=["Consider its application carefully."],
            mode="hugging-face:test-model",
            source_ids=(source_id,),
            applications={source_id: "This is a careful and limited application."},
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
    assert "limited application" in response.json()["sources"][0]["situation_application"]


def test_shared_reflection_is_an_exact_snapshot(monkeypatch):
    repository = MagicMock()
    repository.save.return_value = "share-id"
    repository.get.side_effect = lambda _share_id: repository.save.call_args.args[0]
    monkeypatch.setattr(main_module, "_share_repository", lambda: repository)

    with TestClient(app) as client:
        reflection = client.post(
            "/api/reflections",
            json={
                "situation": "A friend hurt me and I want to respond with honesty and compassion.",
                "language": "en",
            },
        ).json()
        created = client.post(
            "/api/shares",
            json={
                "situation": "A friend hurt me and I want to respond with honesty and compassion.",
                "language": "en",
                "reflection": reflection,
            },
        )
        fetched = client.get(f"/api/shares/{created.json()['id']}")

    assert created.status_code == 201
    assert fetched.status_code == 200
    assert fetched.json()["reflection"] == reflection
    assert fetched.json()["situation"].startswith("A friend hurt me")


def test_missing_shared_reflection_returns_404(monkeypatch):
    repository = MagicMock()
    repository.get.return_value = None
    monkeypatch.setattr(main_module, "_share_repository", lambda: repository)

    with TestClient(app) as client:
        response = client.get("/api/shares/not-a-real-id")

    assert response.status_code == 404


def test_situation_requests_share_normalization() -> None:
    situation = "A situation   with enough detail to be accepted."

    reflection = ReflectionRequest(situation=situation)
    shared = SharedReflectionRequest(
        situation=situation,
        reflection={
            "summary": "Summary",
            "suggested_actions": ["Action"],
            "sources": [
                {
                    "reference": "Luke 1:1",
                    "quotation": "Text",
                    "literary_type": "Gospel",
                    "origin_context": "Context",
                    "broader_context": "Context",
                    "original_meaning": "Meaning",
                    "situation_application": "Application",
                    "context_confidence": "high",
                    "context_reviewed": True,
                    "relevance": "Relevant",
                    "context_reference": "Luke 1:1",
                    "context_quotation": "Text",
                }
            ],
            "limitations": "Limitations",
            "generated_with": "test",
        },
    )

    assert reflection.situation == shared.situation == "A situation with enough detail to be accepted."
