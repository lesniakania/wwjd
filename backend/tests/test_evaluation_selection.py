from app.evaluation_selection import SelectionPolicy, select_candidates
from app.retrieval_diagnostics import RankedCandidate


def candidate(reference: str, confidence: float = 0.6) -> RankedCandidate:
    return RankedCandidate(reference=reference, quotation="Test", retrieval_score=0.1,
                           confidence=confidence)


def test_relevance_policy_keeps_distinct_passages_from_same_book() -> None:
    candidates = [candidate("Matthew 6:25"), candidate("Matthew 18:15"), candidate("John 14:27")]
    assert select_candidates(candidates, SelectionPolicy.RELEVANCE, 2) == [
        "Matthew 6:25", "Matthew 18:15",
    ]
    assert select_candidates(candidates, SelectionPolicy.ONE_PER_BOOK, 2) == [
        "Matthew 6:25", "John 14:27",
    ]


def test_selection_filters_low_confidence_and_overlapping_ranges() -> None:
    candidates = [candidate("John 1:1", 0.2), candidate("Matthew 6:25-27"),
                  candidate("Matthew 6:27"), candidate("Matthew 6:28")]
    assert select_candidates(candidates, SelectionPolicy.RELEVANCE, 3) == [
        "Matthew 6:25-27", "Matthew 6:28",
    ]
