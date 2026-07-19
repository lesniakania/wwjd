import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


TOKEN_RE = re.compile(r"[a-zA-Z']+")
GOSPELS = {"Matthew", "Mark", "Luke", "John"}
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for", "from",
    "had", "has", "have", "he", "her", "him", "his", "i", "if", "in", "is", "it", "me",
    "my", "of", "on", "or", "our", "she", "so", "that", "the", "their", "them", "they",
    "this", "to", "was", "we", "were", "what", "when", "with", "would", "you", "your",
}
THEME_EXPANSIONS = {
    "anger": (
        {"angry", "anger", "furious", "revenge", "retaliate", "embarrass", "humiliate"},
        "anger wrath gentle peace patience reconcile enemy forgive",
    ),
    "honesty": (
        {"lie", "lied", "lying", "dishonest", "honest", "truth", "deceive", "credit"},
        "truth truthful honest deceit false witness integrity",
    ),
    "forgiveness": (
        {"forgive", "forgiveness", "hurt", "offended", "betrayed", "grudge"},
        "forgive mercy reconciliation brother trespass",
    ),
    "conflict": (
        {"conflict", "argument", "confront", "colleague", "coworker", "friend"},
        "brother privately reconcile peace gentle listen",
    ),
    "fear": (
        {"afraid", "anxious", "anxiety", "fear", "worried", "worry"},
        "fear anxious worry trust courage peace",
    ),
    "generosity": (
        {"money", "poor", "give", "generous", "greed", "possessions"},
        "give poor generous treasure neighbor need",
    ),
}
THEME_ANCHORS = {
    "anger": (("Matthew", 5, 21, 26), ("Luke", 6, 27, 36), ("James", 1, 19, 20)),
    "honesty": (("Matthew", 5, 33, 37), ("Ephesians", 4, 25, 25), ("Proverbs", 12, 17, 22)),
    "forgiveness": (("Matthew", 18, 21, 35), ("Luke", 17, 3, 4), ("Colossians", 3, 12, 13)),
    "conflict": (("Matthew", 18, 15, 17), ("Romans", 12, 17, 21), ("James", 3, 13, 18)),
    "fear": (("Matthew", 6, 25, 34), ("John", 14, 25, 27), ("Philippians", 4, 6, 7)),
    "generosity": (("Matthew", 6, 19, 24), ("Luke", 10, 30, 37), ("1 John", 3, 16, 18)),
}


def tokenize(text: str) -> list[str]:
    return [token for token in TOKEN_RE.findall(text.lower()) if token not in STOPWORDS]


def expand_query(text: str) -> str:
    original = set(tokenize(text))
    expansions = [words for triggers, words in THEME_EXPANSIONS.values() if original & triggers]
    return f"{text} {' '.join(expansions)}"


def query_themes(text: str) -> set[str]:
    original = set(tokenize(text))
    return {theme for theme, (triggers, _) in THEME_EXPANSIONS.items() if original & triggers}


@dataclass(frozen=True)
class Verse:
    book: str
    chapter: int
    verse: int
    text: str


@dataclass(frozen=True)
class Passage:
    book: str
    chapter: int
    verse_start: int
    verse_end: int
    text: str

    @property
    def reference(self) -> str:
        verses = str(self.verse_start)
        if self.verse_end != self.verse_start:
            verses += f"–{self.verse_end}"
        return f"{self.book} {self.chapter}:{verses}"


@dataclass(frozen=True)
class SearchResult:
    passage: Passage
    score: float


class HashingEmbedder:
    """Small deterministic semantic-ish vectorizer for a zero-download default."""

    def __init__(self, dimensions: int = 256):
        self.dimensions = dimensions

    def encode(self, text: str) -> dict[int, float]:
        values: Counter[int] = Counter()
        tokens = tokenize(text)
        features = tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
        for feature in features:
            digest = hashlib.blake2b(feature.encode(), digest_size=4).digest()
            index = int.from_bytes(digest, "little") % self.dimensions
            values[index] += 1
        norm = math.sqrt(sum(value * value for value in values.values())) or 1
        return {index: value / norm for index, value in values.items()}


def cosine(left: dict[int, float], right: dict[int, float]) -> float:
    if len(left) > len(right):
        left, right = right, left
    return sum(value * right.get(index, 0.0) for index, value in left.items())


class Retriever:
    def __init__(self, verses_path: Path):
        rows = json.loads(verses_path.read_text(encoding="utf-8"))
        self.verses = [Verse(**row) for row in rows]
        self.passages = self._make_passages(self.verses)
        self.embedder = HashingEmbedder()
        self._tokens = [Counter(tokenize(passage.text)) for passage in self.passages]
        self._vectors = [self.embedder.encode(passage.text) for passage in self.passages]
        self._document_frequency: Counter[str] = Counter()
        for token_counts in self._tokens:
            self._document_frequency.update(token_counts.keys())

    @staticmethod
    def _make_passages(verses: list[Verse], chunk_size: int = 3) -> list[Passage]:
        passages: list[Passage] = []
        current: list[Verse] = []
        for verse in verses:
            if current and (
                verse.book != current[-1].book
                or verse.chapter != current[-1].chapter
                or verse.verse != current[-1].verse + 1
                or len(current) == chunk_size
            ):
                passages.append(Retriever._passage_from(current))
                current = []
            current.append(verse)
        if current:
            passages.append(Retriever._passage_from(current))
        return passages

    @staticmethod
    def _passage_from(verses: list[Verse]) -> Passage:
        first, last = verses[0], verses[-1]
        return Passage(first.book, first.chapter, first.verse, last.verse, " ".join(v.text for v in verses))

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        enriched_query = expand_query(query)
        themes = query_themes(query)
        query_tokens = Counter(tokenize(enriched_query))
        query_vector = self.embedder.encode(enriched_query)
        corpus_size = len(self.passages)
        scored: list[SearchResult] = []

        for passage, token_counts, vector in zip(self.passages, self._tokens, self._vectors):
            lexical = 0.0
            for token, query_count in query_tokens.items():
                frequency = token_counts.get(token, 0)
                if frequency:
                    inverse_frequency = math.log(1 + corpus_size / (1 + self._document_frequency[token]))
                    lexical += min(frequency, query_count) * inverse_frequency
            semantic = cosine(query_vector, vector)
            gospel_boost = 0.12 if passage.book in GOSPELS else 0.0
            anchor_boost = 0.0
            for theme in themes:
                for book, chapter, verse_start, verse_end in THEME_ANCHORS[theme]:
                    overlaps = passage.verse_end >= verse_start and passage.verse_start <= verse_end
                    if passage.book == book and passage.chapter == chapter and overlaps:
                        anchor_boost = max(anchor_boost, 18.0)
            score = lexical + semantic * 1.7 + gospel_boost + anchor_boost
            if score > 0:
                scored.append(SearchResult(passage, score))

        scored.sort(key=lambda result: result.score, reverse=True)
        selected: list[SearchResult] = []
        seen_books: Counter[str] = Counter()
        for result in scored:
            if seen_books[result.passage.book] >= 2:
                continue
            selected.append(result)
            seen_books[result.passage.book] += 1
            if len(selected) == limit:
                break
        return selected
