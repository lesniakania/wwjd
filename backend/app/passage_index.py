"""Context representations for offline candidate retrieval experiments."""

import hashlib
import json
from collections import defaultdict

import numpy as np

from .retrieval_models import Passage, Verse


def contextual_passages(verses: list[Verse]) -> list[Passage]:
    chapters: dict[tuple[str, int], list[Verse]] = defaultdict(list)
    for verse in verses:
        chapters[verse.book, verse.chapter].append(verse)
    positions = {(verse.book, verse.chapter, verse.verse): index
                 for chapter in chapters.values() for index, verse in enumerate(chapter)}
    passages = []
    for verse in verses:
        chapter = chapters[verse.book, verse.chapter]
        position = positions[verse.book, verse.chapter, verse.verse]
        neighbors = chapter[max(0, position - 1):position + 2]
        passages.append(Passage(verse.book, verse.chapter, neighbors[0].verse,
                                neighbors[-1].verse, " ".join(item.text for item in neighbors)))
    return passages


def rank_embeddings(embeddings: np.ndarray, query: np.ndarray, limit: int) -> list[int]:
    return np.argsort(-(embeddings @ query), kind="stable")[:limit].tolist()


def embedding_fingerprint(model: str, texts: list[str]) -> str:
    return hashlib.sha256(json.dumps([model, texts], ensure_ascii=False).encode()).hexdigest()
