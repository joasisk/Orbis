from collections.abc import Generator
from datetime import UTC, datetime, timedelta

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


def test_daily_plan_hard_deadline_priority_and_dependency_readiness() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)
    try:
        token = _bootstrap_and_token(client)
        headers = _headers(token)

        area_resp = client.post("/api/v1/areas", headers=headers, json={"name": "Work"})
        assert area_resp.status_code == 201
        area_id = area_resp.json()["id"]

        project_resp = client.post(
            "/api/v1/projects",
            headers=headers,
            json={"area_id": area_id, "name": "Q2 Deliverables", "is_private": False, "visibility_scope": "shared"},
        )
        assert project_resp.status_code == 201
        project_id = project_resp.json()["id"]

        hard_due_soon = (datetime.now(UTC) + timedelta(hours=10)).isoformat()
        low_priority_hard_resp = client.post(
            "/api/v1/tasks",
            headers=headers,
            json={
                "project_id": project_id,
                "title": "Legal filing",
                "priority": 1,
                "urgency": 1,
                "deadline": hard_due_soon,
                "deadline_type": "hard",
            },
        )
        assert low_priority_hard_resp.status_code == 201

        base_task_resp = client.post(
            "/api/v1/tasks",
            headers=headers,
            json={"project_id": project_id, "title": "Prepare docs", "priority": 8, "urgency": 7},
        )
        assert base_task_resp.status_code == 201
        base_task_id = base_task_resp.json()["id"]

        blocked_task_resp = client.post(
            "/api/v1/tasks",
            headers=headers,
            json={"project_id": project_id, "title": "Submit package", "priority": 9, "urgency": 8},
        )
        assert blocked_task_resp.status_code == 201
        blocked_task_id = blocked_task_resp.json()["id"]

        dep_resp = client.post(
            "/api/v1/task-dependencies",
            headers=headers,
            json={"task_id": blocked_task_id, "depends_on_task_id": base_task_id},
        )
        assert dep_resp.status_code == 201

        ranking_resp = client.get("/api/v1/planning/daily-plan", headers=headers, params={"limit": 3, "current_energy": 5})
        assert ranking_resp.status_code == 200
        payload = ranking_resp.json()
        recommendations = payload["recommendations"]
        assert recommendations[0]["title"] == "Legal filing"
        assert payload["primary_recommendation"]["task_id"] == recommendations[0]["task_id"]
        assert len(payload["fallback_recommendations"]) == 2

        blocked = next(item for item in recommendations if item["task_id"] == blocked_task_id)
        assert "dependency_not_ready" in blocked["reasons"]
        assert blocked["score_breakdown"]["dependency_readiness"] < 0
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass


def test_daily_plan_is_deterministic_for_same_input() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)
    try:
        token = _bootstrap_and_token(client)
        headers = _headers(token)

        area_resp = client.post("/api/v1/areas", headers=headers, json={"name": "Admin"})
        assert area_resp.status_code == 201
        area_id = area_resp.json()["id"]

        project_resp = client.post(
            "/api/v1/projects",
            headers=headers,
            json={"area_id": area_id, "name": "Ops", "is_private": False, "visibility_scope": "shared"},
        )
        assert project_resp.status_code == 201
        project_id = project_resp.json()["id"]

        for payload in [
            {"title": "A", "priority": 5, "urgency": 6},
            {"title": "B", "priority": 8, "urgency": 2},
            {"title": "C", "priority": 3, "urgency": 9},
        ]:
            resp = client.post("/api/v1/tasks", headers=headers, json={"project_id": project_id, **payload})
            assert resp.status_code == 201

        first = client.get("/api/v1/planning/daily-plan", headers=headers, params={"limit": 3, "current_energy": 6})
        second = client.get("/api/v1/planning/daily-plan", headers=headers, params={"limit": 3, "current_energy": 6})
        assert first.status_code == 200
        assert second.status_code == 200

        first_order = [item["task_id"] for item in first.json()["recommendations"]]
        second_order = [item["task_id"] for item in second.json()["recommendations"]]
        assert first_order == second_order
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass
