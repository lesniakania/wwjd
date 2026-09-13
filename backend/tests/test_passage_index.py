import numpy as np

from app.passage_index import contextual_passages, rank_embeddings, embedding_fingerprint
from app.retrieval_models import Verse


def test_context_stays_in_chapter_and_keeps_central_verse_alignment() -> None:
    verses = [Verse("John", 1, 1, "a"), Verse("John", 1, 2, "b"),
              Verse("John", 1, 3, "c"), Verse("John", 2, 1, "d")]
    passages = contextual_passages(verses)
    assert [passage.reference for passage in passages] == [
        "John 1:1–2", "John 1:1–3", "John 1:2–3", "John 2:1",
    ]
    assert passages[1].text == "a b c"
    assert passages[3].text == "d"


def test_ranking_uses_similarity_with_stable_ties() -> None:
    vectors = np.array([[1., 0.], [0., 1.], [1., 0.]], dtype=np.float32)
    assert rank_embeddings(vectors, np.array([1., 0.]), 2) == [0, 2]


def test_cache_fingerprint_includes_model_and_text() -> None:
    assert embedding_fingerprint("model", ["one"]) != embedding_fingerprint("other", ["one"])
    assert embedding_fingerprint("model", ["one"]) != embedding_fingerprint("model", ["two"])
