"""Summaries of human relevance judgments; uncertainty is not a negative judgment."""

from collections import Counter


def summarize_ratings(ratings: list[str | None]) -> dict:
    allowed = {None, "direct", "supporting", "irrelevant", "uncertain"}
    if any(rating not in allowed for rating in ratings):
        raise ValueError("Unknown passage rating")
    counts = Counter(ratings)
    judged = sum(counts[value] for value in ("direct", "supporting", "irrelevant"))
    return {
        "total": len(ratings), "judged": judged, "uncertain": counts["uncertain"],
        "unreviewed": counts[None],
        "strict_precision": counts["direct"] / judged if judged else None,
        "inclusive_precision": (counts["direct"] + counts["supporting"]) / judged
        if judged else None,
        "counts": {value: counts[value] for value in ("direct", "supporting", "irrelevant")},
    }
