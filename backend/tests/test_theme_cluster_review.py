from scripts.theme_cluster_review import build_candidates


def test_build_candidates_combines_cluster_metrics_and_examples() -> None:
    drafts = [
        {
            "id": "cluster-1",
            "suggested_label_pl": "Pierwszy",
            "suggested_label_en": "First",
            "summary_pl": "Pierwszy opis.",
            "summary_en": "First summary.",
            "cluster_size": 10,
            "coherence": 0.8,
            "examples": [{"record_id": "one", "principle": "Care", "text": "One"}],
        },
        {
            "id": "cluster-2",
            "suggested_label_pl": "Drugi",
            "suggested_label_en": "Second",
            "summary_pl": "Drugi opis.",
            "summary_en": "Second summary.",
            "cluster_size": 30,
            "coherence": 0.6,
            "examples": [{"record_id": "two", "principle": "Care", "text": "Two"}],
        },
    ]
    review = {
        "default_action": "keep",
        "decisions": [
            {
                "action": "merge",
                "cluster_ids": ["cluster-1", "cluster-2"],
                "candidate_id": "care",
                "label_pl": "Troska",
                "label_en": "Care",
                "summary_pl": "Troska o innych.",
                "summary_en": "Care for others.",
                "reason_pl": "Ten sam problem etyczny.",
                "excluded_record_ids": ["two"],
            }
        ],
    }

    candidates = build_candidates(drafts, review)

    assert len(candidates) == 1
    assert candidates[0]["cluster_size"] == 40
    assert candidates[0]["coherence"] == 0.65
    assert candidates[0]["source_cluster_ids"] == ["cluster-1", "cluster-2"]
    assert len(candidates[0]["examples"]) == 1
    assert candidates[0]["excluded_record_ids"] == ["two"]


def test_build_candidates_omits_rejected_clusters() -> None:
    drafts = [{"id": "cluster-1"}]
    review = {
        "default_action": "keep",
        "decisions": [{
            "action": "reject",
            "cluster_ids": ["cluster-1"],
            "reason_pl": "Zbyt szeroki.",
        }],
    }

    assert build_candidates(drafts, review) == []
