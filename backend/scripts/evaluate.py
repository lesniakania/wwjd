#!/usr/bin/env python3
"""Compare verse selections from a running API using a fixed editorial dataset."""

import argparse
import asyncio
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.evaluation import compare_reports, evaluate, load_cases, summarize


DEFAULT_DATASET = Path(__file__).parents[1] / "evaluation" / "cases.pl.json"


async def run(args: argparse.Namespace) -> None:
    cases = load_cases(args.dataset)
    if args.reviewed_only:
        cases = [case for case in cases if case.reviewed]
    if args.limit is not None:
        if args.limit < 1:
            raise ValueError("--limit must be positive")
        cases = cases[:args.limit]
    if not cases:
        raise ValueError("No cases selected; review the dataset first or omit --reviewed-only")
    baseline = json.loads(args.baseline.read_text()) if args.baseline else None
    digest = hashlib.sha256(args.dataset.read_bytes()).hexdigest()
    if baseline:
        if baseline["dataset_sha256"] != digest:
            raise ValueError("Baseline uses a different dataset version")
        if {row["id"] for row in baseline["results"]} != {case.id for case in cases}:
            raise ValueError("Baseline uses a different case selection")
    async with httpx.AsyncClient(base_url=args.url, timeout=args.timeout) as client:
        report = await evaluate(cases, client)
    report.update({
        "dataset_sha256": digest,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "label": args.label,
        "url": args.url,
        "unreviewed_cases": sum(not case.reviewed for case in cases),
        "by_category": {
            category: summarize([row for row in report["results"] if row["category"] == category])
            for category in sorted({case.category for case in cases})
        },
    })
    if baseline:
        report["comparison"] = compare_reports(report, baseline)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "results"},
                     ensure_ascii=False, indent=2))
    if report["summary"]["errors"]:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--label", required=True, help="Architecture/model/configuration identifier")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--reviewed-only", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--timeout", type=float, default=180)
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
