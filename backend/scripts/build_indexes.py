#!/usr/bin/env python3
from pathlib import Path

from app.config import get_settings
from app.retrieval import Retriever, SemanticEncoder


def main() -> None:
    settings = get_settings()
    data_dir = Path(__file__).parents[1] / "app" / "data"
    encoder = SemanticEncoder(settings.embedding_model)
    for filename in ("web_verses.json", "polubg_verses.json"):
        source = data_dir / filename
        cache = Retriever.cache_name(source, settings.embedding_model)
        Retriever(source, encoder, cache)
        print(f"Ready: {cache.name}")


if __name__ == "__main__":
    main()
