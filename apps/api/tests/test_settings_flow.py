from collections.abc import Generator

import app.main as app_main
from app.core.db import Base, get_db
from app.main import app
from app.models import User, UserSettings  # noqa: F401
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


def _bootstrap_owner(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/bootstrap-owner",
        json={"email": "owner@example.com", "password": "Password123!"},
    )
    assert response.status_code == 201


def _login(client: TestClient, email: str, password: str) -> dict:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()


def _auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


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


def test_owner_can_get_and_patch_settings() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)

    try:
        _bootstrap_owner(client)
        owner_tokens = _login(client, "owner@example.com", "Password123!")
        headers = _auth_headers(owner_tokens["access_token"])

        get_resp = client.get("/api/v1/settings/me", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["ai_require_manual_approval"] is True

        patch_resp = client.patch(
            "/api/v1/settings/me",
            headers=headers,
            json={
                "reminder_enabled": False,
                "calendar_connected": True,
                "calendar_provider": "mock-calendar",
                "notes_connected": True,
                "notes_provider": "mock-notes",
                "ai_auto_generate_weekly": True,
                "ai_require_manual_approval": True,
            },
        )
        assert patch_resp.status_code == 200
        payload = patch_resp.json()
        assert payload["reminder_enabled"] is False
        assert payload["calendar_connected"] is True
        assert payload["calendar_provider"] == "mock-calendar"
        assert payload["ai_auto_generate_weekly"] is True
        assert payload["ai_require_manual_approval"] is True
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass


def test_guardrail_rejects_disabling_manual_approval_when_auto_generation_on() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)

    try:
        _bootstrap_owner(client)
        owner_tokens = _login(client, "owner@example.com", "Password123!")
        headers = _auth_headers(owner_tokens["access_token"])

        invalid_resp = client.patch(
            "/api/v1/settings/me",
            headers=headers,
            json={"ai_auto_generate_weekly": True, "ai_require_manual_approval": False},
        )
        assert invalid_resp.status_code == 422
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass
