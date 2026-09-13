#!/usr/bin/env python3
"""Compare verse selections using a running API or the local application."""

import argparse
import asyncio
import hashlib
import json
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.config import get_settings
from app.evaluation import compare_reports, evaluate, load_cases
from app.evaluation_reporting import report_details, rescore_report, summarize_repeats
from app.main import app, lifespan


DEFAULT_DATASET = Path(__file__).parents[1] / "evaluation" / "cases.pl.json"


@asynccontextmanager
async def evaluation_client(args: argparse.Namespace) -> AsyncIterator[httpx.AsyncClient]:
    if not args.local:
        async with httpx.AsyncClient(base_url=args.url, timeout=args.timeout) as client:
            yield client
        return
    get_settings().evaluation_diagnostics = args.diagnostics
    async with lifespan(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False), base_url="http://local",
            timeout=args.timeout,
        ) as client:
            yield client


def save_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as output:
        output.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")


def print_progress(completed: int, total: int) -> None:
    if completed % 10 == 0 or completed == total:
        print(f"Completed {completed}/{total}", flush=True)


async def run(args: argparse.Namespace) -> None:
    cases = load_cases(args.dataset)
    if args.reviewed_only:
        cases = [case for case in cases if case.reviewed]
    if args.case_ids:
        selected_ids = set(args.case_ids.split(","))
        if selected_ids - {case.id for case in cases}:
            raise ValueError("Unknown case IDs or cases excluded by review status")
        cases = [case for case in cases if case.id in selected_ids]
    if args.limit is not None:
        if args.limit < 1:
            raise ValueError("--limit must be positive")
        cases = cases[:args.limit]
    if not cases or args.repeat < 1:
        raise ValueError("Select at least one case and a positive repeat count")
    outputs = [args.output] if args.repeat == 1 else [
        args.output.with_name(f"{args.output.stem}-{index + 1}.json")
        for index in range(args.repeat)
    ]
    reserved_paths = outputs + ([args.output] if args.repeat > 1 else [])
    if any(path.exists() for path in reserved_paths):
        raise ValueError("Output already exists; choose a new filename")
    baseline = json.loads(args.baseline.read_text()) if args.baseline else None
    digest = hashlib.sha256(args.dataset.read_bytes()).hexdigest()
    if baseline:
        if baseline["dataset_sha256"] != digest:
            raise ValueError("Baseline uses a different dataset version")
        if {row["id"] for row in baseline["results"]} != {case.id for case in cases}:
            raise ValueError("Baseline uses a different case selection")
    if args.rescore:
        if args.repeat != 1:
            raise ValueError("Rescoring does not support repeats")
        report = rescore_report(json.loads(args.rescore.read_text()), cases, digest)
        report["label"] = args.label
        if baseline:
            report["comparison"] = compare_reports(report, baseline)
        save_report(args.output, report)
        print(json.dumps(report["summary"], indent=2))
        return
    reports = []
    async with evaluation_client(args) as client:
        for index, output in enumerate(outputs, 1):
            print(f"Run {index}/{args.repeat}: {len(cases)} cases", flush=True)
            report = await evaluate(cases, client, diagnostics=args.diagnostics, progress=print_progress)
            report.update({
                "dataset_sha256": digest,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "label": args.label,
                "url": "in-process" if args.local else args.url,
                "unreviewed_cases": sum(not case.reviewed for case in cases),
                **report_details(report["results"]),
            })
            if baseline:
                report["comparison"] = compare_reports(report, baseline)
            save_report(output, report)
            reports.append(report)
            print(json.dumps(report["summary"], indent=2), flush=True)
    if args.repeat > 1:
        save_report(args.output, {
            "label": args.label, "dataset_sha256": digest,
            "reports": [str(path) for path in outputs],
            "repeats": summarize_repeats(reports),
        })
    if any(report["summary"]["errors"] for report in reports):
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
    parser.add_argument("--case-ids", help="Comma-separated case IDs for a fixed comparison subset")
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--diagnostics", action="store_true")
    parser.add_argument("--local", action="store_true", help="Run app in-process without an HTTP server")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--rescore", type=Path, help="Rescore saved responses without calling a model")
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
