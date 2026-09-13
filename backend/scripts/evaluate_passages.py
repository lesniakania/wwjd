#!/usr/bin/env python3
"""Compare verse and context embeddings using frozen analyzed queries, without generation."""

import argparse
import hashlib
import json
from enum import StrEnum
from pathlib import Path

import numpy as np

from app.config import get_settings
from app.evaluation import score_sources, summarize
from app.passage_index import contextual_passages, embedding_fingerprint, rank_embeddings
from app.retrieval import Retriever, SemanticEncoder
from app.retrieval_models import Verse


class Representation(StrEnum):
    VERSE = "verse_embeddings"
    EXPANSION = "verse_embeddings_expanded"
    CONTEXT = "context_embeddings"
    FUSION = "existing_plus_context"


def unique_references(references: list[str], limit: int = 50) -> list[str]:
    return list(dict.fromkeys(references))[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Output already exists")
    report = json.loads(args.report.read_text())
    data = Path(__file__).parents[1] / "app/data/polubg_verses.json"
    verses = [Verse(**row) for row in json.loads(data.read_text())]
    passages = contextual_passages(verses)
    texts = [passage.text for passage in passages]
    settings = get_settings()
    recorded_model = report.get("configuration", {}).get("embedding_model")
    if recorded_model != settings.embedding_model:
        raise ValueError("Embedding model must match the input report")
    encoder = SemanticEncoder(settings.embedding_model)
    fingerprint = embedding_fingerprint(settings.embedding_model, texts)
    cache = data.with_name(f"context_{fingerprint[:16]}.npy")
    if cache.exists():
        context_vectors = np.load(cache)
    else:
        batches = []
        for start in range(0, len(texts), 256):
            batches.append(encoder.encode(texts[start:start + 256]))
            print(f"Context embeddings: {min(start + 256, len(texts))}/{len(texts)}", flush=True)
        context_vectors = np.concatenate(batches)
        np.save(cache, context_vectors)
    verse_vectors = np.load(Retriever.cache_name(data, settings.embedding_model))
    if context_vectors.shape != verse_vectors.shape:
        raise ValueError("Verse and context embedding shapes differ")
    rows: dict[str, list[dict]] = {variant: [] for variant in Representation}
    for row in report["results"]:
        search = row["response"]["diagnostics"]["searches"][0]
        query = encoder.encode(search["query"])
        verse_order = rank_embeddings(verse_vectors, query, 150)
        context_order = rank_embeddings(context_vectors, query, 150)
        verse_refs = [f"{verses[index].book} {verses[index].chapter}:{verses[index].verse}"
                      for index in verse_order]
        expanded_refs = unique_references([passages[index].reference for index in verse_order])
        context_refs = unique_references([passages[index].reference for index in context_order])
        existing_refs = [candidate["reference"] for candidate in search["before_rerank"]]
        fusion: dict[str, float] = {}
        for references in (existing_refs, context_refs):
            for rank, reference in enumerate(references, 1):
                fusion[reference] = fusion.get(reference, 0.) + 1 / (60 + rank)
        variants = {Representation.VERSE: verse_refs[:50],
                    Representation.EXPANSION: expanded_refs,
                    Representation.CONTEXT: context_refs,
                    Representation.FUSION: sorted(fusion, key=lambda ref: -fusion[ref])[:50]}
        for name, actual in variants.items():
            rows[name].append({"id": row["id"], "category": row["category"],
                               "candidates": actual,
                               "scores": score_sources(actual, row["expected"])})
    result = {
        "kind": "candidate-representation-experiment", "input_report": str(args.report),
        "input_sha256": hashlib.sha256(args.report.read_bytes()).hexdigest(),
        "dataset_sha256": report["dataset_sha256"], "model": settings.embedding_model,
        "context_fingerprint": fingerprint, "candidate_limit": 50,
        "corpus_sha256": hashlib.sha256(data.read_bytes()).hexdigest(),
        "existing_candidates": report["stages"]["initial_before_rerank"],
        "variants": {name: {"summary": summarize(results), "results": results}
                     for name, results in rows.items()},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as output:
        output.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({name: value["summary"] for name, value in result["variants"].items()},
                     indent=2), flush=True)


if __name__ == "__main__":
    main()
