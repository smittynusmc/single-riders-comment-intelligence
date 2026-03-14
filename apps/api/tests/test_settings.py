from app.core.config import Settings


def test_normalize_postgresql_database_url_to_psycopg() -> None:
    settings = Settings(database_url="postgresql://postgres:password@db.example.com:5432/comment_intelligence")

    assert settings.database_url == "postgresql+psycopg://postgres:password@db.example.com:5432/comment_intelligence"


def test_normalize_postgres_database_url_to_psycopg() -> None:
    settings = Settings(database_url="postgres://postgres:password@db.example.com:5432/comment_intelligence")

    assert settings.database_url == "postgresql+psycopg://postgres:password@db.example.com:5432/comment_intelligence"


def test_preserve_database_url_with_explicit_driver() -> None:
    settings = Settings(database_url="postgresql+psycopg://postgres:password@db.example.com:5432/comment_intelligence")

    assert settings.database_url == "postgresql+psycopg://postgres:password@db.example.com:5432/comment_intelligence"
