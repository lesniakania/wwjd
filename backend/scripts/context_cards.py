#!/usr/bin/env python3
"""Validate reviewed context cards or create a non-publishable editorial queue."""

import argparse
import json
from pathlib import Path


REQUIRED_LOCALIZED = {
    "literary_type", "origin_context", "broader_context", "original_meaning"
}


def validate(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    for index, row in enumerate(rows):
        label = row.get("id", f"row {index}")
        if label in ids:
            errors.append(f"{label}: duplicate id")
        ids.add(label)
        for language in ("pl", "en"):
            missing = REQUIRED_LOCALIZED - set(row.get(language, {}))
            if missing:
                errors.append(f"{label}: {language} missing {', '.join(sorted(missing))}")
        if row.get("reviewed") is True and not row.get("context_sources"):
            errors.append(f"{label}: reviewed card needs context_sources")
    return errors


def draft_queue(references: list[str]) -> list[dict]:
    return [
        {
            "reference": reference,
            "status": "draft",
            "reviewed": False,
            "editorial_note": "AI may draft this card; a human editor must verify and approve it.",
        }
        for reference in references
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cards", type=Path)
    parser.add_argument("--queue", type=Path)
    parser.add_argument("--references", nargs="*", default=[])
    args = parser.parse_args()
    rows = json.loads(args.cards.read_text(encoding="utf-8"))
    errors = validate(rows)
    if errors:
        raise SystemExit("\n".join(errors))
    if args.queue:
        args.queue.write_text(
            json.dumps(draft_queue(args.references), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(f"Validated {len(rows)} reviewed context cards")


if __name__ == "__main__":
    main()
