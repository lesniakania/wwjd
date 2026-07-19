#!/usr/bin/env python3
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


BOOK_NAMES = {
    "GEN": "Genesis", "EXO": "Exodus", "LEV": "Leviticus", "NUM": "Numbers",
    "DEU": "Deuteronomy", "JOS": "Joshua", "JDG": "Judges", "RUT": "Ruth",
    "1SA": "1 Samuel", "2SA": "2 Samuel", "1KI": "1 Kings", "2KI": "2 Kings",
    "1CH": "1 Chronicles", "2CH": "2 Chronicles", "EZR": "Ezra", "NEH": "Nehemiah",
    "EST": "Esther", "JOB": "Job", "PSA": "Psalms", "PRO": "Proverbs",
    "ECC": "Ecclesiastes", "SNG": "Song of Solomon", "ISA": "Isaiah",
    "JER": "Jeremiah", "LAM": "Lamentations", "EZK": "Ezekiel", "DAN": "Daniel",
    "HOS": "Hosea", "JOL": "Joel", "AMO": "Amos", "OBA": "Obadiah", "JON": "Jonah",
    "MIC": "Micah", "NAM": "Nahum", "HAB": "Habakkuk", "ZEP": "Zephaniah",
    "HAG": "Haggai", "ZEC": "Zechariah", "MAL": "Malachi", "MAT": "Matthew",
    "MRK": "Mark", "LUK": "Luke", "JHN": "John", "ACT": "Acts", "ROM": "Romans",
    "1CO": "1 Corinthians", "2CO": "2 Corinthians", "GAL": "Galatians",
    "EPH": "Ephesians", "PHP": "Philippians", "COL": "Colossians",
    "1TH": "1 Thessalonians", "2TH": "2 Thessalonians", "1TI": "1 Timothy",
    "2TI": "2 Timothy", "TIT": "Titus", "PHM": "Philemon", "HEB": "Hebrews",
    "JAS": "James", "1PE": "1 Peter", "2PE": "2 Peter", "1JN": "1 John",
    "2JN": "2 John", "3JN": "3 John", "JUD": "Jude", "REV": "Revelation",
}
SKIP_TAGS = {"f", "fe", "x", "fig", "rem"}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_usfx(source: Path) -> list[dict]:
    root = ET.parse(source).getroot()
    verses: list[dict] = []
    for book in root.findall("book"):
        book_id = book.attrib.get("id", "")
        if book_id not in BOOK_NAMES:
            continue
        state: dict = {"current": None, "parts": [], "chapter": None}

        def visit(element: ET.Element, skipped: bool = False) -> None:
            tag = element.tag.split("}")[-1]
            now_skipped = skipped or tag in SKIP_TAGS
            if tag == "c":
                state["chapter"] = int(element.attrib["id"])
            elif tag == "v":
                state["current"] = int(re.match(r"\d+", element.attrib["id"]).group())
                state["parts"] = []
            elif tag == "ve":
                if state["current"] is not None:
                    text = normalize("".join(state["parts"]))
                    if text:
                        verses.append({
                            "book": BOOK_NAMES[book_id],
                            "chapter": state["chapter"],
                            "verse": state["current"],
                            "text": text,
                        })
                    state["current"] = None
                    state["parts"] = []
            elif state["current"] is not None and element.text and not now_skipped:
                state["parts"].append(element.text)

            for child in element:
                visit(child, now_skipped)
                if state["current"] is not None and child.tail and not now_skipped:
                    state["parts"].append(child.tail)

        visit(book)
    return verses


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert an eBible USFX file to compact verse JSON")
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    verses = parse_usfx(args.source)
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_text(json.dumps(verses, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(verses)} verses to {args.destination}")


if __name__ == "__main__":
    main()

