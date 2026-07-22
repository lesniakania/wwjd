import json
from pathlib import Path

from app.context import ContextRegistry
from app.retrieval import Passage, THEME_ANCHORS


def test_proverbs_18_is_a_reviewed_wisdom_saying_not_a_scene():
    card = ContextRegistry().for_passage(Passage("Proverbs", 18, 13, 13, ""), "pl")
    assert card.reviewed is True
    assert card.literary_type == "maksyma mądrościowa"
    assert "nie jest wypowiedź Jezusa" in card.origin_context
    assert "przypowieści" in card.origin_context


def test_unreviewed_passage_uses_an_honest_stable_fallback():
    registry = ContextRegistry()
    first = registry.for_passage(Passage("Genesis", 40, 1, 1, ""), "pl")
    second = registry.for_passage(Passage("Genesis", 40, 1, 1, ""), "pl")
    assert first == second
    assert first.reviewed is False
    assert first.confidence == "limited"
    assert "Nie mamy jeszcze zatwierdzonej karty" in first.origin_context


def test_draft_cards_are_not_published():
    rows = json.loads(
        (Path(__file__).parents[1] / "app" / "data" / "context_cards.json").read_text()
    )
    assert rows
    draft = next(row for row in rows if row.get("reviewed") is False)
    card = ContextRegistry().for_passage(
        Passage(draft["book"], draft["chapter_start"], draft["verse_start"], draft["verse_start"], ""),
        "pl",
    )
    assert card.reviewed is False
    assert card.fallback is True


def test_cards_represent_non_narrative_and_deuterocanonical_genres():
    registry = ContextRegistry()
    assert registry.for_passage(Passage("Psalms", 23, 4, 4, ""), "pl").literary_type == "psalm ufności"
    assert registry.for_passage(Passage("Isaiah", 58, 6, 6, ""), "pl").literary_type == "wyrocznia prorocka"
    sirach = registry.for_passage(Passage("Sirach", 11, 8, 8, ""), "en")
    assert sirach.reviewed is True
    assert "not a saying of Jesus of Nazareth" in sirach.origin_context


def test_every_theme_anchor_has_a_reviewed_card_or_editorial_draft():
    registry = ContextRegistry()
    for anchors in THEME_ANCHORS.values():
        for book, chapter, verse_start, _ in anchors:
            point = Passage(book, chapter, verse_start, verse_start, "")
            assert any(registry._contains(row, point) for row in registry.rows), point.reference
