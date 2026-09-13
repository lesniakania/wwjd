#!/usr/bin/env python3
"""Compare retrieval stages without calling the generation model."""

import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter

from app.config import get_settings
from app.evaluation import load_cases, score_sources, stage_scores
from app.evaluation_reporting import report_details
from app.retrieval import BgeReranker, Retriever, SemanticEncoder
from app.retrieval_diagnostics import RetrievalTrace, evaluation_configuration
from app.retrieval_models import RerankerStrategy
from app.themes import SemanticThemeRouter


DATA = Path(__file__).parents[1] / "app" / "data" / "polubg_verses.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DATA.parents[1].parent /
                        "evaluation" / "cases.pl.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--variants", nargs="+", choices=["disabled", *RerankerStrategy],
                        default=["disabled", *RerankerStrategy])
    args = parser.parse_args()
    cases = load_cases(args.dataset)
    if args.limit is not None:
        if args.limit < 1:
            raise ValueError("--limit must be positive")
        cases = cases[:args.limit]
    variants = args.variants
    if any((args.output_dir / f"{variant}.json").exists() for variant in variants):
        raise ValueError("Choose a new output directory; existing reports are never overwritten")
    settings = get_settings()
    if settings.situation_analysis:
        raise ValueError("Use evaluate.py --local --diagnostics for model-assisted analysis")
    encoder = SemanticEncoder(settings.embedding_model) if settings.embedding_model else None
    reranker = (BgeReranker(settings.reranker_model)
                if settings.reranker_model and any(value != "disabled" for value in variants)
                else None)
    retriever = Retriever(
        DATA, encoder, Retriever.cache_name(DATA, settings.embedding_model) if encoder else None,
        SemanticThemeRouter(encoder) if encoder else None,
        reranker_candidates=settings.reranker_candidates,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for variant in variants:
        retriever.reranker = None if variant == "disabled" else reranker
        retriever.reranker_strategy = (
            RerankerStrategy.RAW if variant == "disabled" else RerankerStrategy(variant)
        )
        configuration = evaluation_configuration(settings)
        configuration["reranker_strategy"] = str(variant)
        configuration["reranker_model"] = "" if variant == "disabled" else settings.reranker_model
        rows = []
        for case in cases:
            started = perf_counter()
            trace = RetrievalTrace()
            retriever.search(case.situation, limit=6, trace=trace)
            body = {"sources": [], "diagnostics": {
                "searches": [trace.model_dump()], "configuration": configuration,
            }}
            expected = [source.reference for source in case.expected_sources]
            rows.append({
                "id": case.id, "category": case.category, "situation": case.situation,
                "expected": expected, "response": body,
                "scores": score_sources(trace.selected, expected),
                "stage_scores": stage_scores(body, expected),
                "seconds": perf_counter() - started,
            })
            if len(rows) % 10 == 0:
                print(f"{variant}: {len(rows)}/{len(cases)}", flush=True)
        details = report_details(rows)
        details["stages"].pop("final", None)
        report = {
            "kind": "retrieval-only", "variant": str(variant),
            "dataset_sha256": hashlib.sha256(args.dataset.read_bytes()).hexdigest(),
            "results": rows, **details,
        }
        (args.output_dir / f"{variant}.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(report["stages"], indent=2), flush=True)


if __name__ == "__main__":
    main()
