import json
from pathlib import Path

from app.context import ContextRegistry
from app.retrieval import Passage


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


def test_only_explicitly_reviewed_cards_are_publishable():
    rows = json.loads(
        (Path(__file__).parents[1] / "app" / "data" / "context_cards.json").read_text()
    )
    assert rows
    assert all(row.get("reviewed") is True for row in rows)


def test_cards_represent_non_narrative_and_deuterocanonical_genres():
    registry = ContextRegistry()
    assert registry.for_passage(Passage("Psalms", 23, 4, 4, ""), "pl").literary_type == "psalm ufności"
    assert registry.for_passage(Passage("Isaiah", 58, 6, 6, ""), "pl").literary_type == "wyrocznia prorocka"
    sirach = registry.for_passage(Passage("Sirach", 11, 8, 8, ""), "en")
    assert sirach.reviewed is True
    assert "not a saying of Jesus of Nazareth" in sirach.origin_context
