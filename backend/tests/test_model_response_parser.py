import pytest

from app.model_response import ModelResponseParser


def test_parser_normalizes_current_response_shape() -> None:
    parser = ModelResponseParser({"Luke:10:27-27"})

    response = parser.parse(
        """```json
        {
          "summary": "Choose **mercy**.",
          "suggested_actions": ["Act with `care`."],
          "selected_sources": [{
            "id": "Luke:10:27",
            "situation_application": "Show mercy. This does not mean that danger should be ignored."
          }]
        }
        ```""",
        language="en",
    )

    assert response.summary == "Choose mercy."
    assert response.actions == ["Act with care."]
    assert response.source_ids == ("Luke:10:27-27",)


def test_parser_rejects_incomplete_response() -> None:
    parser = ModelResponseParser({"Luke:10:27-27"})

    with pytest.raises(ValueError, match="Empty model response"):
        parser.parse('{"summary": "", "suggested_actions": []}', language="en")
