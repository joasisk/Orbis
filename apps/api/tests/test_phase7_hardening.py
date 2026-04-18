from collections.abc import Generator

import app.main as app_main
from app.core.config import settings
from app.core.db import Base, get_db
from app.main import app
from app.models import ApiClientKey, SessionToken, User  # noqa: F401
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


def _client_with_test_db() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = test_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app_main.check_db_connection = lambda: None

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def _bootstrap_owner(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/bootstrap-owner",
        json={"email": "owner@example.com", "password": "Password123!"},
    )
    assert response.status_code == 201


def _owner_token(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_api_key_can_authenticate_and_be_revoked() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)

    try:
        _bootstrap_owner(client)
        token = _owner_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        create_resp = client.post(
            "/api/v1/api-keys",
            headers=headers,
            json={"name": "automation-client", "scopes": ["tasks:read"]},
        )
        assert create_resp.status_code == 201
        created = create_resp.json()
        assert created["api_key"].startswith("orbis_")

        key_headers = {"X-API-Key": created["api_key"]}
        me_resp = client.get("/api/v1/users/me", headers=key_headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "owner@example.com"

        revoke_resp = client.post(f"/api/v1/api-keys/{created['id']}/revoke", headers=headers)
        assert revoke_resp.status_code == 200
        assert revoke_resp.json()["is_active"] is False

        revoked_me = client.get("/api/v1/users/me", headers=key_headers)
        assert revoked_me.status_code == 401
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass


def test_sensitive_auth_endpoints_are_rate_limited() -> None:
    previous_limit = settings.api_rate_limit_requests
    previous_window = settings.api_rate_limit_window_seconds
    app_main.rate_limiter.clear()
    settings.api_rate_limit_requests = 2
    settings.api_rate_limit_window_seconds = 60

    client_gen = _client_with_test_db()
    client = next(client_gen)

    try:
        _bootstrap_owner(client)

        first = client.post("/api/v1/auth/login", json={"email": "owner@example.com", "password": "Password123!"})
        assert first.status_code == 200

        second = client.post("/api/v1/auth/login", json={"email": "owner@example.com", "password": "Password123!"})
        assert second.status_code == 200

        third = client.post("/api/v1/auth/login", json={"email": "owner@example.com", "password": "Password123!"})
        assert third.status_code == 429
    finally:
        settings.api_rate_limit_requests = previous_limit
        settings.api_rate_limit_window_seconds = previous_window
        app_main.rate_limiter.clear()
        try:
            next(client_gen)
        except StopIteration:
            pass
