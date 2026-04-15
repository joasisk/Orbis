from collections.abc import Generator
from time import sleep

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings

Base = declarative_base()

engine: Engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> None:
    max_attempts = 5
    retry_delay_seconds = 1

    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except OperationalError as exc:
            if attempt == max_attempts:
                if "password authentication failed" in str(exc).lower():
                    raise RuntimeError(
                        "Database authentication failed. "
                        "Verify POSTGRES_USER/POSTGRES_PASSWORD in .env match the credentials used to "
                        "initialize the database volume. If you changed credentials after first startup, "
                        "reset the Postgres volume and recreate containers."
                    ) from exc
                raise RuntimeError(
                    "Database is unreachable after multiple attempts. "
                    "Ensure the database container is running and POSTGRES_HOST/POSTGRES_PORT are correct."
                ) from exc
            sleep(retry_delay_seconds)
