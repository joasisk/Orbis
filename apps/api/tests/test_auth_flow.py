from collections.abc import Generator

import app.main as app_main
from app.core.db import Base, get_db
from app.main import app
from app.models import AuditEvent, SessionToken, User  # noqa: F401
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


def test_auth_and_role_access() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)

    try:
        _bootstrap_owner(client)

        owner_tokens = _login(client, "owner@example.com", "Password123!")
        owner_access = owner_tokens["access_token"]
        owner_refresh = owner_tokens["refresh_token"]

        me_response = client.get("/api/v1/users/me", headers=_auth_headers(owner_access))
        assert me_response.status_code == 200
        assert me_response.json()["role"] == "owner"

        owner_spouse_status_before = client.get(
            "/api/v1/users/spouse",
            headers=_auth_headers(owner_access),
        )
        assert owner_spouse_status_before.status_code == 200
        assert owner_spouse_status_before.json()["spouse"] is None

        create_spouse_response = client.post(
            "/api/v1/users/spouse",
            headers=_auth_headers(owner_access),
            json={"email": "spouse@example.com", "password": "SpousePass123!"},
        )
        assert create_spouse_response.status_code == 201
        assert create_spouse_response.json()["role"] == "spouse"

        owner_spouse_status_after = client.get(
            "/api/v1/users/spouse",
            headers=_auth_headers(owner_access),
        )
        assert owner_spouse_status_after.status_code == 200
        assert owner_spouse_status_after.json()["spouse"]["email"] == "spouse@example.com"

        spouse_tokens = _login(client, "spouse@example.com", "SpousePass123!")
        spouse_access = spouse_tokens["access_token"]

        spouse_owner_only_response = client.get(
            "/api/v1/users/owner-only",
            headers=_auth_headers(spouse_access),
        )
        assert spouse_owner_only_response.status_code == 403

        spouse_household_response = client.get(
            "/api/v1/users/household",
            headers=_auth_headers(spouse_access),
        )
        assert spouse_household_response.status_code == 200
        assert spouse_household_response.json()["role"] == "spouse"

        spouse_spouse_status_response = client.get(
            "/api/v1/users/spouse",
            headers=_auth_headers(spouse_access),
        )
        assert spouse_spouse_status_response.status_code == 403

        refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": owner_refresh})
        assert refresh_response.status_code == 200
        rotated_refresh = refresh_response.json()["refresh_token"]
        assert rotated_refresh != owner_refresh

        reuse_old_refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": owner_refresh})
        assert reuse_old_refresh_response.status_code == 401

        logout_response = client.post("/api/v1/auth/logout", json={"refresh_token": rotated_refresh})
        assert logout_response.status_code == 204

        post_logout_refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": rotated_refresh},
        )
        assert post_logout_refresh_response.status_code == 401
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass


def test_bootstrap_status_reflects_claim_state() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)

    try:
        pre_bootstrap_response = client.get("/api/v1/auth/bootstrap-status")
        assert pre_bootstrap_response.status_code == 200
        assert pre_bootstrap_response.json() == {"requires_bootstrap": True}

        _bootstrap_owner(client)

        post_bootstrap_response = client.get("/api/v1/auth/bootstrap-status")
        assert post_bootstrap_response.status_code == 200
        assert post_bootstrap_response.json() == {"requires_bootstrap": False}
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass
