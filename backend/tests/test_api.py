from fastapi.testclient import TestClient

from app.generation import GeneratedAnswer, ReflectionGenerator
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
            json={
                "situation": "A friend lied to me and I want to respond honestly without being cruel.",
                "language": "en",
            },
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


def test_chat_answers_followup_with_server_owned_sources(monkeypatch):
    async def generated_answer(*args, **kwargs):
        return GeneratedAnswer(
            "Model explains the selected passages in response to this particular question.",
            "hugging-face:test-model",
        )

    monkeypatch.setattr(ReflectionGenerator, "answer_followup", generated_answer)
    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json={
                "situation": "Mam dość Ukraińców po nagraniu, które zobaczyłam w mediach społecznościowych.",
                "question": "Dlaczego ten fragment pasuje i czego nie powinnam z niego wywnioskować?",
                "history": [
                    {"role": "assistant", "content": "Najpierw oddzielmy fakty od przypuszczeń."}
                ],
                "language": "pl",
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert body["sources"]
    assert all("translation" in source for source in body["sources"])
    assert body["generated_with"] == "hugging-face:test-model"


def test_chat_rejects_unbounded_history():
    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json={
                "situation": "I need help understanding a difficult passage and applying it carefully.",
                "question": "What does it mean?",
                "history": [{"role": "user", "content": "Another question"}] * 13,
                "language": "en",
            },
        )
    assert response.status_code == 422


def test_chat_reports_when_no_conversation_model_is_configured():
    with TestClient(app) as client:
        response = client.post(
            "/api/chat",
            json={
                "situation": "Rozważam słowa z Mateusza 18:17 w kontekście konfliktu i Ukraińców w Polsce.",
                "question": "Co znaczy: niech będzie dla ciebie jak poganin i celnik? Czy mogę ich nienawidzić?",
                "language": "pl",
            },
        )
    assert response.status_code == 503
    assert "HF_TOKEN" in response.json()["detail"]
