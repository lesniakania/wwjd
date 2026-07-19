from pathlib import Path

from app.retrieval import Retriever


DATA = Path(__file__).parents[1] / "app" / "data" / "web_verses.json"


def test_retrieval_finds_relevant_passages():
    retriever = Retriever(DATA)
    results = retriever.search("How can I forgive someone who hurt me?", limit=5)
    assert len(results) == 5
    combined = " ".join(result.passage.text.lower() for result in results)
    assert "forgiv" in combined


def test_references_are_well_formed():
    retriever = Retriever(DATA)
    result = retriever.search("love your enemy", limit=1)[0]
    assert ":" in result.passage.reference
    assert result.passage.text


def test_everyday_conflict_expands_to_ethical_themes():
    retriever = Retriever(DATA)
    results = retriever.search(
        "A colleague took credit for my work and I want to embarrass them publicly.", limit=5
    )
    combined = " ".join(result.passage.text.lower() for result in results)
    assert any(word in combined for word in ("anger", "gentle", "peace", "reconcile", "forgive"))
