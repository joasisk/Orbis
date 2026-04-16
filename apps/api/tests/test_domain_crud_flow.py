from collections.abc import Generator

import app.main as app_main
from app.core.db import Base, get_db
from app.main import app
from app.models import (
    AreaOfLife,  # noqa: F401
    AuditEvent,  # noqa: F401
    EntityVersion,  # noqa: F401
    Project,  # noqa: F401
    RecurringCommitment,  # noqa: F401
    SessionToken,  # noqa: F401
    Task,  # noqa: F401
    TaskDependency,  # noqa: F401
    User,  # noqa: F401
)
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


def _create_and_login_spouse(client: TestClient, owner_token: str) -> str:
    spouse_create_response = client.post(
        "/api/v1/users/spouse",
        headers=_headers(owner_token),
        json={"email": "spouse@example.com", "password": "Password123!"},
    )
    assert spouse_create_response.status_code == 201
    spouse_login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "spouse@example.com", "password": "Password123!"},
    )
    assert spouse_login_response.status_code == 200
    return spouse_login_response.json()["access_token"]


def test_domain_crud_and_history_flow() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)
    try:
        token = _bootstrap_and_token(client)
        headers = _headers(token)

        area_resp = client.post(
            "/api/v1/areas",
            headers=headers,
            json={"name": "Health", "description": "Body and mind"},
        )
        assert area_resp.status_code == 201
        area_id = area_resp.json()["id"]

        project_resp = client.post(
            "/api/v1/projects",
            headers=headers,
            json={
                "area_id": area_id,
                "name": "Get fit",
                "description": "Exercise plan",
                "is_private": False,
                "visibility_scope": "shared",
                "priority": 7,
                "urgency": 6,
            },
        )
        assert project_resp.status_code == 201
        project_id = project_resp.json()["id"]

        task_resp = client.post(
            "/api/v1/tasks",
            headers=headers,
            json={
                "project_id": project_id,
                "title": "Run 5k",
                "notes": "Keep easy pace",
                "priority": 8,
                "urgency": 5,
                "is_private": False,
                "visibility_scope": "shared",
            },
        )
        assert task_resp.status_code == 201
        task_id = task_resp.json()["id"]

        update_task_resp = client.patch(
            f"/api/v1/tasks/{task_id}",
            headers=headers,
            json={"status": "in_progress", "priority": 9},
        )
        assert update_task_resp.status_code == 200
        assert update_task_resp.json()["status"] == "in_progress"

        task_list_resp = client.get("/api/v1/tasks", headers=headers, params={"project_id": project_id, "priority": 9})
        assert task_list_resp.status_code == 200
        assert len(task_list_resp.json()) == 1

        dependency_resp = client.post(
            "/api/v1/task-dependencies",
            headers=headers,
            json={"task_id": task_id, "depends_on_task_id": task_id},
        )
        assert dependency_resp.status_code == 422

        recurring_resp = client.post(
            "/api/v1/recurring-commitments",
            headers=headers,
            json={
                "title": "Weekly planning",
                "cadence": "weekly",
                "interval_count": 1,
                "starts_on": "2026-04-15T09:00:00Z",
                "ends_on": "2026-12-31T09:00:00Z",
            },
        )
        assert recurring_resp.status_code == 201

        history_resp = client.get(f"/api/v1/history/task/{task_id}", headers=headers)
        assert history_resp.status_code == 200
        events = [row["event_type"] for row in history_resp.json()]
        assert "create" in events
        assert "update" in events
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass


def test_domain_write_authorization_cycle_and_recurring_detail() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)
    try:
        owner_token = _bootstrap_and_token(client)
        spouse_token = _create_and_login_spouse(client, owner_token)
        owner_headers = _headers(owner_token)
        spouse_headers = _headers(spouse_token)

        area_resp = client.post(
            "/api/v1/areas",
            headers=owner_headers,
            json={"name": "Work", "description": "Career planning"},
        )
        assert area_resp.status_code == 201
        area_id = area_resp.json()["id"]

        spouse_areas_resp = client.get("/api/v1/areas", headers=spouse_headers)
        assert spouse_areas_resp.status_code == 200
        assert len(spouse_areas_resp.json()) == 1
        assert spouse_areas_resp.json()[0]["id"] == area_id

        project_resp = client.post(
            "/api/v1/projects",
            headers=owner_headers,
            json={
                "area_id": area_id,
                "name": "Promotion prep",
                "is_private": False,
                "visibility_scope": "shared",
            },
        )
        assert project_resp.status_code == 201
        project_id = project_resp.json()["id"]

        spouse_update_project_resp = client.patch(
            f"/api/v1/projects/{project_id}",
            headers=spouse_headers,
            json={"name": "Not allowed"},
        )
        assert spouse_update_project_resp.status_code == 403

        spouse_create_project_resp = client.post(
            "/api/v1/projects",
            headers=spouse_headers,
            json={
                "area_id": area_id,
                "name": "Spouse unauthorized project",
                "is_private": False,
                "visibility_scope": "shared",
            },
        )
        assert spouse_create_project_resp.status_code == 403

        task_a_resp = client.post(
            "/api/v1/tasks",
            headers=owner_headers,
            json={"project_id": project_id, "title": "Task A"},
        )
        assert task_a_resp.status_code == 201
        task_a_id = task_a_resp.json()["id"]

        task_b_resp = client.post(
            "/api/v1/tasks",
            headers=owner_headers,
            json={"project_id": project_id, "title": "Task B"},
        )
        assert task_b_resp.status_code == 201
        task_b_id = task_b_resp.json()["id"]

        dep_resp = client.post(
            "/api/v1/task-dependencies",
            headers=owner_headers,
            json={"task_id": task_b_id, "depends_on_task_id": task_a_id},
        )
        assert dep_resp.status_code == 201

        cycle_resp = client.post(
            "/api/v1/task-dependencies",
            headers=owner_headers,
            json={"task_id": task_a_id, "depends_on_task_id": task_b_id},
        )
        assert cycle_resp.status_code == 422

        spouse_list_dependencies_resp = client.get("/api/v1/task-dependencies", headers=spouse_headers)
        assert spouse_list_dependencies_resp.status_code == 200
        assert len(spouse_list_dependencies_resp.json()) == 1

        recurring_create_resp = client.post(
            "/api/v1/recurring-commitments",
            headers=owner_headers,
            json={
                "title": "Weekly review",
                "cadence": "weekly",
                "interval_count": 1,
                "starts_on": "2026-04-15T09:00:00Z",
            },
        )
        assert recurring_create_resp.status_code == 201
        commitment_id = recurring_create_resp.json()["id"]

        recurring_detail_resp = client.get(f"/api/v1/recurring-commitments/{commitment_id}", headers=owner_headers)
        assert recurring_detail_resp.status_code == 200
        assert recurring_detail_resp.json()["id"] == commitment_id

        spouse_update_recurring_resp = client.patch(
            f"/api/v1/recurring-commitments/{commitment_id}",
            headers=spouse_headers,
            json={"title": "Not allowed"},
        )
        assert spouse_update_recurring_resp.status_code == 403
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass
