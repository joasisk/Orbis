from collections.abc import Generator

import app.main as app_main
from app.core.db import get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError


class _BrokenSession:
    def scalar(self, _: object) -> None:
        raise OperationalError("SELECT 1", {}, ConnectionError("db unavailable"))

    def close(self) -> None:
        return


def _client_with_broken_db() -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[_BrokenSession, None, None]:
        db = _BrokenSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app_main.check_db_connection = lambda: None

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_returns_503_when_database_operational_error_occurs() -> None:
    client_gen = _client_with_broken_db()
    client = next(client_gen)

    try:
        response = client.get("/api/v1/auth/bootstrap-status")
        assert response.status_code == 503
        assert response.json() == {"detail": "Database temporarily unavailable. Verify database connectivity and try again."}
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass
