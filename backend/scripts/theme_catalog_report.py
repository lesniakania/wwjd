#!/usr/bin/env python3
"""Regenerate the human-review report for themes and curated passage anchors."""

import json
from pathlib import Path

from app.context import ContextRegistry
from app.localization import THEME_LABELS, THEME_NAMES
from app.retrieval import THEME_ANCHORS, Passage
from app.themes import THEME_PROFILES, Theme


DATA = Path(__file__).parents[1] / "app" / "data"


def reference(book: str, chapter: int, verse_start: int, verse_end: int) -> str:
    verses = str(verse_start) if verse_start == verse_end else f"{verse_start}–{verse_end}"
    return f"{book} {chapter}:{verses}"


def passage_text(rows: list[dict], book: str, chapter: int, start: int, end: int) -> str:
    return " ".join(
        row["text"]
        for row in rows
        if row["book"] == book and row["chapter"] == chapter and start <= row["verse"] <= end
    )


def build_report() -> str:
    english_rows = json.loads((DATA / "web_verses.json").read_text(encoding="utf-8"))
    polish_rows = json.loads((DATA / "polubg_verses.json").read_text(encoding="utf-8"))
    registry = ContextRegistry()
    lines = [
        "# Theme catalog editorial review",
        "",
        "> Editorial draft. Checking a box is a human review decision.",
        "",
    ]
    for theme in Theme:
        lines.extend(
            [
                f"## {theme}",
                "",
                f"- Polish display name: {THEME_LABELS['pl'][str(theme)]}",
                f"- English display name: {THEME_LABELS['en'][str(theme)]}",
                "- Current semantic profiles:",
                *[f"  - {profile}" for profile in THEME_PROFILES[theme]],
                "",
                "### Proposed anchors",
                "",
            ]
        )
        for book, chapter, verse_start, verse_end in THEME_ANCHORS[str(theme)]:
            card = next(
                row
                for row in registry.rows
                if registry._contains(row, Passage(book, chapter, verse_start, verse_start, ""))
            )
            lines.extend(
                [
                    f"#### {reference(book, chapter, verse_start, verse_end)}",
                    "",
                    f"- PL quotation: {passage_text(polish_rows, book, chapter, verse_start, verse_end)}",
                    f"- EN quotation: {passage_text(english_rows, book, chapter, verse_start, verse_end)}",
                    f"- Reviewed context card: `{card['id']}`",
                    f"- Draft rationale PL: {THEME_NAMES['pl'][str(theme)]}. {card['pl']['original_meaning']}",
                    f"- Draft rationale EN: {THEME_NAMES['en'][str(theme)]}. {card['en']['original_meaning']}",
                    "- [ ] Approve anchor",
                    "- [ ] Request anchor changes",
                    "",
                ]
            )
        lines.extend(
            [
                "### Theme decision",
                "",
                "- [ ] Approve theme",
                "- [ ] Request changes",
                "- Reviewer notes:",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    (DATA / "theme_catalog_review.md").write_text(build_report() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
