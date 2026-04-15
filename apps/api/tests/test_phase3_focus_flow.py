from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db
import app.main as app_main
from app.main import app
from app.models import (  # noqa: F401
    AreaOfLife,
    AuditEvent,
    BlockerEvent,
    EntityVersion,
    FocusSession,
    Project,
    RecurringCommitment,
    SessionToken,
    Task,
    TaskDependency,
    User,
)


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


def _bootstrap_and_token(client: TestClient) -> str:
    bootstrap_response = client.post(
        "/api/v1/auth/bootstrap-owner",
        json={"email": "owner@example.com", "password": "Password123!"},
    )
    assert bootstrap_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "Password123!"},
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def _headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def _task_id(client: TestClient, headers: dict[str, str]) -> str:
    area_resp = client.post("/api/v1/areas", headers=headers, json={"name": "Work"})
    assert area_resp.status_code == 201
    area_id = area_resp.json()["id"]

    project_resp = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"area_id": area_id, "name": "Q2", "is_private": False, "visibility_scope": "shared"},
    )
    assert project_resp.status_code == 201
    project_id = project_resp.json()["id"]

    task_resp = client.post(
        "/api/v1/tasks",
        headers=headers,
        json={"project_id": project_id, "title": "Deep work", "priority": 8, "urgency": 8},
    )
    assert task_resp.status_code == 201
    return task_resp.json()["id"]


def test_focus_start_sidetrack_unable_and_overload_signal() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)
    try:
        token = _bootstrap_and_token(client)
        headers = _headers(token)
        task_id = _task_id(client, headers)

        start_resp = client.post(
            "/api/v1/focus/start",
            headers=headers,
            json={"task_id": task_id, "pre_task_energy": 4},
        )
        assert start_resp.status_code == 200
        session_id = start_resp.json()["id"]

        sidetrack_resp = client.post(
            "/api/v1/focus/sidetrack",
            headers=headers,
            json={"session_id": session_id, "blocker_reason": "missing_dependency", "note": "waiting on docs"},
        )
        assert sidetrack_resp.status_code == 200
        assert sidetrack_resp.json()["focus_session_id"] == session_id

        unable_resp = client.post(
            "/api/v1/focus/unable",
            headers=headers,
            json={
                "session_id": session_id,
                "unable_reason": "blocked by missing files",
                "blocker_reason": "missing_dependency",
                "post_task_energy": 2,
            },
        )
        assert unable_resp.status_code == 200

        plan_resp = client.get("/api/v1/planning/daily-plan", headers=headers, params={"limit": 5, "current_energy": 3})
        assert plan_resp.status_code == 200
        payload = plan_resp.json()
        assert payload["overload_risk_level"] in {"low", "medium", "high"}
        assert isinstance(payload["drivers"], list)
        assert isinstance(payload["recommended_reset_actions"], list)
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass


def test_focus_stop_is_idempotent() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)
    try:
        token = _bootstrap_and_token(client)
        headers = _headers(token)
        task_id = _task_id(client, headers)

        start_resp = client.post(
            "/api/v1/focus/start",
            headers=headers,
            json={"task_id": task_id, "pre_task_energy": 5},
        )
        session_id = start_resp.json()["id"]

        stop_resp = client.post(
            "/api/v1/focus/stop",
            headers=headers,
            json={"session_id": session_id, "post_task_energy": 4},
        )
        assert stop_resp.status_code == 200
        assert stop_resp.json()["status"] == "completed"

        stop_resp_2 = client.post(
            "/api/v1/focus/stop",
            headers=headers,
            json={"session_id": session_id, "post_task_energy": 3},
        )
        assert stop_resp_2.status_code == 200
        assert stop_resp_2.json()["status"] == "completed"
        assert stop_resp_2.json()["post_task_energy"] == 4
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass
