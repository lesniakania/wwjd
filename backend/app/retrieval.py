import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np

from .retrieval_models import Passage, SearchResult, Verse
from .themes import SemanticThemeRouter, Theme, ThemeClassifier

TOKEN_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
GOSPELS = {"Matthew", "Mark", "Luke", "John"}
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for", "from",
    "had", "has", "have", "he", "her", "him", "his", "i", "if", "in", "is", "it", "me",
    "my", "of", "on", "or", "our", "she", "so", "that", "the", "their", "them", "they",
    "this", "to", "was", "we", "were", "what", "when", "with", "would", "you", "your",
    "ale", "bez", "być", "co", "czy", "dla", "do", "go", "i", "ich", "jak", "jest",
    "mi", "mnie", "na", "nie", "o", "od", "po", "się", "to", "w", "we", "z", "za",
}
THEME_ANCHORS = {
    "anger": (
        ("Matthew", 5, 22, 22), ("Matthew", 5, 24, 24),
        ("Luke", 6, 27, 27), ("Luke", 6, 31, 31), ("Luke", 6, 35, 35),
        ("James", 1, 19, 20),
    ),
    "honesty": (
        ("Matthew", 5, 37, 37), ("Ephesians", 4, 25, 25),
        ("Proverbs", 12, 17, 17), ("Proverbs", 12, 22, 22),
    ),
    "forgiveness": (
        ("Matthew", 18, 21, 22), ("Matthew", 18, 33, 33), ("Matthew", 18, 35, 35),
        ("Luke", 17, 3, 4), ("Colossians", 3, 13, 13),
    ),
    "conflict": (
        ("Matthew", 18, 15, 17), ("Romans", 12, 17, 19), ("Romans", 12, 21, 21),
        ("James", 3, 17, 18),
    ),
    "fear": (
        ("Matthew", 6, 25, 25), ("Matthew", 6, 27, 27),
        ("Matthew", 6, 31, 31), ("Matthew", 6, 34, 34),
        ("John", 14, 27, 27), ("Philippians", 4, 6, 7),
    ),
    "generosity": (
        ("Matthew", 6, 19, 21), ("Matthew", 6, 24, 24),
        ("Luke", 10, 33, 34), ("Luke", 10, 36, 37), ("1 John", 3, 17, 18),
    ),
    "prejudice": (
        ("Luke", 10, 27, 27), ("Luke", 10, 33, 34), ("Luke", 10, 36, 37),
        ("Leviticus", 19, 33, 34), ("James", 2, 1, 4), ("James", 2, 8, 9),
    ),
    "discernment": (
        ("Exodus", 23, 1, 2), ("Proverbs", 18, 13, 13),
        ("Proverbs", 18, 17, 17), ("1 Thessalonians", 5, 21, 22),
    ),
    "grief": (
        ("Genesis", 50, 1, 4), ("2 Samuel", 1, 17, 27),
        ("Psalms", 130, 1, 6), ("Romans", 12, 15, 15),
    ),
    "loneliness": (
        ("Psalms", 22, 1, 2), ("Psalms", 23, 4, 4),
        ("Lamentations", 1, 1, 2), ("Matthew", 28, 20, 20),
    ),
    "repentance": (
        ("Psalms", 51, 1, 4), ("Isaiah", 1, 16, 18),
        ("Luke", 3, 8, 14), ("Zechariah", 1, 3, 6),
    ),
    "hope": (
        ("Psalms", 23, 4, 6), ("Psalms", 130, 5, 8),
        ("Romans", 12, 12, 12), ("Philippians", 4, 6, 7),
    ),
    "envy": (
        ("Matthew", 6, 24, 24), ("Romans", 12, 15, 15),
        ("James", 3, 14, 16),
    ),
    "humility": (
        ("Romans", 12, 16, 16), ("Colossians", 3, 12, 13),
        ("James", 3, 13, 13),
    ),
    "self_control": (
        ("Proverbs", 1, 10, 15), ("Mark", 9, 43, 48),
        ("Luke", 22, 40, 46), ("James", 1, 19, 21),
    ),
    "justice": (
        ("Exodus", 23, 2, 3), ("Exodus", 23, 6, 9),
        ("Isaiah", 58, 6, 7), ("James", 2, 8, 9),
    ),
    "responsibility": (
        ("Proverbs", 31, 27, 27), ("Matthew", 18, 15, 17),
        ("Colossians", 3, 17, 17), ("James", 1, 22, 25),
    ),
    "compassion": (
        ("Matthew", 14, 14, 16), ("Luke", 10, 33, 37),
        ("Colossians", 3, 12, 13), ("1 John", 3, 17, 18),
    ),
    "boundaries_consent_privacy": (
        ("Matthew", 18, 15, 17), ("Romans", 12, 10, 10),
        ("Romans", 12, 17, 18), ("James", 2, 8, 8),
    ),
    "dignity_and_respect": (
        ("Luke", 10, 27, 27), ("Romans", 12, 10, 10),
        ("Romans", 12, 16, 16), ("James", 2, 1, 4), ("James", 2, 8, 9),
    ),
    "stewardship": (
        ("Genesis", 1, 1, 2), ("Matthew", 6, 19, 21),
        ("Proverbs", 31, 27, 27), ("James", 1, 22, 25),
    ),
}


