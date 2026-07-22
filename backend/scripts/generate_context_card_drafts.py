#!/usr/bin/env python3
"""Generate a broad, review-required set of literary context card drafts.

The script uses public-domain BSB section headings only to choose unit boundaries. It sends
the corresponding local WEB text to the configured chat model. Generated records are always
stored with ``reviewed: false`` and therefore cannot be served by the application.
"""

import argparse
import asyncio
import json
import re
from collections import defaultdict
from pathlib import Path

import httpx

from app.config import Settings


BOOK_ALIASES = {"Song": "Song of Solomon"}
GOSPELS = {"Matthew", "Mark", "Luke", "John"}
NEW_TESTAMENT = {
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians",
    "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians",
    "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus",
    "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John",
    "3 John", "Jude", "Revelation",
}
WISDOM = {"Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon"}
DEUTEROCANON_TARGETS = [
    ("Tobit", 4, 5, 19, "Tobit's instruction to his son"),
    ("Judith", 8, 9, 36, "Judith challenges the leaders of Bethulia"),
    ("Wisdom", 2, 1, 24, "The reasoning of the ungodly and the righteous person"),
    ("Baruch", 3, 9, 15, "Israel is called to listen to wisdom"),
    ("1 Maccabees", 2, 15, 28, "Mattathias refuses apostasy"),
    ("2 Maccabees", 7, 1, 42, "A mother and her seven sons remain faithful"),
]
SYSTEM_PROMPT = """Prepare editorial DRAFTS of Catholic Bible context cards.
Use only the supplied reference, public-domain passage text, and section title as direct evidence.
You may use stable introductory knowledge about biblical books, but state debated authorship or dating
cautiously. Never invent a speaker, audience, scene, causal link, or historical detail. Do not quote or
closely paraphrase commentary. Write natural, idiomatic Polish and English with correct Polish inflection.
Each field must contain concise prose: literary_type is a short label; origin_context is 2-3 sentences;
broader_context is 2-3 sentences; original_meaning is 1-2 sentences. Distinguish a narrative, parable,
speech, law, psalm, prophecy, wisdom saying, letter, and apocalyptic vision. Return strict JSON as an array
of objects with exactly: key, pl, en. Both pl and en contain exactly literary_type, origin_context,
broader_context, original_meaning. These are drafts for human review, not authoritative commentary."""


def plain(value: object) -> str:
    return re.sub(r"\s+", " ", str(value)).strip().replace("**", "").replace("`", "")


def verse_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(verse_text(item) for item in content)
    if isinstance(content, dict):
        return str(content.get("text", ""))
    return ""


def sections_from_bsb(data: dict) -> dict[str, list[dict]]:
    by_book: dict[str, list[dict]] = defaultdict(list)
    for raw_book in data["books"]:
        book = BOOK_ALIASES.get(raw_book["name"], raw_book["name"])
        for wrapper in raw_book["chapters"]:
            chapter = wrapper["chapter"]
            number = chapter["number"]
            headings: list[tuple[int, str]] = []
            pending: list[str] = []
            verses: dict[int, str] = {}
            for item in chapter["content"]:
                if item["type"] == "heading":
                    pending.append(plain(verse_text(item.get("content", ""))))
                elif item["type"] == "verse":
                    verse = int(item["number"])
                    verses[verse] = plain(verse_text(item.get("content", "")))
                    if pending:
                        headings.append((verse, " — ".join(filter(None, pending))))
                        pending = []
            for index, (start, title) in enumerate(headings):
                end = headings[index + 1][0] - 1 if index + 1 < len(headings) else max(verses)
                if not title or end < start or end - start + 1 > 45:
                    continue
                text = " ".join(verses.get(verse, "") for verse in range(start, end + 1))
                by_book[book].append({
                    "book": book, "chapter": number, "start": start, "end": end,
                    "title": title, "text": text,
                })
    return by_book


def overlaps_existing(unit: dict, cards: list[dict]) -> bool:
    point_start = (unit["chapter"], unit["start"])
    point_end = (unit["chapter"], unit["end"])
    return any(
        row["book"] == unit["book"]
        and point_start <= (row["chapter_end"], row["verse_end"])
        and point_end >= (row["chapter_start"], row["verse_start"])
        for row in cards
    )


def book_weight(book: str) -> float:
    if book in GOSPELS:
        return 5.0
    if book in NEW_TESTAMENT:
        return 2.4
    if book in WISDOM:
        return 2.0
    return 1.0


def choose_units(by_book: dict[str, list[dict]], cards: list[dict], count: int) -> list[dict]:
    candidates = {
        book: [unit for unit in units if not overlaps_existing(unit, cards)]
        for book, units in by_book.items()
    }
    candidates = {book: units for book, units in candidates.items() if units}
    quotas = {book: 1 for book in candidates}
    while sum(quotas.values()) < count:
        available = [book for book in candidates if quotas[book] < len(candidates[book])]
        if not available:
            break
        book = max(
            available,
            key=lambda name: book_weight(name) * len(candidates[name]) / (quotas[name] + 1),
        )
        quotas[book] += 1
    selected: list[dict] = []
    for book, quota in quotas.items():
        units = candidates[book]
        indexes = [round(index * (len(units) - 1) / max(quota - 1, 1)) for index in range(quota)]
        selected.extend(units[index] for index in dict.fromkeys(indexes))
    return selected[:count]


def local_passage_text(rows: list[dict], book: str, chapter: int, start: int, end: int) -> str:
    return " ".join(
        row["text"] for row in rows
        if row["book"] == book and row["chapter"] == chapter and start <= row["verse"] <= end
    )


def unit_key(unit: dict) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", unit["title"].lower()).strip("-")[:48]
    return f"{unit['book'].lower().replace(' ', '-')}-{unit['chapter']}-{unit['start']}-{slug}"


async def generate_batch(client: httpx.AsyncClient, settings: Settings, units: list[dict]) -> list[dict]:
    supplied = [
        {
            "key": unit_key(unit),
            "reference": f"{unit['book']} {unit['chapter']}:{unit['start']}-{unit['end']}",
            "section_title": unit["title"],
            "passage_text": unit["text"],
        }
        for unit in units
    ]
    payload = {
        "model": settings.hf_model_pl,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(supplied, ensure_ascii=False)},
        ],
        "temperature": 0.1,
        "max_tokens": 6000,
        "response_format": {"type": "json_object"},
    }
    for attempt in range(3):
        response = await client.post(
            f"{settings.hf_base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {settings.hf_token}"},
            json=payload,
        )
        response.raise_for_status()
        raw = str(response.json()["choices"][0]["message"]["content"]).strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                if {"key", "pl", "en"} <= set(parsed):
                    parsed = [parsed]
                else:
                    parsed = parsed.get("cards", parsed.get("items", []))
            if isinstance(parsed, list) and len(parsed) == len(units):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        if attempt == 2:
            raise ValueError(f"Model did not return a complete JSON batch: {raw[:1000]}")
        payload["messages"] = [
            *payload["messages"],
            {"role": "assistant", "content": raw},
            {
                "role": "user",
                "content": (
                    "Popraw odpowiedź. Zwróć dokładnie jeden kompletny obiekt dla każdego "
                    "wejścia. Zachowaj angielskie nazwy kluczy. Pole pl musi być po polsku, "
                    "a pole en po angielsku. Nie pomijaj żadnego pola ani języka."
                ),
            },
        ]
        payload["model"] = settings.hf_model
    raise AssertionError("unreachable")


def to_card(unit: dict, generated: dict) -> dict:
    def localized(language: str) -> dict:
        value = generated[language]
        aliases = {
            "literary_type": ("literary_type", "literacki_typ", "typ_literacki"),
            "origin_context": ("origin_context", "kontekst_pochodzenia"),
            "broader_context": ("broader_context", "szerszy_kontekst"),
            "original_meaning": ("original_meaning", "oryginalne_znaczenie", "pierwotne_znaczenie"),
        }
        result = {}
        for key, names in aliases.items():
            result[key] = plain(next(value[name] for name in names if name in value))
        return result

    return {
        "id": unit_key(unit), "book": unit["book"],
        "chapter_start": unit["chapter"], "verse_start": unit["start"],
        "chapter_end": unit["chapter"], "verse_end": unit["end"],
        "context_chapter": unit["chapter"], "context_verse_start": unit["start"],
        "context_verse_end": unit["end"], "reviewed": False, "confidence": "draft",
        "context_sources": [
            f"{unit['book']} {unit['chapter']}:{unit['start']}–{unit['end']}",
            "Berean Standard Bible section headings (public domain; boundary aid only)",
        ],
        "pl": localized("pl"), "en": localized("en"),
    }


async def run(args: argparse.Namespace) -> None:
    cards = json.loads(args.cards.read_text(encoding="utf-8"))
    bsb = json.loads(args.bsb.read_text(encoding="utf-8"))
    web = json.loads(args.web.read_text(encoding="utf-8"))
    needed = args.target - len(cards)
    if needed <= 0:
        print(f"Already have {len(cards)} cards")
        return
    manual = []
    for book, chapter, start, end, title in DEUTEROCANON_TARGETS:
        if any(row["book"] == book for row in cards):
            continue
        manual.append({
            "book": book, "chapter": chapter, "start": start, "end": end, "title": title,
            "text": local_passage_text(web, book, chapter, start, end),
        })
    units = manual + choose_units(sections_from_bsb(bsb), cards, needed - len(manual))
    units = units[:needed]
    queue = [
        {
            "key": unit_key(unit),
            "book": unit["book"],
            "chapter": unit["chapter"],
            "verse_start": unit["start"],
            "verse_end": unit["end"],
            "section_title": unit["title"],
            "status": "pending_generation",
            "reviewed": False,
        }
        for unit in units
    ]
    args.queue.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared generation queue with {len(queue)} literary units", flush=True)
    if args.prepare_only:
        return
    settings = Settings()
    if not settings.hf_token:
        raise SystemExit("HF_TOKEN is required")
    async with httpx.AsyncClient(timeout=120) as client:
        for offset in range(0, len(units), args.batch_size):
            batch = units[offset:offset + args.batch_size]
            responses = await asyncio.gather(*(
                generate_batch(client, settings, [unit]) for unit in batch
            ))
            generated = [item for response in responses for item in response]
            by_key = {item["key"]: item for item in generated}
            cards.extend(to_card(unit, by_key[unit_key(unit)]) for unit in batch)
            args.cards.write_text(
                json.dumps(cards, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(f"Saved {len(cards)}/{args.target} cards", flush=True)
    if len(cards) != args.target:
        raise SystemExit(f"Generated {len(cards)} cards, expected {args.target}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cards", type=Path, default=Path("app/data/context_cards.json"))
    parser.add_argument("--bsb", type=Path, required=True)
    parser.add_argument("--web", type=Path, default=Path("app/data/web_verses.json"))
    parser.add_argument("--target", type=int, default=200)
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument(
        "--queue", type=Path, default=Path("app/data/context_card_generation_queue.json")
    )
    parser.add_argument("--prepare-only", action="store_true")
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
