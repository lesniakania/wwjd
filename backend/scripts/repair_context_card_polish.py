#!/usr/bin/env python3
"""Repair draft cards whose Polish fields were accidentally generated in English."""

import argparse
import asyncio
import json
import re
from pathlib import Path

import httpx

from app.config import Settings


FIELDS = ("literary_type", "origin_context", "broader_context", "original_meaning")
ENGLISH_WORDS = {
    "the", "and", "is", "are", "this", "that", "with", "from", "into", "through",
    "his", "her", "their", "describes", "passage", "context", "book", "written",
    "part", "story", "god", "narrative", "prophecy", "letter",
}
POLISH_WORDS = {
    "i", "oraz", "jest", "są", "to", "że", "który", "która", "przez", "w", "z",
    "do", "na", "się", "jego", "jej", "ich", "księgi", "fragment", "opowiada",
    "bóg", "jezus", "list", "psalm", "proroctwo", "wspólnota", "autor",
}
SYSTEM = """Jesteś bardzo dobrym polskim redaktorem tekstów biblijnych. Przepisz dostarczone
cztery pola na naturalną, poprawną gramatycznie polszczyznę. Zachowaj sens i ostrożność źródła;
nie dodawaj nowych faktów, interpretacji ani cytatów. Usuń kalki z angielskiego. Nazwy gatunków
również podaj po polsku. Zwróć wyłącznie obiekt JSON z dokładnie czterema angielskimi kluczami:
literary_type, origin_context, broader_context, original_meaning. Wartości muszą być po polsku."""


def scores(text: str) -> tuple[int, int]:
    words = re.findall(r"[a-ząćęłńóśźż]+", text.lower())
    return sum(word in ENGLISH_WORDS for word in words), sum(word in POLISH_WORDS for word in words)


def needs_repair(card: dict) -> bool:
    if card.get("reviewed") is True:
        return False
    english, polish = scores(" ".join(card["pl"].values()))
    return english >= 4 and english > polish


def valid_polish(value: object) -> bool:
    if not isinstance(value, dict) or not set(FIELDS) <= set(value):
        return False
    english, polish = scores(" ".join(str(value[field]) for field in FIELDS))
    return polish >= english


async def repair(client: httpx.AsyncClient, settings: Settings, card: dict) -> tuple[str, dict]:
    source = card["pl"] if card.get("pl") else card["en"]
    payload = {
        "model": settings.hf_model_pl,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": json.dumps(source, ensure_ascii=False)},
        ],
        "temperature": 0.05,
        "max_tokens": 1400,
        "response_format": {"type": "json_object"},
    }
    last = ""
    for attempt in range(3):
        response = await client.post(
            f"{settings.hf_base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {settings.hf_token}"}, json=payload,
        )
        response.raise_for_status()
        last = str(response.json()["choices"][0]["message"]["content"]).strip()
        last = last.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            value = json.loads(last)
            if valid_polish(value):
                return card["id"], {field: re.sub(r"\s+", " ", str(value[field])).strip() for field in FIELDS}
        except (json.JSONDecodeError, TypeError):
            pass
        payload["messages"].append({"role": "assistant", "content": last})
        payload["messages"].append({
            "role": "user",
            "content": "Odpowiedź nadal nie jest w całości po polsku. Popraw ją i zachowaj wszystkie cztery klucze.",
        })
        if attempt == 1:
            payload["model"] = settings.hf_model
    raise ValueError(f"Could not repair {card['id']}: {last[:300]}")


async def run(args: argparse.Namespace) -> None:
    settings = Settings()
    cards = json.loads(args.cards.read_text(encoding="utf-8"))
    pending = [card for card in cards if needs_repair(card)]
    print(f"Found {len(pending)} draft cards requiring Polish repair", flush=True)
    by_id = {card["id"]: card for card in cards}
    async with httpx.AsyncClient(timeout=120) as client:
        for offset in range(0, len(pending), args.concurrency):
            batch = pending[offset:offset + args.concurrency]
            repaired = await asyncio.gather(*(repair(client, settings, card) for card in batch))
            for card_id, value in repaired:
                by_id[card_id]["pl"] = value
                issues = by_id[card_id].get("draft_issues", [])
                by_id[card_id]["draft_issues"] = [
                    issue for issue in issues if issue != "polish_translation_required"
                ]
                if not by_id[card_id]["draft_issues"]:
                    by_id[card_id].pop("draft_issues", None)
            args.cards.write_text(json.dumps(cards, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Repaired {min(offset + len(batch), len(pending))}/{len(pending)}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cards", type=Path, default=Path("app/data/context_cards.json"))
    parser.add_argument("--concurrency", type=int, default=5)
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
