import json
import sys
import warnings
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from app import retrieval
from app.retrieval import BgeReranker, THEME_ANCHORS, Passage, Retriever, SemanticEncoder
from app.themes import Theme


DATA = Path(__file__).parents[1] / "app" / "data" / "web_verses.json"


class FakeOnnxTextEmbedding:
    init_arguments: dict[str, object] = {}
    encoded_batches: list[list[str]] = []

    def __init__(self, model_name: str, **kwargs: object) -> None:
        self.init_arguments = {"model_name": model_name, **kwargs}
        FakeOnnxTextEmbedding.init_arguments = self.init_arguments

    def embed(self, texts: list[str], batch_size: int) -> object:
        FakeOnnxTextEmbedding.encoded_batches.append(texts)
        return iter(np.asarray([index + 1.0, 2.0]) for index, _ in enumerate(texts))


class WarningOnnxTextEmbedding(FakeOnnxTextEmbedding):
    def __init__(self, model_name: str, **kwargs: object) -> None:
        warnings.warn(
            f"The model {model_name} now uses mean pooling instead of CLS embedding. "
            "In order to preserve the previous behaviour, consider either pinning fastembed "
            "version to 0.5.1 or using `add_custom_model` functionality.",
            UserWarning,
            stacklevel=2,
        )
        super().__init__(model_name, **kwargs)


def test_semantic_encoder_uses_onnx_runtime(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(retrieval, "TextEmbedding", FakeOnnxTextEmbedding)
    monkeypatch.setattr(retrieval, "MODEL_CACHE", tmp_path)

    encoder = SemanticEncoder("example/onnx-model")
    embeddings = encoder.encode(["first", "second"])

    assert FakeOnnxTextEmbedding.init_arguments == {
        "model_name": "example/onnx-model",
        "cache_dir": str(tmp_path),
    }
    assert FakeOnnxTextEmbedding.encoded_batches[-1] == ["first", "second"]
    assert embeddings.dtype == np.float32
    np.testing.assert_allclose(np.linalg.norm(embeddings, axis=1), [1.0, 1.0])


def test_semantic_encoder_returns_one_vector_for_one_text(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(retrieval, "TextEmbedding", FakeOnnxTextEmbedding)
    monkeypatch.setattr(retrieval, "MODEL_CACHE", tmp_path)

    embedding = SemanticEncoder("example/onnx-model").encode("only")

    assert embedding.shape == (2,)


def test_semantic_encoder_suppresses_fastembed_pooling_warning(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(retrieval, "TextEmbedding", WarningOnnxTextEmbedding)
    monkeypatch.setattr(retrieval, "MODEL_CACHE", tmp_path)

    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        SemanticEncoder("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    assert caught_warnings == []


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


class ControlledReranker:
    def rerank(self, query: str, passages: list[Passage]) -> np.ndarray:
        assert query == "Which passage best addresses fear?"
        assert [passage.reference for passage in passages] == [
            "Matthew 6:25",
            "Philippians 4:6",
            "John 14:27",
        ]
        return np.asarray([0.2, 0.9, 0.5], dtype=np.float32)


def test_reranker_reorders_only_the_configured_candidate_window(tmp_path: Path) -> None:
    verses_path = tmp_path / "verses.json"
    verses_path.write_text(
        json.dumps(
            [
                {
                    "book": "Matthew",
                    "chapter": 6,
                    "verse": 25,
                    "text": "Do not be anxious about your life.",
                },
                {
                    "book": "Philippians",
                    "chapter": 4,
                    "verse": 6,
                    "text": "Do not be anxious about anything, but pray.",
                },
                {
                    "book": "John",
                    "chapter": 14,
                    "verse": 27,
                    "text": "Let not your hearts be troubled, neither let them be afraid.",
                },
            ]
        ),
        encoding="utf-8",
    )
    retriever = Retriever(verses_path, reranker=ControlledReranker(), reranker_candidates=3)
    candidates = [
        (0, 0.9, 0.9),
        (1, 0.8, 0.8),
        (2, 0.7, 0.7),
    ]

    reranked = retriever._rerank("Which passage best addresses fear?", candidates)

    assert [index for index, _, _ in reranked] == [1, 2, 0]


def test_bge_reranker_scores_query_passage_pairs(monkeypatch, tmp_path: Path) -> None:
    initialized_with: dict[str, str] = {}

    class FakeCrossEncoder:
        def __init__(self, model_name: str, cache_folder: str) -> None:
            initialized_with.update(model_name=model_name, cache_folder=cache_folder)

        def predict(self, pairs: list[tuple[str, str]]) -> list[float]:
            assert pairs == [("query", "First text"), ("query", "Second text")]
            return [0.2, 0.9]

    monkeypatch.setattr(retrieval, "MODEL_CACHE", tmp_path)
    monkeypatch.setitem(sys.modules, "sentence_transformers", SimpleNamespace(CrossEncoder=FakeCrossEncoder))

    scores = BgeReranker("BAAI/bge-reranker-v2-m3").rerank(
        "query",
        [
            Passage("Matthew", 1, 1, 1, "First text"),
            Passage("Mark", 1, 1, 1, "Second text"),
        ],
    )

    assert initialized_with == {
        "model_name": "BAAI/bge-reranker-v2-m3",
        "cache_folder": str(tmp_path),
    }
    np.testing.assert_allclose(scores, [0.2, 0.9])


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
