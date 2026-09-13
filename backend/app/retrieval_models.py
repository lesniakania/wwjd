from dataclasses import dataclass
from enum import StrEnum


class RerankerStrategy(StrEnum):
    RAW = "raw"
    FUSED = "fused"
    THEMATIC_FUSED = "thematic_fused"


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
    context: Passage
    score: float
    confidence: float
    themes: tuple[str, ...]
