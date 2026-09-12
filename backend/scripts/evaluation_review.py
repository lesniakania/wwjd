#!/usr/bin/env python3
"""Render the evaluation dataset with verbatim local Polish scripture for review."""

import argparse
from pathlib import Path

from app.evaluation import load_cases, render_review


def main() -> None:
    directory = Path(__file__).parents[1] / "evaluation"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=directory / "cases.pl.json")
    parser.add_argument("--output", type=Path, default=directory / "review.pl.md")
    args = parser.parse_args()
    args.output.write_text(render_review(load_cases(args.dataset)), encoding="utf-8")


if __name__ == "__main__":
    main()
