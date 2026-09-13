from app.review_comparison import summarize_ratings


def test_uncertain_is_reported_and_excluded_from_precision() -> None:
    result = summarize_ratings(["direct", "supporting", "irrelevant", "uncertain"])
    assert result["judged"] == 3
    assert result["uncertain"] == 1
    assert result["strict_precision"] == 1 / 3
    assert result["inclusive_precision"] == 2 / 3


def test_no_decided_ratings_has_no_precision() -> None:
    assert summarize_ratings([None, "uncertain"])["inclusive_precision"] is None
