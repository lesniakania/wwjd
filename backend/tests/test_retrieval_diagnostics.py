from pathlib import Path

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.retrieval import Retriever
from app.retrieval_diagnostics import RetrievalTrace


DATA = Path(__file__).parents[1] / "app" / "data" / "polubg_verses.json"


def test_trace_preserves_ranking_and_is_request_local() -> None:
    retriever = Retriever(DATA)
    query = "Mam dość Ukraińców i nie chcę im pomagać."
    expected = retriever.search(query, limit=6)
    trace = RetrievalTrace()
    actual = retriever.search(query, limit=6, trace=trace)
    assert actual == expected
    assert trace.before_rerank
    assert trace.before_rerank == trace.after_rerank
    assert trace.selected == [result.passage.reference for result in actual]
    assert not RetrievalTrace().before_rerank


def test_diagnostics_are_opt_in_and_include_safe_configuration(monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "evaluation_diagnostics", True)
    with TestClient(app) as client:
        payload = {"situation": "Kolega mnie okłamał i chcę powiedzieć mu prawdę."}
        ordinary = client.post("/api/reflections", json=payload).json()
        detailed = client.post("/api/reflections", json={**payload, "diagnostics": True}).json()
    assert ordinary.get("diagnostics") is None
    trace = detailed["diagnostics"]
    assert trace["searches"][0]["selected"]
    assert trace["configuration"]["embedding_model"] == ""
    assert "hf_token" not in trace["configuration"]
    assert "database_url" not in trace["configuration"]
    assert len(trace["configuration"]["code_sha256"]) == 64


def test_diagnostics_disabled_by_default() -> None:
    with TestClient(app) as client:
        response = client.post("/api/reflections", json={
            "situation": "Kolega mnie okłamał i chcę powiedzieć mu prawdę.",
            "diagnostics": True,
        })
    assert response.status_code == 403


def test_fused_ranking_preserves_initial_evidence_and_checks_scores() -> None:
    retriever = Retriever(DATA, reranker=ReverseReranker(), reranker_strategy="fused")
    candidates = [(0, 0.9, 0.8), (1, 0.8, 0.7), (2, 0.7, 0.6)]
    ranked = retriever._rerank("test", candidates)
    assert ranked[0] == candidates[0]
    assert {item[0] for item in ranked} == {0, 1, 2}


class ReverseReranker:
    def rerank(self, query: str, passages: list) -> list[float]:
        return [float(index) for index in range(len(passages))]


def test_explicit_concerns_override_literal_keywords() -> None:
    retriever = Retriever(DATA)
    trace = RetrievalTrace()
    retriever.search("Somebody lied; I am afraid.", trace=trace,
                     theme_override={"prejudice": 0.9})
    assert trace.themes == {"prejudice": 0.9}


def test_reviewed_short_anchor_is_returned_as_a_complete_passage() -> None:
    retriever = Retriever(DATA)
    results = retriever.search(
        "Jeśli przybysz będzie mieszkał z tobą nie czyńcie mu krzywdy",
        limit=6, theme_override={"prejudice": 0.9},
    )
    leviticus = next(result.passage for result in results if result.passage.book == "Leviticus")
    assert (leviticus.verse_start, leviticus.verse_end) == (33, 34)
