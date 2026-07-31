#!/usr/bin/env python3
"""Apply human editorial decisions to generated ethical-theme clusters."""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DATA = Path(__file__).parents[1] / "app" / "data"


def decision_by_cluster(review: dict[str, Any]) -> dict[str, dict[str, Any]]:
    decisions: dict[str, dict[str, Any]] = {}
    for decision in review["decisions"]:
        for cluster_id in decision["cluster_ids"]:
            if cluster_id in decisions:
                raise ValueError(f"Duplicate editorial decision for {cluster_id}")
            decisions[cluster_id] = decision
    return decisions


def candidate_metadata(cluster: dict[str, Any], decision: dict[str, Any] | None) -> dict[str, str]:
    if decision is None:
        return {
            "id": cluster["id"],
            "label_pl": cluster["suggested_label_pl"],
            "label_en": cluster["suggested_label_en"],
            "summary_pl": cluster["summary_pl"],
            "summary_en": cluster["summary_en"],
        }
    return {
        "id": decision["candidate_id"],
        "label_pl": decision["label_pl"],
        "label_en": decision["label_en"],
        "summary_pl": decision["summary_pl"],
        "summary_en": decision["summary_en"],
    }


def build_candidates(drafts: list[dict[str, Any]], review: dict[str, Any]) -> list[dict[str, Any]]:
    decisions = decision_by_cluster(review)
    draft_ids = {cluster["id"] for cluster in drafts}
    unknown_ids = set(decisions) - draft_ids
    if unknown_ids:
        raise ValueError(f"Editorial decisions reference unknown clusters: {sorted(unknown_ids)}")

    grouped: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for cluster in drafts:
        decision = decisions.get(cluster["id"])
        if decision is not None and decision["action"] == "reject":
            continue
        metadata = candidate_metadata(cluster, decision)
        grouped[metadata["id"]].append((cluster, metadata))

    candidates: list[dict[str, Any]] = []
    for candidate_id, members in grouped.items():
        clusters = [cluster for cluster, _metadata in members]
        metadata = members[0][1]
        excluded_record_ids = sorted(
            {
                record_id
                for cluster in clusters
                for record_id in (decisions.get(cluster["id"]) or {}).get(
                    "excluded_record_ids", []
                )
            }
        )
        total_size = sum(cluster["cluster_size"] for cluster in clusters)
        coherence = sum(
            cluster["coherence"] * cluster["cluster_size"] for cluster in clusters
        ) / total_size
        examples = {
            example["record_id"]: example
            for cluster in clusters
            for example in cluster["examples"]
            if example["record_id"] not in excluded_record_ids
        }
        candidates.append(
            {
                **metadata,
                "source_cluster_ids": [cluster["id"] for cluster in clusters],
                "cluster_size": total_size,
                "coherence": round(coherence, 4),
                "examples": list(examples.values()),
                "excluded_record_ids": excluded_record_ids,
                "status": "editorial_candidate",
                "reviewed": False,
            }
        )
    return sorted(candidates, key=lambda candidate: candidate["label_pl"].casefold())


def main() -> None:
    drafts = json.loads((DATA / "theme_cluster_drafts.json").read_text(encoding="utf-8"))
    review = json.loads((DATA / "theme_cluster_review.json").read_text(encoding="utf-8"))
    candidates = build_candidates(drafts, review)
    (DATA / "theme_candidates.json").write_text(
        json.dumps(candidates, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
