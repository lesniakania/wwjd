from pathlib import Path

from app.retrieval import Retriever, query_themes


DATA = Path(__file__).parents[1] / "app" / "data" / "web_verses.json"


def test_retrieval_finds_relevant_passages():
    retriever = Retriever(DATA)
    results = retriever.search("How can I forgive someone who hurt me?", limit=5)
    assert 1 <= len(results) <= 5
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


def test_polish_inflections_detect_prejudice_and_unverified_claims():
    themes = query_themes(
        "Mam dość Ukraińców. Widziałem nagranie w mediach społecznościowych i dużo się o tym mówi."
    )
    assert {"prejudice", "discernment"} <= themes


def test_group_blame_query_returns_ethical_teaching_not_matching_place_names():
    polish_data = DATA.with_name("polubg_verses.json")
    retriever = Retriever(polish_data)
    results = retriever.search(
        "Mam dość Ukraińców w Polsce. Jedno nagranie krąży w mediach społecznościowych, "
        "ale nic się nie mówi o atakach Ukraińców na Polaków.",
        limit=4,
    )

    references = {result.passage.reference for result in results}
    assert len(results) == 4
    assert not references & {"Isaiah 33:19", "1 Chronicles 11:44", "2 Corinthians 9:4"}
    assert all(result.themes for result in results)
    assert any(
        reference.startswith(("Luke 10:", "Leviticus 19:", "James 2:"))
        for reference in references
    )
    assert any(
        reference.startswith(("Exodus 23:", "Proverbs 18:", "1 Thessalonians 5:"))
        for reference in references
    )
