import json
from unittest.mock import MagicMock

import pytest

from app.models import ReflectionResponse, SharedReflectionRequest, Source
from app.share_repository import ShareRepository


def _shared_reflection() -> SharedReflectionRequest:
    source = Source(
        reference="Matthew 5:44",
        quotation="Love your enemies.",
        literary_type="Teaching",
        origin_context="Jesus teaches his listeners.",
        broader_context="The Sermon on the Mount.",
        original_meaning="Respond to hostility with active goodwill.",
        situation_application="Choose goodwill without ignoring harm.",
        context_confidence="high",
        context_reviewed=True,
        relevance="The passage addresses retaliation.",
        context_reference="Matthew 5:43–45",
        context_quotation="Love your enemies.",
    )
    reflection = ReflectionResponse(
        summary="Choose active goodwill.",
        suggested_actions=["Pause before responding."],
        sources=[source],
        limitations="This is a reflection.",
        generated_with="local-extractive",
    )
    return SharedReflectionRequest(
        situation="A friend hurt me and I want to respond without retaliation.",
        language="en",
        reflection=reflection,
    )


@pytest.fixture
def connection(monkeypatch) -> MagicMock:
    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.__exit__.return_value = False
    monkeypatch.setattr("app.share_repository.psycopg.connect", MagicMock(return_value=connection))
    return connection


def test_share_repository_saves_snapshot_as_jsonb(connection: MagicMock):
    repository = ShareRepository("postgresql://wwjd:secret@db:5432/wwjd")
    payload = _shared_reflection()

    share_id = repository.save(payload)

    assert share_id
    connection.execute.assert_any_call(
        "INSERT INTO shared_reflections (id, payload) VALUES (%s, %s::jsonb)",
        (share_id, json.dumps(payload.model_dump(mode="json"))),
    )


def test_share_repository_retrieves_exact_snapshot(connection: MagicMock):
    payload = _shared_reflection()
    connection.execute.return_value.fetchone.return_value = (payload.model_dump(mode="json"),)
    repository = ShareRepository("postgresql://wwjd:secret@db:5432/wwjd")

    assert repository.get("share-id") == payload


def test_share_repository_returns_none_for_unknown_id(connection: MagicMock):
    connection.execute.return_value.fetchone.return_value = None
    repository = ShareRepository("postgresql://wwjd:secret@db:5432/wwjd")

    assert repository.get("unknown") is None


def test_share_repository_initializes_schema(connection: MagicMock):
    ShareRepository("postgresql://wwjd:secret@db:5432/wwjd")

    connection.execute.assert_called_once_with(
        """CREATE TABLE IF NOT EXISTS shared_reflections (
            id TEXT PRIMARY KEY,
            payload JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
    )
