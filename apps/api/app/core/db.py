from collections.abc import Generator

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy import create_engine

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
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
