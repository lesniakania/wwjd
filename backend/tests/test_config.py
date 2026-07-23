from app.config import Settings


def test_database_url_defaults_to_local_postgres(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = Settings(_env_file=None)

    assert settings.database_url == "postgresql://wwjd:secret@localhost:5434/wwjd"
