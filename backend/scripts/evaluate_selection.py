#!/usr/bin/env python3
"""Replay selection policies on saved diagnostics without network or model calls."""

import argparse
import json
from enum import StrEnum
from pathlib import Path

from app.evaluation import score_sources, summarize
from app.evaluation_selection import SelectionPolicy, select_candidates
from app.retrieval import Retriever
from app.retrieval_diagnostics import RankedCandidate


class Ordering(StrEnum):
    RANKED = "ranked"
    THEME_PRIORITY = "theme_priority"
    THEME_ALPHABETICAL = "theme_alphabetical"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Output already exists")
    report = json.loads(args.report.read_text())
    retriever = Retriever(Path(__file__).parents[1] / "app/data/polubg_verses.json")
    passages = {passage.reference: passage for passage in retriever.passages}
    variants: dict[str, list[dict]] = {}
    for row in report["results"]:
        searches = row["response"]["diagnostics"]["searches"]
        for ordering in Ordering:
            for policy in SelectionPolicy:
                actual: list[str] = []
                for search in searches:
                    candidates = [RankedCandidate.model_validate(value)
                                  for value in search["after_rerank"]]
                    themes = search["themes"]
                    if ordering != Ordering.RANKED and len(themes) > 1:
                        preferred: list[RankedCandidate] = []
                        ordered_themes = (sorted(themes) if ordering == Ordering.THEME_ALPHABETICAL else
                                          sorted(themes, key=lambda value: -themes[value]))
                        for theme in ordered_themes:
                            match = next((candidate for candidate in candidates
                                          if candidate not in preferred and retriever._is_anchor(
                                              passages[candidate.reference], {theme})), None)
                            if match is not None:
                                preferred.append(match)
                        candidates = preferred + [candidate for candidate in candidates
                                                  if candidate not in preferred]
                    expanded = [candidate.model_copy(update={
                        "reference": retriever._complete_anchor(
                            passages[candidate.reference], set(themes),
                        ).reference,
                    }) for candidate in candidates]
                    actual.extend(select_candidates(expanded, policy))
                name = f"{ordering}/{policy}"
                variants.setdefault(name, []).append({
                    "id": row["id"], "category": row["category"], "selected": actual,
                    "scores": score_sources(actual, row["expected"]),
                })
    result = {
        "kind": "saved-pool-selection-ablation", "input_report": str(args.report),
        "dataset_sha256": report["dataset_sha256"],
        "limitations": "Only saved top candidates; not a full production replay. No generation. "
                        "Uses overlap deduplication, not the production adjacent-start rule.",
        "recorded_selected": report["stages"]["selected"],
        "variants": {name: {"summary": summarize(rows), "results": rows}
                     for name, rows in variants.items()},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as output:
        output.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({name: value["summary"] for name, value in result["variants"].items()},
                     indent=2))


if __name__ == "__main__":
    main()
