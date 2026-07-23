import json
import secrets

import psycopg

from .models import SharedReflectionRequest


class ShareRepository:
    """Persist snapshots that users explicitly choose to share."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self._initialize_schema()

    def save(self, payload: SharedReflectionRequest) -> str:
        share_id = secrets.token_urlsafe(16)
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                "INSERT INTO shared_reflections (id, payload) VALUES (%s, %s::jsonb)",
                (share_id, json.dumps(payload.model_dump(mode="json"))),
            )
        return share_id

    def get(self, share_id: str) -> SharedReflectionRequest | None:
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                "SELECT payload FROM shared_reflections WHERE id = %s",
                (share_id,),
            ).fetchone()
        if row is None:
            return None
        return SharedReflectionRequest.model_validate(row[0])

    def _initialize_schema(self) -> None:
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS shared_reflections (
            id TEXT PRIMARY KEY,
            payload JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
            )
