from app.evaluation import EvaluationCase, score_sources, summarize
from app.evaluation_reporting import stage_scores, rescore_report, summarize_repeats, report_details


def test_stage_scores_distinguish_complete_passages_from_verse_coverage() -> None:
    body = {"diagnostics": {"searches": [{
        "before_rerank": [{"reference": "James 1:19"}, {"reference": "James 1:20"}],
        "after_rerank": [{"reference": "James 1:20"}, {"reference": "James 1:19"}],
        "selected": ["James 1:19"],
    }]}}
    scores = stage_scores(body, ["James 1:19-20"])
    assert scores["before_rerank"]["recall"] == 0
    assert scores["before_rerank"]["verse_coverage"] == 1
    assert scores["selected"]["verse_coverage"] == 0.5
    assert "initial_before_rerank" in scores


def test_summary_counts_local_generation_separately_from_errors() -> None:
    rows = [{"scores": score_sources([], ["Luke 1:1"]),
             "response": {"generated_with": "local-extractive"}}]
    assert summarize(rows)["local_extractive"] == 1
    assert summarize(rows)["errors"] == 0


def test_rescoring_preserves_response_and_uses_new_editorial_targets() -> None:
    case = EvaluationCase(id="one", category="test", situation="A detailed sample situation.",
                          expected_sources=[{"reference": "Luke 1:1", "rationale": "Relevant text"}])
    old = {"dataset_sha256": "old", "results": [{
        "id": "one", "situation": case.situation,
        "response": {"sources": [{"reference": "Luke 1:1"}]},
        "scores": score_sources([], ["Luke 1:2"]),
    }]}
    new = rescore_report(old, [case], "new")
    assert new["summary"]["hit"] == 1
    assert new["original_dataset_sha256"] == "old"
    assert new["results"][0]["response"] == old["results"][0]["response"]
    assert old["results"][0]["scores"]["hit"] == 0


def test_repeat_summary_reports_variability() -> None:
    reports = [
        {"summary": {"hit": value, "precision": value, "recall": value,
                     "mrr": value, "errors": 0, "local_extractive": 0}}
        for value in (0.0, 0.5, 1.0)
    ]
    summary = summarize_repeats(reports)
    assert summary["hit"]["mean"] == 0.5
    assert summary["hit"]["stdev"] == 0.5


def test_stage_scores_keep_original_query_separate_from_fallback() -> None:
    body = {"diagnostics": {"searches": [
        {"before_rerank": [], "after_rerank": [], "selected": []},
        {"before_rerank": [{"reference": "Luke 1:1"}],
         "after_rerank": [{"reference": "Luke 1:1"}], "selected": ["Luke 1:1"]},
    ]}}
    scores = stage_scores(body, ["Luke 1:1"])
    assert scores["initial_before_rerank"]["hit"] == 0
    assert scores["before_rerank"]["hit"] == 1


def test_analysis_failures_are_counted_separately_from_generation_fallbacks() -> None:
    rows = [{"id": "one", "category": "test", "scores": score_sources([], ["Luke 1:1"]),
             "response": {"diagnostics": {"configuration": {}, "analysis": {
                 "status": "fallback", "seconds": 2.0,
             }}}}]
    assert report_details(rows)["analysis_fallbacks"] == 1
