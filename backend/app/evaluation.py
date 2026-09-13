"""Offline scoring and HTTP execution of human-reviewable verse selection cases."""

import json
import re
from collections.abc import Callable
from pathlib import Path
from time import perf_counter

import httpx
from pydantic import BaseModel, Field

from .localization import POLISH_BOOKS


class ExpectedSource(BaseModel):
    reference: str
    rationale: str = Field(min_length=10)


class EvaluationCase(BaseModel):
    id: str
    category: str
    situation: str = Field(min_length=20, max_length=3000)
    reviewed: bool = False
    expected_sources: list[ExpectedSource] = Field(min_length=1)
    review_notes: str = ""


def parse_reference(value: str) -> set[tuple[str, int, int]]:
    match = re.fullmatch(r"(.+?) (\d+):(\d+)(?:[–-](\d+))?", value.strip())
    if not match:
        raise ValueError(f"Unsupported reference: {value}")
    book, chapter, start, end = match.groups()
    book = {localized: canonical for canonical, localized in POLISH_BOOKS.items()}.get(book, book)
    first, last = int(start), int(end or start)
    if first < 1 or last < first or last - first > 200:
        raise ValueError(f"Invalid verse range: {value}")
    return {(book, int(chapter), verse) for verse in range(first, last + 1)}


def load_cases(path: Path) -> list[EvaluationCase]:
    import_data = path.read_text(encoding="utf-8")
    from_json = json.loads(import_data)
    cases = [EvaluationCase.model_validate(row) for row in from_json]
    if not cases or len({case.id for case in cases}) != len(cases):
        raise ValueError("Dataset must contain cases with unique IDs")
    corpus_path = Path(__file__).parent / "data" / "polubg_verses.json"
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    available = {(row["book"], row["chapter"], row["verse"]) for row in corpus}
    for case in cases:
        for source in case.expected_sources:
            if not parse_reference(source.reference) <= available:
                raise ValueError(f"{case.id}: reference absent from Polish corpus: {source.reference}")
    return cases


def score_sources(actual: list[str], expected: list[str]) -> dict[str, float]:
    targets = [parse_reference(value) for value in expected]
    matched: set[int] = set()
    hits = 0
    reciprocal_rank = 0.0
    for rank, value in enumerate(actual, 1):
        verses = parse_reference(value)
        # Require the entire editorial target; a neighboring verse alone is insufficient.
        candidates = {index for index, target in enumerate(targets) if target <= verses}
        new_matches = candidates - matched
        if new_matches:
            hits += 1
            reciprocal_rank = reciprocal_rank or 1 / rank
            matched.update(new_matches)
    return {
        "hit": float(bool(matched)),
        "precision": hits / len(actual) if actual else 0.0,
        "recall": len(matched) / len(targets) if targets else 0.0,
        "mrr": reciprocal_rank,
    }


async def evaluate(
    cases: list[EvaluationCase], client: httpx.AsyncClient, diagnostics: bool = False,
    progress: Callable[[int, int], None] | None = None,
) -> dict:
    results = []
    for case in cases:
        started = perf_counter()
        row = {"id": case.id, "category": case.category, "situation": case.situation}
        expected = [source.reference for source in case.expected_sources]
        row["expected"] = expected
        try:
            response = await client.post(
                "/api/reflections", json={"situation": case.situation, "language": "pl", "diagnostics": diagnostics}
            )
            response.raise_for_status()
            body = response.json()
            row["response"] = body
            actual = [source["reference"] for source in body["sources"]]
            if not 1 <= len(actual) <= 3:
                raise ValueError("Expected between one and three sources")
            row["scores"] = score_sources(actual, expected)
            if diagnostics:
                if not body.get("diagnostics"):
                    raise ValueError("Server did not return requested diagnostics")
                row["stage_scores"] = stage_scores(body, expected)
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
            row["error"] = str(error)
            row["scores"] = score_sources([], expected)
        row["seconds"] = round(perf_counter() - started, 3)
        results.append(row)
        if progress is not None:
            progress(len(results), len(cases))
    return {"summary": summarize(results), "results": results}


