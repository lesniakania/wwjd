import json
from pathlib import Path
from urllib.parse import urlparse

from app.context import ContextRegistry
from app.context_sources import context_source
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


def test_draft_cards_are_not_published(tmp_path):
    rows = json.loads(
        (Path(__file__).parents[1] / "app" / "data" / "context_cards.json").read_text(
            encoding="utf-8"
        )
    )
    assert rows
    draft = {**rows[0], "id": "test-draft", "reviewed": False}
    draft_path = tmp_path / "context_cards.json"
    draft_path.write_text(json.dumps([draft]), encoding="utf-8")

    card = ContextRegistry(draft_path).for_passage(
        Passage(
            draft["book"], draft["chapter_start"], draft["verse_start"], draft["verse_start"], ""
        ),
        "pl",
    )
    assert card.reviewed is False
    assert card.fallback is True


def test_cards_represent_non_narrative_and_deuterocanonical_genres():
    registry = ContextRegistry()
    assert (
        registry.for_passage(Passage("Psalms", 23, 4, 4, ""), "pl").literary_type == "psalm ufności"
    )
    assert (
        registry.for_passage(Passage("Isaiah", 58, 6, 6, ""), "pl").literary_type
        == "wyrocznia prorocka"
    )
    sirach = registry.for_passage(Passage("Sirach", 11, 8, 8, ""), "en")
    assert sirach.reviewed is True
    assert "not a saying of Jesus of Nazareth" in sirach.origin_context


def test_every_theme_anchor_has_a_reviewed_card_or_editorial_draft():
    registry = ContextRegistry()
    for anchors in THEME_ANCHORS.values():
        for book, chapter, verse_start, _ in anchors:
            point = Passage(book, chapter, verse_start, verse_start, "")
            assert any(registry._contains(row, point) for row in registry.rows), point.reference


def test_context_sources_link_to_authoritative_material():
    scripture = context_source("Matthew 5:1–7:29", "en")
    assert scripture.label == "Matthew 5:1–7:29"
    assert scripture.url == "https://bible.usccb.org/bible/matthew/5"

    catechism = context_source("Catechism of the Catholic Church 1965–1986", "en")
    assert catechism.url.startswith("https://www.vatican.va/")


def test_context_sources_are_localized_for_polish_responses():
    scripture = context_source("Matthew 5:1–7:29", "pl")
    assert scripture.label == "Mateusza 5:1–7:29 (UBG)"
    assert scripture.url == "https://www.bible.com/pl/bible/138/MAT.5.UBG"

    notes = context_source("USCCB, Matthew 5 notes", "pl")
    assert notes.label == "Mateusza 5 — tekst biblijny (UBG)"
    assert notes.url == "https://www.bible.com/pl/bible/138/MAT.5.UBG"

    catechism = context_source("Catechism of the Catholic Church 1965–1986", "pl")
    assert catechism.label == "Katechizm Kościoła Katolickiego 1965–1986"
    assert catechism.url == "https://www.katechizm.opoka.org.pl/"


def test_every_reviewed_context_source_has_a_trusted_https_link():
    trusted_hosts = {"bible.usccb.org", "www.vatican.va", "www.openbible.info", "berean.bible"}
    registry = ContextRegistry()

    for row in registry.rows:
        for label in row["context_sources"]:
            parsed_url = urlparse(context_source(label, "en").url)
            assert parsed_url.scheme == "https", label
            assert parsed_url.hostname in trusted_hosts, label
