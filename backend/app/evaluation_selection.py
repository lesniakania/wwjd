"""Offline selection ablations on an identical, already ranked candidate pool."""

from collections import Counter
from enum import StrEnum

from .evaluation import parse_reference
from .retrieval_diagnostics import RankedCandidate


class SelectionPolicy(StrEnum):
    ONE_PER_BOOK = "one_per_book"
    TWO_PER_BOOK = "two_per_book"
    RELEVANCE = "relevance"


def select_candidates(
    candidates: list[RankedCandidate], policy: SelectionPolicy, limit: int = 6,
) -> list[str]:
    if limit < 1:
        raise ValueError("limit must be positive")
    book_limit = {SelectionPolicy.ONE_PER_BOOK: 1, SelectionPolicy.TWO_PER_BOOK: 2,
                  SelectionPolicy.RELEVANCE: limit}[policy]
    selected: list[str] = []
    seen_verses: set[tuple[str, int, int]] = set()
    books: Counter[str] = Counter()
    for candidate in candidates:
        verses = parse_reference(candidate.reference)
        book = next(iter(verses))[0]
        if candidate.confidence < 0.36 or books[book] >= book_limit or verses & seen_verses:
            continue
        selected.append(candidate.reference)
        seen_verses.update(verses)
        books[book] += 1
        if len(selected) == limit:
            break
    return selected
