from collections.abc import Generator

import app.main as app_main
from app.core.db import Base, get_db
from app.main import app
from app.models import (  # noqa: F401
    AreaOfLife,
    AuditEvent,
    BlockerEvent,
    EntityVersion,
    FocusSession,
    NoteExtraction,
    Project,
    RecurringCommitment,
    SessionToken,
    Task,
    TaskDependency,
    User,
    WeeklyPlanItem,
    WeeklyPlanProposal,
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


def _seed_tasks(client: TestClient, headers: dict[str, str]) -> list[str]:
    area_resp = client.post("/api/v1/areas", headers=headers, json={"name": "Operations"})
    assert area_resp.status_code == 201
    area_id = area_resp.json()["id"]

    project_resp = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"area_id": area_id, "name": "Maintenance", "is_private": False, "visibility_scope": "shared"},
    )
    assert project_resp.status_code == 201
    project_id = project_resp.json()["id"]

    ids: list[str] = []
    for payload in [
        {"title": "File taxes", "priority": 9, "urgency": 8, "deadline_type": "hard"},
        {"title": "Replace air filter", "priority": 7, "urgency": 5},
        {"title": "Refactor utility script", "priority": 3, "urgency": 2},
    ]:
        resp = client.post("/api/v1/tasks", headers=headers, json={"project_id": project_id, **payload})
        assert resp.status_code == 201
        ids.append(resp.json()["id"])

    return ids


def test_weekly_proposal_generate_and_approve_with_edit() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)
    try:
        token = _bootstrap_and_token(client)
        headers = _headers(token)
        _seed_tasks(client, headers)

        proposal_resp = client.post(
            "/api/v1/planning/weekly-proposals/generate",
            headers=headers,
            json={"week_start_date": "2026-04-13"},
        )
        assert proposal_resp.status_code == 200
        proposal = proposal_resp.json()
        assert proposal["status"] == "proposed"
        assert proposal["provider_key"] == "heuristic-local"
        assert proposal["items"]
        item_id = proposal["items"][0]["id"]

        approve_resp = client.post(
            f"/api/v1/planning/weekly-proposals/{proposal['id']}/approve",
            headers=headers,
            json={"edits": [{"item_id": item_id, "suggested_day": "friday", "suggested_minutes": 60}]},
        )
        assert approve_resp.status_code == 200
        approved = approve_resp.json()
        assert approved["status"] == "approved"
        updated_item = next(item for item in approved["items"] if item["id"] == item_id)
        assert updated_item["suggested_day"] == "friday"
        assert updated_item["suggested_minutes"] == 60

        latest_resp = client.get("/api/v1/planning/weekly-proposals/latest", headers=headers)
        assert latest_resp.status_code == 200
        assert latest_resp.json()["id"] == proposal["id"]
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass


def test_note_extraction_preview_and_accept_creates_tasks() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)
    try:
        token = _bootstrap_and_token(client)
        headers = _headers(token)

        preview_resp = client.post(
            "/api/v1/planning/note-extractions/preview",
            headers=headers,
            json={
                "source_title": "Brain dump",
                "source_ref": "vault://daily/2026-04-15.md",
                "note_content": "- book dentist\n- send project update\n- grocery list",
            },
        )
        assert preview_resp.status_code == 200
        extraction = preview_resp.json()
        assert extraction["status"] == "proposed"
        assert len(extraction["candidate_tasks"]) >= 2

        decide_resp = client.post(
            f"/api/v1/planning/note-extractions/{extraction['id']}/decision",
            headers=headers,
            json={"decision": "accept", "selected_indices": [0, 1]},
        )
        assert decide_resp.status_code == 200
        decided = decide_resp.json()
        assert decided["status"] == "accepted"

        tasks_resp = client.get("/api/v1/tasks", headers=headers)
        assert tasks_resp.status_code == 200
        titles = [item["title"] for item in tasks_resp.json()]
        assert "book dentist" in titles
        assert "send project update" in titles
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass
