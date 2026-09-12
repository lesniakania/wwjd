import json
from pathlib import Path

import httpx
import pytest

from app.evaluation import (
    compare_reports, evaluate, load_cases, parse_reference, render_review, score_sources,
)


DATASET = Path(__file__).parents[1] / "evaluation" / "cases.pl.json"


def test_dataset_has_100_unique_valid_cases() -> None:
    cases = load_cases(DATASET)
    assert len(cases) == 100
    assert len({case.situation for case in cases}) == 100
    assert sum(case.category == "uprzedzenia" for case in cases) == 50


def test_scoring_handles_ranges_duplicates_and_unknown_sources() -> None:
    relevant = ["Łukasza 10:27", "Jakuba 2:1"]
    result = score_sources(
        ["Łukasza 10:25–28", "Łukasza 10:27", "Jana 1:1"], relevant
    )
    assert result["hit"] == 1
    assert result["recall"] == 0.5
    assert result["precision"] == pytest.approx(1 / 3)
    assert result["mrr"] == 1


def test_scoring_empty_and_wrong_results() -> None:
    assert score_sources([], ["Jakuba 2:1"])["hit"] == 0
    assert score_sources(["Jana 1:1"], ["Jakuba 2:1"])["mrr"] == 0


async def test_api_errors_are_counted_and_responses_preserved() -> None:
    cases = load_cases(DATASET)[:2]
    transport = httpx.MockTransport(mock_response)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        report = await evaluate(cases, client)
    assert report["summary"]["count"] == 2
    assert report["summary"]["errors"] == 1
    assert report["summary"]["hit"] == 0.5
    assert report["results"][0]["response"]["summary"] == "Saved for review"
    assert report["results"][1]["error"]


def mock_response(request: httpx.Request) -> httpx.Response:
    situation = json.loads(request.content)["situation"]
    if situation == load_cases(DATASET)[0].situation:
        return httpx.Response(200, json={
            "sources": [{"reference": "Łukasza 10:27"}], "summary": "Saved for review"
        })
    return httpx.Response(503)


def test_comparison_rejects_changed_dataset() -> None:
    with pytest.raises(ValueError, match="different dataset"):
        compare_reports({"dataset_sha256": "new"}, {"dataset_sha256": "old"})


def test_review_contains_local_corpus_quotations() -> None:
    text = render_review(load_cases(DATASET)[:1])
    assert "pl-001" in text
    assert "Łukasza 10:27" in text
    assert "Będziesz miłował" in text
    assert "CC BY-ND 4.0" in text


def test_comparison_reports_metric_deltas_and_rejects_different_selection() -> None:
    before = score_sources(["Jana 1:1"], ["Łukasza 10:27"])
    after = score_sources(["Łukasza 10:27"], ["Łukasza 10:27"])
    baseline = {
        "dataset_sha256": "same", "summary": {**before, "errors": 0},
        "results": [{"id": "pl-001", "scores": before}],
    }
    report = {
        "dataset_sha256": "same", "summary": {**after, "errors": 0},
        "results": [{"id": "pl-001", "scores": after}],
    }
    comparison = compare_reports(report, baseline)
    assert comparison["summary_delta"]["precision"] == 1
    assert comparison["cases"][0]["delta"]["mrr"] == 1
    report["results"][0]["id"] = "other"
    with pytest.raises(ValueError, match="different case"):
        compare_reports(report, baseline)


def test_dataset_rejects_missing_verse_and_duplicate_ids(tmp_path: Path) -> None:
    path = tmp_path / "cases.json"
    row = load_cases(DATASET)[0].model_dump()
    path.write_text(json.dumps([row, row]))
    with pytest.raises(ValueError, match="unique IDs"):
        load_cases(path)
    row["expected_sources"][0]["reference"] = "Luke 100:1"
    path.write_text(json.dumps([row]))
    with pytest.raises(ValueError, match="absent"):
        load_cases(path)


def test_partial_target_and_different_book_are_not_matches() -> None:
    assert score_sources(["Luke 10:25"], ["Luke 10:25-28"])["hit"] == 0
    assert score_sources(["John 10:27"], ["Luke 10:27"])["hit"] == 0
    assert score_sources(["John 1:1", "Luke 10:27"], ["Luke 10:27"])["mrr"] == 0.5


def test_dataset_includes_verbatim_quotations_for_every_expected_source() -> None:
    corpus_path = Path(__file__).parents[1] / "app" / "data" / "polubg_verses.json"
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    verses = {(row["book"], row["chapter"], row["verse"]): row["text"] for row in corpus}
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    for case in cases:
        for source in case["expected_sources"]:
            keys = sorted(parse_reference(source["reference"]))
            assert source["quotation"] == " ".join(verses[key] for key in keys), case["id"]


def test_editorial_revision_replaces_body_metaphor_and_prioritizes_trust() -> None:
    cases = {case.id: case for case in load_cases(DATASET)}
    for case_id in ("pl-026", "pl-027", "pl-028", "pl-029", "pl-030"):
        assert all(
            source.reference != "1 Corinthians 12:22"
            for source in cases[case_id].expected_sources
        )
    assert cases["pl-091"].expected_sources[0].reference == "Proverbs 31:11"


def test_fear_and_boundaries_have_situation_specific_selections() -> None:
    cases = load_cases(DATASET)
    for category in ("lek_i_niepewnosc", "granice_i_szacunek"):
        selections = [
            tuple(source.reference for source in case.expected_sources)
            for case in cases if case.category == category
        ]
        assert len(set(selections)) == len(selections)


@pytest.mark.parametrize(("case_id", "removed_reference"), [
    ("pl-029", "James 1:19"),
    ("pl-030", "Ephesians 4:29"),
    ("pl-077", "Psalms 62:8"),
    ("pl-078", "Ecclesiastes 4:9-10"),
    ("pl-093", "Colossians 3:21"),
])
def test_second_editorial_review_replaces_rejected_sources(
    case_id: str, removed_reference: str,
) -> None:
    case = next(case for case in load_cases(DATASET) if case.id == case_id)
    assert removed_reference not in [source.reference for source in case.expected_sources]


def test_every_case_has_three_editorial_proposals() -> None:
    for case in load_cases(DATASET):
        assert len(case.expected_sources) == 3, case.id


def test_stuttering_case_focuses_on_listening_instead_of_love() -> None:
    case = next(case for case in load_cases(DATASET) if case.id == "pl-029")
    references = {source.reference for source in case.expected_sources}
    assert "Job 13:17" in references
    assert references.isdisjoint({"1 Corinthians 13:4", "Romans 12:10"})
