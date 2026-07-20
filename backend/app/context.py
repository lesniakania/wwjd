import json
from dataclasses import dataclass
from pathlib import Path

from .localization import Language
from .retrieval import Passage


DATA_PATH = Path(__file__).parent / "data" / "context_cards.json"


BOOK_TYPES = {
    "Psalms": ("psalm", "psalm"),
    "Proverbs": ("maksyma mądrościowa", "wisdom saying"),
    "Ecclesiastes": ("literatura mądrościowa", "wisdom literature"),
    "Song of Solomon": ("poezja", "poetry"),
    "Isaiah": ("proroctwo", "prophecy"),
    "Jeremiah": ("proroctwo", "prophecy"),
    "Ezekiel": ("proroctwo", "prophecy"),
    "Daniel": ("opowiadanie i wizja apokaliptyczna", "narrative and apocalyptic vision"),
    "Revelation": ("wizja apokaliptyczna", "apocalyptic vision"),
}
GOSPELS = {"Matthew", "Mark", "Luke", "John"}
LETTERS = {
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude",
}


@dataclass(frozen=True)
class ContextCard:
    id: str
    book: str
    chapter_start: int
    verse_start: int
    chapter_end: int
    verse_end: int
    context_chapter: int
    context_verse_start: int
    context_verse_end: int
    literary_type: str
    origin_context: str
    broader_context: str
    original_meaning: str
    context_sources: tuple[str, ...]
    confidence: str
    reviewed: bool
    fallback: bool = False


class ContextRegistry:
    def __init__(self, path: Path = DATA_PATH):
        rows = json.loads(path.read_text(encoding="utf-8"))
        self.rows = rows

    def for_passage(self, passage: Passage, language: Language) -> ContextCard:
        matches = [row for row in self.rows if self._contains(row, passage)]
        # Prefer the narrowest reviewed unit if ranges overlap.
        matches.sort(key=lambda row: (row["chapter_end"] - row["chapter_start"], row["verse_end"] - row["verse_start"]))
        row = next((item for item in matches if item.get("reviewed") is True), None)
        if row is None:
            return self._fallback(passage, language)
        localized = row[language]
        return ContextCard(
            id=row["id"], book=row["book"], chapter_start=row["chapter_start"],
            verse_start=row["verse_start"], chapter_end=row["chapter_end"],
            verse_end=row["verse_end"], context_chapter=row.get("context_chapter", row["chapter_start"]),
            context_verse_start=row["context_verse_start"],
            context_verse_end=row["context_verse_end"],
            literary_type=localized["literary_type"], origin_context=localized["origin_context"],
            broader_context=localized["broader_context"], original_meaning=localized["original_meaning"],
            context_sources=tuple(row.get("context_sources", [])),
            confidence=row.get("confidence", "high"), reviewed=True,
        )

    @staticmethod
    def _contains(row: dict, passage: Passage) -> bool:
        if row["book"] != passage.book:
            return False
        start = (row["chapter_start"], row["verse_start"])
        end = (row["chapter_end"], row["verse_end"])
        point = (passage.chapter, passage.verse_start)
        return start <= point <= end

    @staticmethod
    def _fallback(passage: Passage, language: Language) -> ContextCard:
        if passage.book in GOSPELS:
            kinds = ("fragment Ewangelii", "Gospel passage")
        elif passage.book in LETTERS:
            kinds = ("fragment listu", "letter passage")
        else:
            kinds = BOOK_TYPES.get(passage.book, ("fragment księgi biblijnej", "biblical passage"))
        kind = kinds[0 if language == "pl" else 1]
        if language == "pl":
            origin = f"To {kind} z {passage.chapter}. rozdziału tej księgi. Nie mamy jeszcze zatwierdzonej karty, która pozwalałaby pewnie wskazać mówcę, odbiorców lub konkretną scenę."
            broader = "Aby nie dopowiadać szczegółów, pokazujemy jedynie najbliższy fragment rozdziału. Szerszy kontekst warto sprawdzić w całej księdze i zatwierdzonym komentarzu katolickim."
            meaning = "Znaczenie należy odczytywać z tekstu rozdziału i gatunku księgi; aplikacja nie przedstawia w tym miejscu szczegółowej interpretacji jako pewnego faktu."
        else:
            origin = f"This is a {kind} from chapter {passage.chapter}. No reviewed card is available yet, so the speaker, audience, and precise scene are not asserted."
            broader = "To avoid inventing details, only the nearby chapter text is shown. Consult the whole book and an approved Catholic commentary for wider context."
            meaning = "Its meaning should be read from the chapter and the book's genre; the app does not present a detailed interpretation here as established fact."
        return ContextCard(
            id=f"fallback:{passage.book}:{passage.chapter}", book=passage.book,
            chapter_start=passage.chapter, verse_start=passage.verse_start,
            chapter_end=passage.chapter, verse_end=passage.verse_end,
            context_chapter=passage.chapter,
            context_verse_start=max(1, passage.verse_start - 2), context_verse_end=passage.verse_end + 2,
            literary_type=kind, origin_context=origin, broader_context=broader,
            original_meaning=meaning, context_sources=(), confidence="limited",
            reviewed=False, fallback=True,
        )
