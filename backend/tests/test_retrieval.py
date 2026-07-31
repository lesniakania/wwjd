import json
from pathlib import Path

import numpy as np

from app.retrieval import THEME_ANCHORS, Retriever
from app.themes import Theme


DATA = Path(__file__).parents[1] / "app" / "data" / "web_verses.json"


def test_every_theme_anchor_exists_in_both_corpora() -> None:
    for corpus_path in (DATA, DATA.with_name("polubg_verses.json")):
        rows = json.loads(corpus_path.read_text(encoding="utf-8"))
        available_verses = {
            (row["book"], row["chapter"], row["verse"])
            for row in rows
        }
        for anchors in THEME_ANCHORS.values():
            for book, chapter, verse_start, verse_end in anchors:
                assert all(
                    (book, chapter, verse) in available_verses
                    for verse in range(verse_start, verse_end + 1)
                ), f"Missing anchor in {corpus_path.name}: {book} {chapter}:{verse_start}-{verse_end}"


def test_retrieval_finds_relevant_passages():
    retriever = Retriever(DATA)
    results = retriever.search("How can I forgive someone who hurt me?", limit=5)
    assert 1 <= len(results) <= 5
    combined = " ".join(result.passage.text.lower() for result in results)
    assert "forgiv" in combined


def test_references_are_well_formed():
    retriever = Retriever(DATA)
    result = retriever.search("love your enemy", limit=1)[0]
    assert ":" in result.passage.reference
    assert result.passage.text


def test_everyday_conflict_expands_to_ethical_themes():
    retriever = Retriever(DATA)
    results = retriever.search(
        "A colleague took credit for my work and I want to embarrass them publicly.", limit=5
    )
    combined = " ".join(result.passage.text.lower() for result in results)
    assert any(word in combined for word in ("anger", "gentle", "peace", "reconcile", "forgive"))


def test_displayed_context_is_wide_enough_to_show_the_surrounding_situation():
    retriever = Retriever(DATA)
    passage = next(
        passage
        for passage in retriever.passages
        if passage.book == "Matthew" and passage.chapter == 18 and passage.verse_start == 17
    )
    context = retriever.context_for(passage, radius=5)
    assert context.verse_start == 12
    assert context.verse_end == 22


class ControlledEncoder:
    model_name = "controlled-test-encoder"

    def encode(self, texts: str | list[str]) -> np.ndarray:
        if isinstance(texts, list):
            return np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
        return np.asarray([0.0, 1.0], dtype=np.float32)


class PrejudiceThemeRouter:
    def classify(
        self,
        text: str,
        excluded: set[Theme] | None = None,
    ) -> dict[Theme, float]:
        return {Theme.PREJUDICE: 0.7}


def test_theme_anchors_do_not_hide_strong_semantic_results(tmp_path: Path) -> None:
    verses_path = tmp_path / "verses.json"
    verses_path.write_text(
        json.dumps(
            [
                {
                    "book": "Matthew",
                    "chapter": 18,
                    "verse": 21,
                    "text": "How often shall my brother sin against me, and I forgive him?",
                },
                {
                    "book": "John",
                    "chapter": 11,
                    "verse": 35,
                    "text": "Jesus wept.",
                },
            ]
        ),
        encoding="utf-8",
    )

    results = Retriever(verses_path, encoder=ControlledEncoder()).search(
        "How can I forgive after a painful loss?",
        limit=2,
    )

    assert {result.passage.reference for result in results} == {
        "Matthew 18:21",
        "John 11:35",
    }


def test_semantic_theme_adds_general_ethical_anchor(tmp_path: Path) -> None:
    verses_path = tmp_path / "verses.json"
    verses_path.write_text(
        json.dumps(
            [
                {
                    "book": "Luke",
                    "chapter": 10,
                    "verse": 27,
                    "text": "You shall love your neighbor as yourself.",
                },
                {
                    "book": "John",
                    "chapter": 11,
                    "verse": 35,
                    "text": "Jesus wept.",
                },
            ]
        ),
        encoding="utf-8",
    )

    results = Retriever(
        verses_path,
        encoder=ControlledEncoder(),
        theme_router=PrejudiceThemeRouter(),
    ).search("Jednostkowe zachowanie stało się podstawą oceny całej grupy.", limit=2)

    neighbor_result = next(
        result for result in results if result.passage.reference == "Luke 10:27"
    )
    assert neighbor_result.themes == ("prejudice",)
