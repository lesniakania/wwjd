import json
from pathlib import Path

import numpy as np

from app.retrieval import THEME_ANCHORS
from app.themes import Theme


DATA = Path(__file__).parents[1] / "app" / "data"
CLUSTER_DRAFTS = DATA / "theme_cluster_drafts.json"
CLUSTER_CENTROIDS = DATA / "theme_cluster_centroids.npy"
PRINCIPLE_CACHE = DATA / "theme_principle_cache.json"
CATALOG_REVIEW = DATA / "theme_catalog_review.md"
CLUSTER_REVIEW = DATA / "theme_cluster_review.json"
THEME_CANDIDATES = DATA / "theme_candidates.json"
CANDIDATE_ALIGNMENT = DATA / "theme_candidate_alignment.json"


def test_cluster_drafts_are_unreviewed_and_have_ethics_provenance() -> None:
    rows = json.loads(CLUSTER_DRAFTS.read_text(encoding="utf-8"))
    centroids = np.load(CLUSTER_CENTROIDS)
    principles = json.loads(PRINCIPLE_CACHE.read_text(encoding="utf-8"))

    assert len(rows) >= 80
    assert len(principles) == 6000
    assert centroids.shape[0] == len(rows)
    assert len({row["id"] for row in rows}) == len(rows)
    assert all(row["source"] == "ETHICS commonsense" for row in rows)
    assert all(row["license"] == "MIT" for row in rows)
    assert all(row["status"] == "draft" and row["reviewed"] is False for row in rows)
    assert all(row["theme"] is None and len(row["examples"]) >= 3 for row in rows)
    assert all(row["suggested_label_en"] and row["suggested_label_pl"] for row in rows)
    assert all(row["summary_en"] and row["summary_pl"] for row in rows)
    assert all(0.0 <= row["coherence"] <= 1.0 for row in rows)
    assert all(example["principle"] for row in rows for example in row["examples"])


def test_catalog_review_contains_every_theme_and_anchor() -> None:
    report = CATALOG_REVIEW.read_text(encoding="utf-8")

    for theme in Theme:
        assert f"## {theme}" in report
        for book, chapter, verse_start, verse_end in THEME_ANCHORS[str(theme)]:
            verses = str(verse_start) if verse_start == verse_end else f"{verse_start}–{verse_end}"
            assert f"{book} {chapter}:{verses}" in report


def test_catalog_review_has_explicit_editorial_decisions() -> None:
    report = CATALOG_REVIEW.read_text(encoding="utf-8")

    assert report.count("- [ ] Approve theme") == len(Theme)
    assert report.count("- [ ] Request changes") == len(Theme)
    assert "Polish display name: Gniew i odwet" in report
    assert "Polish display name: gniewu i reagowania bez odwetu" not in report


def test_cluster_review_references_every_changed_cluster_once() -> None:
    drafts = json.loads(CLUSTER_DRAFTS.read_text(encoding="utf-8"))
    review = json.loads(CLUSTER_REVIEW.read_text(encoding="utf-8"))
    draft_ids = {row["id"] for row in drafts}
    reviewed_ids = [cluster_id for row in review["decisions"] for cluster_id in row["cluster_ids"]]

    assert review["default_action"] == "keep"
    assert len(reviewed_ids) == len(set(reviewed_ids))
    assert set(reviewed_ids) <= draft_ids
    assert {row["action"] for row in review["decisions"]} <= {"merge", "rename", "reject"}
    assert all(row["reason_pl"] for row in review["decisions"])


def test_theme_candidates_apply_merges_renames_and_rejections() -> None:
    review = json.loads(CLUSTER_REVIEW.read_text(encoding="utf-8"))
    candidates = json.loads(THEME_CANDIDATES.read_text(encoding="utf-8"))
    rejected_ids = {
        cluster_id
        for decision in review["decisions"]
        if decision["action"] == "reject"
        for cluster_id in decision["cluster_ids"]
    }
    included_ids = {
        cluster_id for candidate in candidates for cluster_id in candidate["source_cluster_ids"]
    }

    assert rejected_ids.isdisjoint(included_ids)
    assert len({candidate["id"] for candidate in candidates}) == len(candidates)
    assert len({candidate["label_pl"] for candidate in candidates}) == len(candidates)
    assert all(candidate["status"] == "editorial_candidate" for candidate in candidates)
    assert all(candidate["reviewed"] is False for candidate in candidates)
    animal_welfare = next(row for row in candidates if row["id"] == "animal_welfare")
    assert len(animal_welfare["source_cluster_ids"]) == 4
    assert animal_welfare["label_pl"] == "Dobrostan zwierząt"
    assert len(candidates) <= 50
    assert all(candidate["label_pl"] != "Interakcje z dziećmi" for candidate in candidates)
    dignity = next(row for row in candidates if row["id"] == "dignity_and_inclusion")
    assert "ethics:commonsense:train:6095" in dignity["excluded_record_ids"]


def test_every_candidate_has_one_catalog_alignment_decision() -> None:
    candidates = json.loads(THEME_CANDIDATES.read_text(encoding="utf-8"))
    alignment = json.loads(CANDIDATE_ALIGNMENT.read_text(encoding="utf-8"))
    candidate_ids = {candidate["id"] for candidate in candidates}
    covered_ids = [
        candidate_id
        for group in alignment["covered_by_existing"]
        for candidate_id in group["candidate_ids"]
    ]
    proposed_ids = [
        candidate_id
        for proposal in alignment["new_theme_proposals"]
        for candidate_id in proposal["candidate_ids"]
    ]

    assert len(covered_ids + proposed_ids) == len(set(covered_ids + proposed_ids))
    assert set(covered_ids + proposed_ids) == candidate_ids
    assert alignment["existing_theme_count"] + len(alignment["new_theme_proposals"]) == len(Theme)
    assert alignment["candidate_count"] == len(candidates)
    assert all(
        Theme(theme)
        for group in alignment["covered_by_existing"]
        for theme in group["existing_themes"]
    )


def test_new_theme_proposals_are_unreviewed_and_bilingual() -> None:
    alignment = json.loads(CANDIDATE_ALIGNMENT.read_text(encoding="utf-8"))
    proposals = alignment["new_theme_proposals"]

    assert {proposal["id"] for proposal in proposals} == {
        "boundaries_consent_privacy",
        "dignity_and_respect",
        "stewardship",
    }
    assert all(proposal["label_pl"] and proposal["label_en"] for proposal in proposals)
    assert all(proposal["summary_pl"] and proposal["summary_en"] for proposal in proposals)
    assert all(proposal["status"] == "approved" and proposal["reviewed"] is True for proposal in proposals)
