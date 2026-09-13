#!/usr/bin/env python3
"""Normalize saved prompt outputs with the production parser and anonymize their review."""

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from app.model_response import ModelResponseParser


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Output exists")
    report = json.loads((args.run / "report.json").read_text())
    items = json.loads((Path(__file__).parents[1] /
                       "evaluation/calibration-v1/adjudication.json").read_text())["items"]
    groups: dict[tuple[str, str], list[dict]] = {}
    stats: dict[str, Counter] = {}
    for record in report["records"]:
        counter = stats.setdefault(record["variant"], Counter())
        counter["requests"] += 1
        counter["strict_format_errors"] += "error_type" in record
        try:
            parsed = ModelResponseParser({record["id"]}).parse(record["raw_content"], "pl")
            if parsed.source_ids != (record["id"],):
                raise ValueError("Unexpected source selection")
            text = parsed.applications[record["id"]]
        except (KeyError, ValueError, TypeError):
            counter["production_parser_failures"] += 1
            continue
        counter["usable"] += 1
        groups.setdefault((record["id"], text), []).append({
            "variant": record["variant"], "repeat": record["repeat"],
        })
    generator = random.Random(20260914)
    human = []
    provenance = {}
    lines = ["# Porównanie zastosowań — dwa prompty", "",
             "Źródła i kontekst są identyczne pomiędzy wariantami. Nie otwieraj provenance.json przed oceną.",
             "Powtórzenia z identycznym tekstem zostały połączone. Listy zdań normalizuje parser produkcyjny.",
             "Oceny wpisuj w human-review.json: text_faithfulness = faithful / unsupported / uncertain; "
             "situation_fit = direct / supporting / off_target / uncertain; "
             "harm_risk = no_identified_risk / concerning / uncertain.",
             "Oceniaj wszystkie istotne twierdzenia, również zastrzeżenia. Uczciwe przyznanie słabego "
             "dopasowania może być faithful, choć nie daje direct situation_fit.", ""]
    for item in items:
        entries = [(text, origins) for (identifier, text), origins in groups.items()
                   if identifier == item["id"]]
        generator.shuffle(entries)
        candidates = []
        lines += [f"## {item['id']}", "", item["situation"], "",
                  f"**{item['reference']}** — {item['quotation']}", ""]
        for index, (text, origins) in enumerate(entries, 1):
            identifier = f"{item['id']}-v{index}"
            candidates.append({"id": identifier, "text": text, "text_faithfulness": None,
                               "situation_fit": None, "harm_risk": None, "notes": ""})
            provenance[identifier] = origins
            lines += [f"**{identifier}**", "", text, ""]
        human.append({"id": item["id"], "situation": item["situation"],
                      "reference": item["reference"], "quotation": item["quotation"],
                      "surrounding_text": item["surrounding_text"], "applications": candidates})
    args.output.mkdir(parents=True)
    for name, body in (("human-review", human), ("provenance", provenance), ("execution", stats)):
        (args.output / f"{name}.json").write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n")
    (args.output / "review.pl.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
