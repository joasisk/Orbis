from app.core.config import Settings


def test_database_url_percent_encodes_credentials() -> None:
    settings = Settings(
        POSTGRES_USER="orbis:user",
        POSTGRES_PASSWORD="p@ss/w:rd#1",
        POSTGRES_HOST="db",
        POSTGRES_PORT=5432,
        POSTGRES_DB="orbis",
    )

    assert settings.database_url == "postgresql+psycopg://orbis%3Auser:p%40ss%2Fw%3Ard%231@db:5432/orbis"