def tokenize(text: str) -> list[str]:
    return [token for token in TOKEN_RE.findall(text.lower()) if token not in STOPWORDS]


def query_themes(text: str) -> set[str]:
    return set(query_theme_confidences(text))


def query_theme_confidences(text: str) -> dict[str, float]:
    return {
        str(theme): confidence
        for theme, confidence in ThemeClassifier().classify_with_confidence(text).items()
    }


class SemanticEncoder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        model_cache = Path(__file__).parent / "data" / "models"
        try:
            self.model = SentenceTransformer(
                model_name, cache_folder=str(model_cache), local_files_only=True
            )
        except OSError:
            self.model = SentenceTransformer(model_name, cache_folder=str(model_cache))

    def encode(self, texts: str | list[str]) -> np.ndarray:
        return np.asarray(
            self.model.encode(
                texts,
                batch_size=256,
                show_progress_bar=isinstance(texts, list) and len(texts) > 100,
                normalize_embeddings=True,
            ),
            dtype=np.float32,
        )


class Retriever:
    """Hybrid verse retriever: semantic similarity + BM25 + cautious thematic priors."""

    def __init__(
        self,
        verses_path: Path,
        encoder: SemanticEncoder | None = None,
        cache_path: Path | None = None,
        theme_router: SemanticThemeRouter | None = None,
    ):
        rows = json.loads(verses_path.read_text(encoding="utf-8"))
        self.verses = [Verse(**row) for row in rows]
        self.passages = [Passage(v.book, v.chapter, v.verse, v.verse, v.text) for v in self.verses]
        self.encoder = encoder
        self.theme_router = theme_router
        self._tokens = [Counter(tokenize(verse.text)) for verse in self.verses]
        self._document_frequency: Counter[str] = Counter()
        for counts in self._tokens:
            self._document_frequency.update(counts.keys())
        self._embeddings = self._load_or_build_embeddings(cache_path)

    def _load_or_build_embeddings(self, cache_path: Path | None) -> np.ndarray | None:
        if self.encoder is None:
            return None
        if cache_path and cache_path.exists():
            cached = np.load(cache_path)
            if cached.shape[0] == len(self.verses):
                return cached
        embeddings = self.encoder.encode([verse.text for verse in self.verses])
        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(cache_path, embeddings)
        return embeddings

    @staticmethod
    def cache_name(source: Path, model_name: str) -> Path:
        fingerprint = hashlib.sha256(model_name.encode()).hexdigest()[:10]
        return source.with_name(f"{source.stem}_{fingerprint}.npy")

    def _lexical_scores(self, query: str) -> np.ndarray:
        query_tokens = Counter(tokenize(query))
        scores = np.zeros(len(self.verses), dtype=np.float32)
        average_length = sum(map(len, self._tokens)) / max(len(self._tokens), 1)
        corpus_size = len(self.verses)
        for index, counts in enumerate(self._tokens):
            length = max(sum(counts.values()), 1)
            for token, query_count in query_tokens.items():
                frequency = counts.get(token, 0)
                if not frequency:
                    continue
                inverse_frequency = math.log(
                    1 + (corpus_size - self._document_frequency[token] + 0.5)
                    / (self._document_frequency[token] + 0.5)
                )
                normalized = frequency * 2.2 / (frequency + 1.2 * (0.25 + 0.75 * length / average_length))
                scores[index] += inverse_frequency * normalized * min(query_count, 2)
        return scores

    def search(self, query: str, limit: int = 4) -> list[SearchResult]:
        theme_confidences = query_theme_confidences(query)
        if self.theme_router is not None:
            semantic_themes = {
                str(theme): confidence
                for theme, confidence in self.theme_router.classify(
                    query,
                    excluded={Theme(theme) for theme in theme_confidences},
                ).items()
            }
            for theme, confidence in semantic_themes.items():
                theme_confidences[theme] = max(theme_confidences.get(theme, 0.0), confidence)
        themes = set(theme_confidences)
        lexical = self._lexical_scores(query)
        semantic = np.zeros(len(self.verses), dtype=np.float32)
        if self.encoder is not None and self._embeddings is not None:
            query_embedding = self.encoder.encode(query)
            semantic = self._embeddings @ query_embedding

        lexical_order = np.argsort(lexical)[::-1][:80]
        semantic_order = np.argsort(semantic)[::-1][:80]
        candidates = set(lexical_order.tolist()) | set(semantic_order.tolist())
        for index, passage in enumerate(self.passages):
            if self._is_anchor(passage, themes):
                candidates.add(index)

        lexical_rank = {index: rank for rank, index in enumerate(lexical_order, start=1)}
        semantic_rank = {index: rank for rank, index in enumerate(semantic_order, start=1)}
        scored: list[tuple[int, float, float]] = []
        for index in candidates:
            passage = self.passages[index]
            anchor = self._is_anchor(passage, themes)
            fused = 0.0
            if index in semantic_rank:
                fused += 1 / (50 + semantic_rank[index])
            if index in lexical_rank and lexical[index] > 0:
                fused += 0.25 / (50 + lexical_rank[index])
            if anchor:
                anchor_confidence = max(
                    confidence
                    for theme, confidence in theme_confidences.items()
                    if self._is_anchor(passage, {theme})
                )
                fused += 0.025 + 0.02 * anchor_confidence
            if passage.book in GOSPELS:
                fused += 0.002
            confidence = float(semantic[index]) if self._embeddings is not None else 0.0
            if lexical[index] > 0:
                confidence = max(confidence, min(0.72, 0.32 + float(lexical[index]) / 25))
            if anchor:
                confidence = max(confidence, 0.5 + 0.08 * anchor_confidence)
            scored.append((index, fused, confidence))
        scored.sort(key=lambda item: item[1], reverse=True)

        # Give each detected concern a chance to contribute evidence. Without
        # this, four passages about one strong theme can crowd out an equally
        # important concern such as verifying a viral allegation.
        if len(themes) > 1:
            preferred: list[tuple[int, float, float]] = []
            preferred_indexes: set[int] = set()
            for theme in sorted(themes):
                match = next(
                    (
                        item
                        for item in scored
                        if item[0] not in preferred_indexes
                        and self._is_anchor(self.passages[item[0]], {theme})
                    ),
                    None,
                )
                if match is not None:
                    preferred.append(match)
                    preferred_indexes.add(match[0])
            scored = preferred + [item for item in scored if item[0] not in preferred_indexes]

        selected: list[SearchResult] = []
        seen_books: Counter[str] = Counter()
        per_book_limit = 1 if themes else 2
        for index, score, confidence in scored:
            passage = self.passages[index]
            if confidence < 0.36 or seen_books[passage.book] >= per_book_limit:
                continue
            if any(
                passage.book == item.passage.book
                and passage.chapter == item.passage.chapter
                and abs(passage.verse_start - item.passage.verse_start) <= 1
                for item in selected
            ):
                continue
            matched_themes = tuple(
                sorted(theme for theme in themes if self._is_anchor(passage, {theme}))
            )
            selected.append(
                SearchResult(
                    passage,
                    self.context_for(passage, radius=5),
                    score,
                    confidence,
                    matched_themes,
                )
            )
            seen_books[passage.book] += 1
            if len(selected) == limit:
                break
        return selected

    def context_for(self, passage: Passage, radius: int = 2) -> Passage:
        focus_index = next(
            index
            for index, verse in enumerate(self.verses)
            if verse.book == passage.book
            and verse.chapter == passage.chapter
            and verse.verse == passage.verse_start
        )
        chapter_verses: list[Verse] = []
        for index in range(max(0, focus_index - radius), min(len(self.verses), focus_index + radius + 1)):
            verse = self.verses[index]
            if verse.book == passage.book and verse.chapter == passage.chapter:
                chapter_verses.append(verse)
        first, last = chapter_verses[0], chapter_verses[-1]
        text = " ".join(f"[{verse.verse}] {verse.text}" for verse in chapter_verses)
        return Passage(first.book, first.chapter, first.verse, last.verse, text)

    def passage_range(self, book: str, chapter: int, verse_start: int, verse_end: int) -> Passage:
        verses = [
            verse for verse in self.verses
            if verse.book == book and verse.chapter == chapter and verse_start <= verse.verse <= verse_end
        ]
        if not verses:
            raise ValueError(f"Unknown passage range: {book} {chapter}:{verse_start}-{verse_end}")
        text = " ".join(f"[{verse.verse}] {verse.text}" for verse in verses)
        return Passage(book, chapter, verses[0].verse, verses[-1].verse, text)

    @staticmethod
    def source_id(passage: Passage) -> str:
        return f"{passage.book}:{passage.chapter}:{passage.verse_start}-{passage.verse_end}"

    @staticmethod
    def _is_anchor(passage: Passage, themes: set[str]) -> bool:
        return any(
            passage.book == book
            and passage.chapter == chapter
            and verse_start <= passage.verse_start <= verse_end
            for theme in themes
            for book, chapter, verse_start, verse_end in THEME_ANCHORS[theme]
        )
