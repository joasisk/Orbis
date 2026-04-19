from collections.abc import Generator

import app.main as app_main
from app.core.db import Base, get_db
from app.main import app
from app.models import (  # noqa: F401
    AreaOfLife,
    AuditEvent,
    BlockerEvent,
    CalendarExternalEvent,
    CalendarSoftBlock,
    DailySchedule,
    DailyScheduleItem,
    EntityVersion,
    FocusSession,
    NoteExtraction,
    Project,
    RecurringCommitment,
    ReminderEvent,
    SessionToken,
    Task,
    TaskDependency,
    User,
    WeeklyPlanItem,
    WeeklyPlanProposal,
    WeeklySchedule,
)
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
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


def test_weekly_schedule_lifecycle_and_daily_item_telemetry() -> None:
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
        proposal_id = proposal_resp.json()["id"]

        generate_schedule_resp = client.post(
            "/api/v1/schedules/weeks/generate",
            headers=headers,
            json={"week_start_date": "2026-04-13", "source_proposal_id": proposal_id},
        )
        assert generate_schedule_resp.status_code == 200
        weekly = generate_schedule_resp.json()
        assert weekly["status"] == "proposed"
        assert len(weekly["days"]) == 7
        assert weekly["source_proposal_id"] == proposal_id

        accept_week_resp = client.post(f"/api/v1/schedules/weeks/{weekly['id']}/accept", headers=headers)
        assert accept_week_resp.status_code == 200
        accepted = accept_week_resp.json()
        assert accepted["status"] == "accepted"
        monday = accepted["days"][0]
        assert monday["items"]

        patch_day_resp = client.patch(
            f"/api/v1/schedules/days/{monday['id']}",
            headers=headers,
            json={"mood_score": 4, "morning_energy": 0.7, "self_evaluation": "solid start"},
        )
        assert patch_day_resp.status_code == 200
        patched_day = patch_day_resp.json()
        assert patched_day["status"] == "adjusted"
        item_id = patched_day["items"][0]["id"]

        patch_item_resp = client.patch(
            f"/api/v1/schedules/day-items/{item_id}",
            headers=headers,
            json={"outcome_status": "done", "actual_minutes": 42, "distraction_count": 1},
        )
        assert patch_item_resp.status_code == 200
        updated_day = patch_item_resp.json()
        updated_item = next(item for item in updated_day["items"] if item["id"] == item_id)
        assert updated_item["outcome_status"] == "done"
        assert updated_item["actual_minutes"] == 42

        start_focus_resp = client.post(
            f"/api/v1/schedules/day-items/{item_id}/start-focus",
            headers=headers,
            json={"pre_task_energy": 6.5},
        )
        assert start_focus_resp.status_code == 200

        end_focus_resp = client.post(
            f"/api/v1/schedules/day-items/{item_id}/end-focus",
            headers=headers,
            json={"post_task_energy": 6.0},
        )
        assert end_focus_resp.status_code == 200

        get_day_resp = client.get("/api/v1/schedules/days/2026-04-13", headers=headers)
        assert get_day_resp.status_code == 200
        assert get_day_resp.json()["id"] == monday["id"]
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass


def test_reminder_event_capture_and_response_logging() -> None:
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
        proposal_id = proposal_resp.json()["id"]

        generate_schedule_resp = client.post(
            "/api/v1/schedules/weeks/generate",
            headers=headers,
            json={"week_start_date": "2026-04-13", "source_proposal_id": proposal_id},
        )
        assert generate_schedule_resp.status_code == 200
        monday = generate_schedule_resp.json()["days"][0]
        monday_item = monday["items"][0]

        create_reminder_resp = client.post(
            "/api/v1/reminders/events",
            headers=headers,
            json={
                "daily_schedule_id": monday["id"],
                "daily_schedule_item_id": monday_item["id"],
                "delivery_channel": "in_app",
            },
        )
        assert create_reminder_resp.status_code == 200
        reminder = create_reminder_resp.json()
        assert reminder["response_status"] == "pending"

        list_pending_resp = client.get("/api/v1/reminders/events", headers=headers)
        assert list_pending_resp.status_code == 200
        pending_events = list_pending_resp.json()
        assert len(pending_events) == 1
        assert pending_events[0]["id"] == reminder["id"]

        response_resp = client.patch(
            f"/api/v1/reminders/events/{reminder['id']}/response",
            headers=headers,
            json={"response_status": "acknowledged"},
        )
        assert response_resp.status_code == 200
        responded = response_resp.json()
        assert responded["response_status"] == "acknowledged"
        assert responded["responded_at"] is not None
        assert responded["response_delay_seconds"] is not None

        list_after_response_resp = client.get("/api/v1/reminders/events", headers=headers)
        assert list_after_response_resp.status_code == 200
        assert list_after_response_resp.json() == []

        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)
        try:
            owner = db.scalar(select(User).where(User.email == "owner@example.com"))
            assert owner is not None
            reminder_audit_rows = list(
                db.scalars(
                    select(AuditEvent)
                    .where(
                        AuditEvent.actor_user_id == owner.id,
                        AuditEvent.event_type.in_(["reminder.event_created", "reminder.response_recorded"]),
                    )
                    .order_by(AuditEvent.created_at.asc())
                ).all()
            )
            assert len(reminder_audit_rows) >= 2
        finally:
            db.close()

        next_proposal_resp = client.post(
            "/api/v1/planning/weekly-proposals/generate",
            headers=headers,
            json={"week_start_date": "2026-04-20"},
        )
        assert next_proposal_resp.status_code == 200
        telemetry = next_proposal_resp.json()["evaluation_log"]["telemetry_snapshot"]
        assert telemetry["reminder_response_count"] >= 1
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass


def test_phase5_calendar_import_and_soft_block_export_requires_acceptance() -> None:
    client_gen = _client_with_test_db()
    client = next(client_gen)
    try:
        token = _bootstrap_and_token(client)
        headers = _headers(token)
        _seed_tasks(client, headers)

        settings_resp = client.patch(
            "/api/v1/settings/me",
            headers=headers,
            json={"calendar_connected": True, "calendar_provider": "mock-calendar"},
        )
        assert settings_resp.status_code == 200

        import_resp = client.post(
            "/api/v1/calendar/events/import",
            headers=headers,
            json={"start_date": "2026-04-13", "end_date": "2026-04-17"},
        )
        assert import_resp.status_code == 200
        imported = import_resp.json()
        assert imported["imported_count"] > 0
        assert imported["events"][0]["provider_key"] == "mock-calendar"

        proposal_resp = client.post(
            "/api/v1/planning/weekly-proposals/generate",
            headers=headers,
            json={"week_start_date": "2026-04-13"},
        )
        assert proposal_resp.status_code == 200
        proposal_id = proposal_resp.json()["id"]

        generate_schedule_resp = client.post(
            "/api/v1/schedules/weeks/generate",
            headers=headers,
            json={"week_start_date": "2026-04-13", "source_proposal_id": proposal_id},
        )
        assert generate_schedule_resp.status_code == 200
        monday = generate_schedule_resp.json()["days"][0]

        export_conflict_resp = client.post(
            f"/api/v1/calendar/daily-schedules/{monday['id']}/soft-blocks/export",
            headers=headers,
        )
        assert export_conflict_resp.status_code == 409

        accept_day_resp = client.post(f"/api/v1/schedules/days/{monday['id']}/accept", headers=headers)
        assert accept_day_resp.status_code == 200

        export_resp = client.post(
            f"/api/v1/calendar/daily-schedules/{monday['id']}/soft-blocks/export",
            headers=headers,
        )
        assert export_resp.status_code == 200
        exported = export_resp.json()
        assert exported["exported_count"] == len(exported["blocks"])
        assert exported["blocks"]
        assert exported["blocks"][0]["provider_key"] == "mock-calendar"
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass


def test_phase5_adaptive_reminder_scheduler_respects_window_and_throttle() -> None:
    from datetime import UTC, datetime

    from app.services.reminders import ReminderService

    client_gen = _client_with_test_db()
    client = next(client_gen)
    try:
        token = _bootstrap_and_token(client)
        headers = _headers(token)
        _seed_tasks(client, headers)

        settings_resp = client.patch(
            "/api/v1/settings/me",
            headers=headers,
            json={"reminder_enabled": True, "reminder_window_start": "08:00", "reminder_window_end": "20:00"},
        )
        assert settings_resp.status_code == 200

        proposal_resp = client.post(
            "/api/v1/planning/weekly-proposals/generate",
            headers=headers,
            json={"week_start_date": "2026-04-13"},
        )
        assert proposal_resp.status_code == 200
        proposal_id = proposal_resp.json()["id"]

        generate_schedule_resp = client.post(
            "/api/v1/schedules/weeks/generate",
            headers=headers,
            json={"week_start_date": "2026-04-13", "source_proposal_id": proposal_id},
        )
        assert generate_schedule_resp.status_code == 200
        monday = generate_schedule_resp.json()["days"][0]

        accept_day_resp = client.post(f"/api/v1/schedules/days/{monday['id']}/accept", headers=headers)
        assert accept_day_resp.status_code == 200

        db_gen = app.dependency_overrides[get_db]()
        db = next(db_gen)
        try:
            actor = db.scalar(select(User).where(User.email == "owner@example.com"))
            assert actor is not None

            created_off_hours = ReminderService.schedule_due_events(
                db=db,
                actor=actor,
                now=datetime(2026, 4, 13, 6, 0, tzinfo=UTC),
            )
            assert created_off_hours == []

            created_first = ReminderService.schedule_due_events(
                db=db,
                actor=actor,
                now=datetime(2026, 4, 13, 10, 0, tzinfo=UTC),
            )
            assert len(created_first) >= 1

            created_second = ReminderService.schedule_due_events(
                db=db,
                actor=actor,
                now=datetime(2026, 4, 13, 10, 20, tzinfo=UTC),
            )
            assert created_second == []

            delivered_logs = list(
                db.scalars(
                    select(AuditEvent).where(
                        AuditEvent.actor_user_id == actor.id,
                        AuditEvent.event_type == "reminder.delivered",
                    )
                ).all()
            )
            assert len(delivered_logs) == len(created_first)
            assert delivered_logs[0].event_metadata["daily_schedule_item_id"] is not None
        finally:
            db.close()
    finally:
        try:
            next(client_gen)
        except StopIteration:
            pass