def summarize(results: list[dict]) -> dict:
    count = len(results)
    return {
        "count": count,
        "errors": sum("error" in row for row in results),
        "local_extractive": sum(
            row.get("response", {}).get("generated_with") == "local-extractive"
            for row in results
        ),
        **{
            metric: sum(row["scores"][metric] for row in results) / count if count else 0.0
            for metric in ("hit", "precision", "recall", "mrr")
        },
    }


def compare_reports(report: dict, baseline: dict) -> dict:
    if report["dataset_sha256"] != baseline["dataset_sha256"]:
        raise ValueError("Cannot compare reports from different dataset versions")
    previous = {row["id"]: row for row in baseline["results"]}
    if set(previous) != {row["id"] for row in report["results"]}:
        raise ValueError("Cannot compare different case selections")
    return {
        "summary_delta": {
            metric: report["summary"][metric] - baseline["summary"][metric]
            for metric in ("hit", "precision", "recall", "mrr", "errors")
        },
        "cases": [
            {"id": row["id"], "delta": {
                metric: row["scores"][metric] - previous[row["id"]]["scores"][metric]
                for metric in ("hit", "precision", "recall", "mrr")
            }}
            for row in report["results"]
            if row["scores"] != previous[row["id"]]["scores"]
        ],
    }


def render_review(cases: list[EvaluationCase]) -> str:
    corpus = json.loads(
        (Path(__file__).parent / "data" / "polubg_verses.json").read_text(encoding="utf-8")
    )
    verses = {(row["book"], row["chapter"], row["verse"]): row["text"] for row in corpus}
    lines = [
        "# Zestaw ewaluacyjny — szkic do przeglądu",
        "",
        "Źródło prawdy: cases.pl.json. Zmiany i zatwierdzenia wprowadzaj w tym pliku,",
        "a następnie wygeneruj ten podgląd ponownie. Propozycje nie są listą wszystkich",
        "poprawnych odpowiedzi. Każdy werset wymaga oceny w kontekście konkretnej wypowiedzi.",
        "",
        "Cytaty: Uwspółcześniona Biblia Gdańska (UBG), © 2018 Fundacja Wrota Nadziei,",
        "[CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/).",
        "Tekst z lokalnego korpusu polubg_verses.json, importowanego z eBible.org;",
        "cytaty bez zmian. Uzasadnienia są osobnymi propozycjami redakcyjnymi.",
        "",
    ]
    for case in cases:
        lines.extend([
            f"## {case.id} · {case.category}", "", case.situation, "",
            f"Zatwierdzony: {'tak' if case.reviewed else 'nie'}", "",
        ])
        for source in case.expected_sources:
            keys = sorted(parse_reference(source.reference))
            book, chapter, first = keys[0]
            last = keys[-1][2]
            label = f"{POLISH_BOOKS.get(book, book)} {chapter}:{first}"
            if first != last:
                label += f"–{last}"
            lines.extend([
                f"**{label}**", "", "> " + " ".join(verses[key] for key in keys), "",
                source.rationale, "",
            ])
        lines.extend([f"Uwagi: {case.review_notes or '—'}", ""])
    return "\n".join(lines)


def stage_scores(body: dict, expected: list[str]) -> dict[str, dict[str, float]]:
    searches = body.get("diagnostics", {}).get("searches", [])
    if not searches:
        return {}
    selected_search = searches[-1]
    stages = {
        "initial_before_rerank": [
            item["reference"] for item in searches[0]["before_rerank"]
        ],
        "before_rerank": [item["reference"] for item in selected_search["before_rerank"]],
        "after_rerank_top6": [
            item["reference"] for item in selected_search["after_rerank"][:6]
        ],
        "selected": selected_search["selected"],
        "final": [source["reference"] for source in body.get("sources", [])],
    }
    expected_verses = set().union(*(parse_reference(value) for value in expected))
    scores = {}
    for stage, references in stages.items():
        actual_verses = set().union(*(parse_reference(value) for value in references))
        scores[stage] = {
            **score_sources(references, expected),
            "verse_coverage": len(actual_verses & expected_verses) / len(expected_verses),
        }
    return scores
