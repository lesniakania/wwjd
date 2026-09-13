#!/usr/bin/env python3
"""Prepare a reproducible 20-case calibration sample from the original saved runs."""

import hashlib
import json
import random
from pathlib import Path

from app.blind_review import build_case


ROOT = Path(__file__).parents[1]


def main() -> None:
    destination = ROOT / "evaluation/calibration-v1"
    if destination.exists():
        raise ValueError("Review directory already exists")
    cases = json.loads((ROOT / "evaluation/cases.pl.json").read_text())
    reports = {name: json.loads((ROOT / f"evaluation/runs/{name}.json").read_text())
               for name in ("baseline", "reranker")}
    digest = hashlib.sha256((ROOT / "evaluation/cases.pl.json").read_bytes()).hexdigest()
    if any(report["dataset_sha256"] != digest for report in reports.values()):
        raise ValueError("Report dataset differs from the approved dataset")
    corpus = {(verse["book"], verse["chapter"], verse["verse"]): verse["text"] for verse in
              json.loads((ROOT / "app/data/polubg_verses.json").read_text())}
    generator = random.Random(20260912)
    selected = generator.sample([case for case in cases if case["category"] == "uprzedzenia"], 10)
    for category in sorted({case["category"] for case in cases} - {"uprzedzenia"}):
        selected.append(generator.choice([case for case in cases if case["category"] == category]))
    generator.shuffle(selected)
    lookup = {name: {row["id"]: row for row in report["results"]}
              for name, report in reports.items()}
    packets = []
    keys = {}
    for case in selected:
        outputs = {}
        for name, rows in lookup.items():
            row = rows[case["id"]]
            if row["situation"] != case["situation"]:
                raise ValueError("Situation differs between report and dataset")
            outputs[name] = row["response"]["sources"]
        packet, key = build_case(case, outputs, corpus)
        packets.append(packet)
        keys[case["id"]] = key
    destination.mkdir()
    (destination / "human-review.json").write_text(json.dumps(
        {"dataset_sha256": digest, "cases": packets}, ensure_ascii=False, indent=2) + "\n")
    (destination / "provenance.json").write_text(json.dumps(keys, ensure_ascii=False, indent=2) + "\n")
    lines = ["# Kalibracja oceny — 20 sytuacji", "",
             "Najpierw oceniaj bez otwierania provenance.json ani ocen AI.", "",
             "Wpisuj oceny w human-review.json (pola rating i notes). Ten dokument służy do czytania.",
             "", "Cytaty: direct = bezpośrednio trafny; supporting = sensowny pomocniczo; "
             "irrelevant = nietrafny; uncertain = wymaga dalszego sprawdzenia.",
             "Zastosowania: appropriate = poprawne; problematic = błędne lub krzywdzące; "
             "uncertain = wymaga sprawdzenia. Oceniaj zastosowanie osobno od cytatu.",
             "Kontekst zawiera trzy wersety przed i po cytacie; może nie wystarczyć do interpretacji.", ""]
    for packet in packets:
        lines += [f"## {packet['id']}", "", packet["situation"], ""]
        for passage in packet["passages"]:
            lines += [f"### {passage['id']} — {passage['reference']}", "", passage["quotation"], "",
                      "<details><summary>Tekst otaczający cytat</summary>", "",
                      passage["surrounding_text"], "", "</details>", ""]
        lines += ["### Zastosowania w odpowiedziach", ""]
        for application in packet["applications"]:
            lines += [f"**{application['id']} → {application['passage_id']}**", "",
                      application["text"], ""]
    (destination / "review.pl.md").write_text("\n".join(lines) + "\n")
    print(f"Prepared {len(packets)} cases at {destination}")


if __name__ == "__main__":
    main()
