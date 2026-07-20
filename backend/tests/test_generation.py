from pathlib import Path

from app.config import Settings
from app.generation import GeneratedReflection, ReflectionGenerator


def test_model_json_parser_accepts_markdown_fence():
    parsed = ReflectionGenerator._parse_json_content(
        '```json\n{"summary":"Jasne wyjaśnienie", "selected_source_ids":["Luke:10:27-27"]}\n```'
    )
    assert parsed["summary"] == "Jasne wyjaśnienie"
    assert parsed["selected_source_ids"] == ["Luke:10:27-27"]


def test_model_source_id_accepts_omitted_repeated_end_verse():
    assert ReflectionGenerator._canonical_source_id(
        "Proverbs:18:13", {"Proverbs:18:13-13", "Luke:10:27-27"}
    ) == "Proverbs:18:13-13"


async def test_generation_retries_one_malformed_model_response(monkeypatch):
    generator = ReflectionGenerator(Settings(hf_token="test-token", embedding_model=""))
    expected = GeneratedReflection(
        "Summary", ["Action"], "hugging-face:test", ("Luke:10:27-27",),
        {"Luke:10:27-27": "Explanation"},
    )
    attempts = 0

    async def flaky_remote(*args):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ValueError("malformed JSON")
        return expected

    monkeypatch.setattr(generator, "_generate_remote", flaky_remote)
    assert await generator.generate("A sufficiently long situation", [], "en") == expected
    assert attempts == 2


async def test_generation_falls_back_locally_when_remote_model_keeps_failing(monkeypatch):
    generator = ReflectionGenerator(Settings(hf_token="test-token", embedding_model=""))
    attempts = 0

    async def broken_remote(*args):
        nonlocal attempts
        attempts += 1
        raise ValueError("malformed JSON")

    monkeypatch.setattr(generator, "_generate_remote", broken_remote)
    # Use the real retrieval result so the fallback exercises the complete
    # local response shape, including source explanations.
    from app.retrieval import Retriever

    data = Path(__file__).parents[1] / "app" / "data" / "web_verses.json"
    retriever = Retriever(data)
    results = retriever.search("love your neighbour", limit=2)
    generated = await generator.generate("A sufficiently long situation", results, "en")

    assert attempts == 2
    assert generated.mode == "local-extractive"
    assert generated.source_ids
