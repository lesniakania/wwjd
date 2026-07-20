from app.generation import ReflectionGenerator


def test_chat_parser_accepts_plain_text_provider_response():
    parsed = ReflectionGenerator._parse_chat_content(
        "To jest zwykła odpowiedź tekstowa, a nie JSON."
    )
    assert parsed["answer"] == "To jest zwykła odpowiedź tekstowa, a nie JSON."
    assert parsed["source_ids"] == []


def test_chat_parser_accepts_fenced_json_and_source_ids():
    parsed = ReflectionGenerator._parse_chat_content(
        '```json\n{"answer":"Wyjaśnienie", "source_ids":["Luke:10:27-27"]}\n```'
    )
    assert parsed == {
        "answer": "Wyjaśnienie",
        "source_ids": ["Luke:10:27-27"],
    }
