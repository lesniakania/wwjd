import json

import httpx

from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app
from app.situation_analysis import (
    AnalysisStatus, SituationAnalyzer, SpeakerRole, SituationAnalysis, SituationProfile,
)
from app.themes import Theme


def mock_analysis(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    assert body["temperature"] == 0
    assert "accusations" in body["messages"][0]["content"]
    return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({
        "speaker_role": "actor",
        "problem": "The speaker assumes wrongdoing based on another person's background.",
        "themes": ["prejudice", "dignity_and_respect"],
        "search_query": "Treat strangers fairly. Do not judge people by their origin.",
    })}}]})


async def test_analysis_retains_speaker_role_and_validates_closed_theme_catalog() -> None:
    analyzer = SituationAnalyzer(Settings(hf_token="test", situation_analysis=True))
    async with httpx.AsyncClient(transport=httpx.MockTransport(mock_analysis)) as client:
        result = await analyzer.analyze(
            "I avoid foreign coworkers because I assume they are all dishonest.", "en", client
        )
    assert result.status == AnalysisStatus.SUCCESS
    assert result.profile.speaker_role == SpeakerRole.ACTOR
    assert result.profile.themes == [Theme.PREJUDICE, Theme.DIGNITY_AND_RESPECT]


def invalid_analysis(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": {"content": '{"themes":["bogus"]}'}}]})


async def test_invalid_analysis_returns_explicit_fallback() -> None:
    analyzer = SituationAnalyzer(Settings(hf_token="test", situation_analysis=True))
    async with httpx.AsyncClient(transport=httpx.MockTransport(invalid_analysis)) as client:
        result = await analyzer.analyze("A sufficiently detailed situation.", "en", client)
    assert result.status == AnalysisStatus.FALLBACK
    assert result.profile is None


async def test_disabled_analysis_does_not_need_network() -> None:
    result = await SituationAnalyzer(Settings(situation_analysis=False)).analyze(
        "A sufficiently detailed situation.", "en"
    )
    assert result.status == AnalysisStatus.DISABLED


def unavailable_analysis(request: httpx.Request) -> httpx.Response:
    return httpx.Response(503)


async def test_provider_failure_is_reported_without_provider_response_text() -> None:
    analyzer = SituationAnalyzer(Settings(hf_token="test", situation_analysis=True))
    async with httpx.AsyncClient(transport=httpx.MockTransport(unavailable_analysis)) as client:
        result = await analyzer.analyze("A sufficiently detailed situation.", "en", client)
    assert result.status == AnalysisStatus.FALLBACK
    assert result.error_type == "HTTPStatusError"


async def analyzed_prejudice(
    self: SituationAnalyzer, situation: str, language: str,
) -> SituationAnalysis:
    return SituationAnalysis(status=AnalysisStatus.SUCCESS, profile=SituationProfile(
        speaker_role=SpeakerRole.ACTOR,
        problem="The speaker unfairly excludes another person.",
        themes=[Theme.PREJUDICE],
        search_query="Treat a stranger with kindness and impartiality.",
    ))


def test_service_uses_analysis_for_retrieval_and_original_input_for_safety(monkeypatch) -> None:
    monkeypatch.setattr(SituationAnalyzer, "analyze", analyzed_prejudice)
    monkeypatch.setattr(get_settings(), "evaluation_diagnostics", True)
    with TestClient(app) as client:
        response = client.post("/api/reflections", json={
            "situation": "I am in immediate danger because someone threatened to kill me.",
            "language": "en", "diagnostics": True,
        })
    assert response.status_code == 200
    body = response.json()
    assert body["safety_message"]
    trace = body["diagnostics"]["searches"][0]
    assert trace["query"] == "Treat a stranger with kindness and impartiality."
    assert set(trace["themes"]) == {"prejudice"}


def empty_analysis(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": {"content": None}}]})


async def test_missing_model_content_falls_back() -> None:
    analyzer = SituationAnalyzer(Settings(hf_token="test", situation_analysis=True))
    async with httpx.AsyncClient(transport=httpx.MockTransport(empty_analysis)) as client:
        result = await analyzer.analyze("A sufficiently detailed situation.", "en", client)
    assert result.status == AnalysisStatus.FALLBACK
