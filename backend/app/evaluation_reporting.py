"""Aggregate stage diagnostics and rescore saved responses without model calls."""

from copy import deepcopy
from statistics import mean, median, stdev

from .evaluation import EvaluationCase, score_sources, stage_scores, summarize


def report_details(results: list[dict]) -> dict:
    stages = sorted({stage for row in results for stage in row.get("stage_scores", {})})
    configurations = [
        row["response"]["diagnostics"]["configuration"]
        for row in results if row.get("response", {}).get("diagnostics")
    ]
    analyses = [
        row.get("response", {}).get("diagnostics", {}).get("analysis")
        for row in results if row.get("response", {}).get("diagnostics")
    ]
    return {
        "analysis_successes": sum(value is not None and value["status"] == "success"
                                  for value in analyses),
        "analysis_fallbacks": sum(value is not None and value["status"] == "fallback"
                                  for value in analyses),
        "analysis_seconds_total": sum(value.get("seconds", 0) for value in analyses if value),
        "stages": {
            stage: {
                metric: mean(row.get("stage_scores", {}).get(stage, {}).get(metric, 0)
                             for row in results)
                for metric in ("hit", "recall", "mrr", "verse_coverage")
            }
            for stage in stages
        },
        "diagnostic_cases": len(configurations),
        "configuration": configurations[0] if configurations else None,
        "configuration_consistent": all(value == configurations[0] for value in configurations),
        "seconds_total": sum(row.get("seconds", 0) for row in results),
        "seconds_median": median(row.get("seconds", 0) for row in results) if results else 0,
        "by_category": {
            category: summarize([row for row in results if row["category"] == category])
            for category in sorted({row["category"] for row in results})
        },
    }


def rescore_report(report: dict, cases: list[EvaluationCase], digest: str) -> dict:
    revised = deepcopy(report)
    cases_by_id = {case.id: case for case in cases}
    if set(cases_by_id) != {row["id"] for row in revised["results"]}:
        raise ValueError("Rescoring requires exactly the same case IDs")
    for row in revised["results"]:
        case = cases_by_id[row["id"]]
        if case.situation != row["situation"]:
            raise ValueError(f"Cannot rescore a changed situation: {case.id}")
        row["category"] = case.category
        row["expected"] = [source.reference for source in case.expected_sources]
        actual = [] if "error" in row else [
            source["reference"] for source in row["response"]["sources"]
        ]
        row["scores"] = score_sources(actual, row["expected"])
        if "error" not in row and row.get("response", {}).get("diagnostics"):
            row["stage_scores"] = stage_scores(row["response"], row["expected"])
    revised.pop("comparison", None)
    revised["original_dataset_sha256"] = report["dataset_sha256"]
    revised["dataset_sha256"] = digest
    revised["summary"] = summarize(revised["results"])
    revised.update(report_details(revised["results"]))
    return revised


def summarize_repeats(reports: list[dict]) -> dict:
    return {
        metric: {
            "mean": mean(report["summary"][metric] for report in reports),
            "stdev": stdev(report["summary"][metric] for report in reports)
            if len(reports) > 1 else 0,
            "values": [report["summary"][metric] for report in reports],
        }
        for metric in ("hit", "precision", "recall", "mrr", "errors", "local_extractive")
    }
