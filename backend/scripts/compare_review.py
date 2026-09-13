#!/usr/bin/env python3
"""Compare saved systems using the independently completed calibration judgments."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from app.review_comparison import summarize_ratings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Output already exists")
    human_path = args.directory / "human-review.json"
    human = json.loads(human_path.read_text())
    provenance = json.loads((args.directory / "provenance.json").read_text())
    systems = sorted({origin for case in provenance.values() for origins in case["passages"].values()
                      for origin in origins} - {"gold"})
    reports = {}
    for system in systems:
        rows = []
        for case in human["cases"]:
            key = provenance[case["id"]]
            passages = [item for item in case["passages"]
                        if system in key["passages"][item["id"]]]
            applications = [item for item in case["applications"]
                            if system in key["applications"][item["id"]]]
            if any(item["rating"] not in {None, "appropriate", "problematic", "uncertain"}
                   for item in applications):
                raise ValueError("Unknown application rating")
            rows.append({"id": case["id"], "passage_ratings": [p["rating"] for p in passages],
                         "application_ratings": [a["rating"] for a in applications]})
        passage_ratings = [rating for row in rows for rating in row["passage_ratings"]]
        applications = Counter(rating for row in rows for rating in row["application_ratings"])
        judged = applications["appropriate"] + applications["problematic"]
        hits = sum(any(rating in {"direct", "supporting"} for rating in row["passage_ratings"])
                   for row in rows)
        unresolved = sum(not any(rating in {"direct", "supporting"}
                                 for rating in row["passage_ratings"])
                         and any(rating in {None, "uncertain"}
                                 for rating in row["passage_ratings"]) for row in rows)
        reports[system] = {
            "passages": summarize_ratings(passage_ratings), "cases": len(rows),
            "confirmed_inclusive_hits": hits, "unresolved_hit_cases": unresolved,
            "applications": {"appropriate": applications["appropriate"],
                             "problematic": applications["problematic"],
                             "uncertain": applications["uncertain"],
                             "unreviewed": applications[None],
                             "problematic_rate_judged": applications["problematic"] / judged
                             if judged else None},
            "results": rows,
        }
    result = {"human_review_sha256": hashlib.sha256(human_path.read_bytes()).hexdigest(),
              "kind": "human-calibration-comparison", "systems": reports,
              "limitations": "20 development cases; micro precision on decided unique case/reference "
                              "pairs; uncertain excluded. Applications are separate judgments. "
                              "Not full recall or a causal reranker-only experiment."}
    with args.output.open("x") as output:
        output.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({name: {key: value for key, value in report.items() if key != "results"}
                      for name, report in reports.items()}, indent=2))


if __name__ == "__main__":
    main()
