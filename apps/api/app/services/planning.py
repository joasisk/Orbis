from datetime import UTC, date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Task
from app.models.focus import FocusSession
from app.models.planning import (
    DailySchedule,
    DailyScheduleItem,
    NoteExtraction,
    WeeklyPlanItem,
    WeeklyPlanProposal,
    WeeklySchedule,
)
from app.models.reminder import ReminderEvent
from app.models.user import User
from app.schemas.planning import (
    DailyScheduleItemFocusEndRequest,
    DailyScheduleItemFocusStartRequest,
    DailyScheduleItemPatchRequest,
    DailySchedulePatchRequest,
    DailyScheduleResponse,
    NoteExtractionDecisionRequest,
    NoteExtractionResponse,
    NoteTaskCandidateResponse,
    WeeklyPlanApproveRequest,
    WeeklyPlanGenerateRequest,
    WeeklyPlanItemResponse,
    WeeklyPlanProposalResponse,
    WeeklyScheduleGenerateRequest,
    WeeklyScheduleResponse,
)
from app.services.ai import PROMPT_TEMPLATE_VERSION, get_default_provider

TERMINAL_TASK_STATUSES = {"done", "completed", "cancelled", "archived"}


class PlanningService:
    @staticmethod
    def generate_weekly_proposal(db: Session, actor: User, payload: WeeklyPlanGenerateRequest) -> WeeklyPlanProposalResponse:
        provider = get_default_provider()

        tasks = list(
            db.scalars(
                select(Task).where(
                    Task.owner_user_id == actor.id,
                )
            ).all()
        )
        candidates = [task for task in tasks if task.status.lower() not in TERMINAL_TASK_STATUSES]
        suggestions = provider.generate_weekly_plan(candidates)

        proposal = WeeklyPlanProposal(
            owner_user_id=actor.id,
            week_start_date=payload.week_start_date,
            status="proposed",
            provider_key=provider.provider_key,
            prompt_template_version=PROMPT_TEMPLATE_VERSION,
            evaluation_log={
                "candidate_task_count": len(candidates),
                "proposed_item_count": len(suggestions),
                "generated_at": datetime.now(UTC).isoformat(),
                "telemetry_snapshot": PlanningService.planner_telemetry_snapshot(db, actor),
            },
        )
        db.add(proposal)
        db.flush()

        items: list[WeeklyPlanItem] = []
        for rank, suggestion in enumerate(suggestions, start=1):
            item = WeeklyPlanItem(
                proposal_id=proposal.id,
                owner_user_id=actor.id,
                task_id=suggestion.task_id,
                suggested_day=suggestion.suggested_day,
                suggested_minutes=suggestion.suggested_minutes,
                rationale=suggestion.rationale,
                rank=rank,
            )
            db.add(item)
            items.append(item)

        db.commit()
        db.refresh(proposal)
        for item in items:
            db.refresh(item)

        return PlanningService._proposal_response(proposal, items)

    @staticmethod
    def get_latest_weekly_proposal(db: Session, actor: User) -> WeeklyPlanProposalResponse:
        proposal = db.scalar(
            select(WeeklyPlanProposal)
            .where(WeeklyPlanProposal.owner_user_id == actor.id)
            .order_by(WeeklyPlanProposal.created_at.desc())
            .limit(1)
        )
        if proposal is None:
            raise HTTPException(status_code=404, detail="No weekly proposal found")

        items = list(
            db.scalars(
                select(WeeklyPlanItem)
                .where(WeeklyPlanItem.proposal_id == proposal.id)
                .order_by(WeeklyPlanItem.rank.asc(), WeeklyPlanItem.created_at.asc())
            ).all()
        )
        return PlanningService._proposal_response(proposal, items)

    @staticmethod
    def approve_weekly_proposal(
        db: Session,
        actor: User,
        proposal_id: str,
        payload: WeeklyPlanApproveRequest,
    ) -> WeeklyPlanProposalResponse:
        proposal = db.scalar(select(WeeklyPlanProposal).where(WeeklyPlanProposal.id == proposal_id))
        if proposal is None:
            raise HTTPException(status_code=404, detail="Weekly proposal not found")
        if proposal.owner_user_id != actor.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        if proposal.status != "proposed":
            raise HTTPException(status_code=409, detail="Proposal is no longer pending approval")

        items = list(db.scalars(select(WeeklyPlanItem).where(WeeklyPlanItem.proposal_id == proposal.id)).all())
        item_lookup = {item.id: item for item in items}

        for edit in payload.edits:
            item = item_lookup.get(edit.item_id)
            if item is None:
                raise HTTPException(status_code=404, detail=f"Proposal item not found: {edit.item_id}")
            if edit.suggested_day is not None:
                item.suggested_day = edit.suggested_day
            if edit.suggested_minutes is not None:
                item.suggested_minutes = edit.suggested_minutes
            if edit.rationale is not None:
                item.rationale = edit.rationale

        proposal.status = "approved"
        proposal.approved_at = datetime.now(UTC)
        db.commit()
        db.refresh(proposal)
        for item in items:
            db.refresh(item)

        return PlanningService._proposal_response(proposal, items)

    @staticmethod
    def preview_note_extraction(
        db: Session,
        actor: User,
        source_title: str,
        source_ref: str | None,
        note_content: str,
    ) -> NoteExtractionResponse:
        provider = get_default_provider()
        candidates = provider.extract_task_candidates(note_content)
        extraction = NoteExtraction(
            owner_user_id=actor.id,
            source_title=source_title,
            source_ref=source_ref,
            note_content=note_content,
            provider_key=provider.provider_key,
            candidate_tasks=[{"title": candidate.title, "notes": candidate.notes} for candidate in candidates],
            status="proposed",
        )
        db.add(extraction)
        db.commit()
        db.refresh(extraction)
        return PlanningService._extraction_response(extraction)

    @staticmethod
    def decide_note_extraction(
        db: Session,
        actor: User,
        extraction_id: str,
        payload: NoteExtractionDecisionRequest,
    ) -> NoteExtractionResponse:
        extraction = db.scalar(select(NoteExtraction).where(NoteExtraction.id == extraction_id))
        if extraction is None:
            raise HTTPException(status_code=404, detail="Note extraction not found")
        if extraction.owner_user_id != actor.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        if extraction.status != "proposed":
            return PlanningService._extraction_response(extraction)

        if payload.decision == "dismiss":
            extraction.status = "dismissed"
            extraction.reviewed_at = datetime.now(UTC)
            db.commit()
            db.refresh(extraction)
            return PlanningService._extraction_response(extraction)

        for index in payload.selected_indices:
            if index < 0 or index >= len(extraction.candidate_tasks):
                raise HTTPException(status_code=422, detail=f"selected index out of range: {index}")
            candidate = extraction.candidate_tasks[index]
            task = Task(
                owner_user_id=actor.id,
                project_id=None,
                title=str(candidate["title"]),
                notes=candidate.get("notes"),
                status="todo",
                is_private=False,
                visibility_scope="shared",
            )
            db.add(task)

        extraction.status = "accepted"
        extraction.reviewed_at = datetime.now(UTC)
        extraction.candidate_tasks = [
            {**candidate, "selected": idx in payload.selected_indices} for idx, candidate in enumerate(extraction.candidate_tasks)
        ]
        db.commit()
        db.refresh(extraction)
        return PlanningService._extraction_response(extraction)

    @staticmethod
    def _proposal_response(proposal: WeeklyPlanProposal, items: list[WeeklyPlanItem]) -> WeeklyPlanProposalResponse:
        return WeeklyPlanProposalResponse(
            id=proposal.id,
            week_start_date=proposal.week_start_date,
            status=proposal.status,
            provider_key=proposal.provider_key,
            prompt_template_version=proposal.prompt_template_version,
            created_at=proposal.created_at,
            approved_at=proposal.approved_at,
            evaluation_log=proposal.evaluation_log,
            items=[
                WeeklyPlanItemResponse(
                    id=item.id,
                    task_id=item.task_id,
                    suggested_day=item.suggested_day,
                    suggested_minutes=item.suggested_minutes,
                    rationale=item.rationale,
                    rank=item.rank,
                )
                for item in items
            ],
        )

    @staticmethod
    def _extraction_response(extraction: NoteExtraction) -> NoteExtractionResponse:
        return NoteExtractionResponse(
            id=extraction.id,
            source_title=extraction.source_title,
            source_ref=extraction.source_ref,
            status=extraction.status,
            provider_key=extraction.provider_key,
            created_at=extraction.created_at,
            reviewed_at=extraction.reviewed_at,
            candidate_tasks=[
                NoteTaskCandidateResponse(title=str(candidate.get("title", "")), notes=candidate.get("notes"))
                for candidate in extraction.candidate_tasks
            ],
        )

    @staticmethod
    def generate_weekly_schedule(db: Session, actor: User, payload: WeeklyScheduleGenerateRequest) -> WeeklyScheduleResponse:
        existing = db.scalar(
            select(WeeklySchedule).where(
                WeeklySchedule.owner_user_id == actor.id,
                WeeklySchedule.week_start_date == payload.week_start_date,
            )
        )
        if existing is not None:
            raise HTTPException(status_code=409, detail="Weekly schedule already exists for week_start_date")

        source_proposal = PlanningService._resolve_source_proposal(db, actor, payload.source_proposal_id, payload.week_start_date)
        proposal_items = list(
            db.scalars(
                select(WeeklyPlanItem)
                .where(WeeklyPlanItem.proposal_id == source_proposal.id)
                .order_by(WeeklyPlanItem.rank.asc(), WeeklyPlanItem.created_at.asc())
            ).all()
        )
        week_dates = [payload.week_start_date + timedelta(days=offset) for offset in range(7)]
        week_by_label = {week_date.strftime("%A").lower(): week_date for week_date in week_dates}

        weekly_schedule = WeeklySchedule(
            owner_user_id=actor.id,
            week_start_date=payload.week_start_date,
            status="proposed",
            source_proposal_id=source_proposal.id,
        )
        db.add(weekly_schedule)
        db.flush()

        daily_schedules: dict[date, DailySchedule] = {}
        for week_date in week_dates:
            daily_schedule = DailySchedule(
                weekly_schedule_id=weekly_schedule.id,
                owner_user_id=actor.id,
                schedule_date=week_date,
                status="proposed",
            )
            db.add(daily_schedule)
            db.flush()
            daily_schedules[week_date] = daily_schedule

        for item in proposal_items:
            day_date = week_by_label.get(item.suggested_day.lower(), payload.week_start_date)
            db.add(
                DailyScheduleItem(
                    daily_schedule_id=daily_schedules[day_date].id,
                    owner_user_id=actor.id,
                    task_id=item.task_id,
                    planned_minutes=item.suggested_minutes,
                    outcome_status="planned",
                    order_index=item.rank,
                    distraction_count=0,
                )
            )

        db.commit()
        return PlanningService.get_weekly_schedule_by_date(db=db, actor=actor, week_start_date=payload.week_start_date)

    @staticmethod
    def get_weekly_schedule_by_date(db: Session, actor: User, week_start_date: date) -> WeeklyScheduleResponse:
        weekly_schedule = db.scalar(
            select(WeeklySchedule).where(
                WeeklySchedule.owner_user_id == actor.id,
                WeeklySchedule.week_start_date == week_start_date,
            )
        )
        if weekly_schedule is None:
            raise HTTPException(status_code=404, detail="Weekly schedule not found")
        return PlanningService._weekly_schedule_response(db, weekly_schedule)

    @staticmethod
    def accept_weekly_schedule(db: Session, actor: User, weekly_schedule_id: str) -> WeeklyScheduleResponse:
        weekly_schedule = PlanningService._owned_weekly_schedule_or_404(db, actor, weekly_schedule_id)
        if weekly_schedule.status == "accepted":
            return PlanningService._weekly_schedule_response(db, weekly_schedule)
        if weekly_schedule.status == "rejected":
            raise HTTPException(status_code=409, detail="Rejected schedules cannot be accepted")
        weekly_schedule.status = "accepted"
        weekly_schedule.accepted_at = datetime.now(UTC)
        day_schedules = list(db.scalars(select(DailySchedule).where(DailySchedule.weekly_schedule_id == weekly_schedule.id)).all())
        for day in day_schedules:
            if day.status == "proposed":
                day.status = "accepted"
        db.commit()
        db.refresh(weekly_schedule)
        return PlanningService._weekly_schedule_response(db, weekly_schedule)

    @staticmethod
    def reject_weekly_schedule(db: Session, actor: User, weekly_schedule_id: str) -> WeeklyScheduleResponse:
        weekly_schedule = PlanningService._owned_weekly_schedule_or_404(db, actor, weekly_schedule_id)
        if weekly_schedule.status == "accepted":
            raise HTTPException(status_code=409, detail="Accepted schedules cannot be rejected")
        weekly_schedule.status = "rejected"
        db.commit()
        db.refresh(weekly_schedule)
        return PlanningService._weekly_schedule_response(db, weekly_schedule)

    @staticmethod
    def get_daily_schedule_by_date(db: Session, actor: User, schedule_date: date) -> DailyScheduleResponse:
        schedule = db.scalar(
            select(DailySchedule)
            .where(DailySchedule.owner_user_id == actor.id, DailySchedule.schedule_date == schedule_date)
            .order_by(DailySchedule.created_at.desc())
        )
        if schedule is None:
            raise HTTPException(status_code=404, detail="Daily schedule not found")
        return PlanningService._daily_schedule_response(db, schedule)

    @staticmethod
    def accept_daily_schedule(db: Session, actor: User, daily_schedule_id: str) -> DailyScheduleResponse:
        schedule = PlanningService._owned_daily_schedule_or_404(db, actor, daily_schedule_id)
        if schedule.status == "proposed":
            schedule.status = "accepted"
            db.commit()
            db.refresh(schedule)
        return PlanningService._daily_schedule_response(db, schedule)

    @staticmethod
    def patch_daily_schedule(
        db: Session,
        actor: User,
        daily_schedule_id: str,
        payload: DailySchedulePatchRequest,
    ) -> DailyScheduleResponse:
        schedule = PlanningService._owned_daily_schedule_or_404(db, actor, daily_schedule_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(schedule, key, value)
        if update_data and schedule.status == "accepted":
            schedule.status = "adjusted"
        db.commit()
        db.refresh(schedule)
        return PlanningService._daily_schedule_response(db, schedule)

    @staticmethod
    def patch_daily_schedule_item(
        db: Session,
        actor: User,
        daily_schedule_item_id: str,
        payload: DailyScheduleItemPatchRequest,
    ) -> DailyScheduleResponse:
        item = PlanningService._owned_day_item_or_404(db, actor, daily_schedule_item_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        if item.outcome_status == "postponed" and item.postponed_to_date is None:
            raise HTTPException(status_code=422, detail="postponed_to_date is required for postponed outcome")
        if item.outcome_status != "postponed":
            item.postponed_to_date = None

        day_schedule = PlanningService._owned_daily_schedule_or_404(db, actor, item.daily_schedule_id)
        if day_schedule.status == "accepted":
            day_schedule.status = "adjusted"
        db.commit()
        db.refresh(day_schedule)
        return PlanningService._daily_schedule_response(db, day_schedule)

    @staticmethod
    def start_day_item_focus(
        db: Session,
        actor: User,
        daily_schedule_item_id: str,
        payload: DailyScheduleItemFocusStartRequest,
    ) -> DailyScheduleResponse:
        item = PlanningService._owned_day_item_or_404(db, actor, daily_schedule_item_id)
        active = db.scalar(select(FocusSession).where(FocusSession.owner_user_id == actor.id, FocusSession.status == "active"))
        if active is not None and active.task_id != item.task_id:
            raise HTTPException(status_code=409, detail="An active focus session already exists")
        if active is None:
            db.add(
                FocusSession(
                    owner_user_id=actor.id,
                    task_id=item.task_id,
                    status="active",
                    pre_task_energy=payload.pre_task_energy,
                )
            )
            db.commit()
        day_schedule = PlanningService._owned_daily_schedule_or_404(db, actor, item.daily_schedule_id)
        return PlanningService._daily_schedule_response(db, day_schedule)

    @staticmethod
    def end_day_item_focus(
        db: Session,
        actor: User,
        daily_schedule_item_id: str,
        payload: DailyScheduleItemFocusEndRequest,
    ) -> DailyScheduleResponse:
        item = PlanningService._owned_day_item_or_404(db, actor, daily_schedule_item_id)
        active = db.scalar(
            select(FocusSession).where(
                FocusSession.owner_user_id == actor.id,
                FocusSession.task_id == item.task_id,
                FocusSession.status == "active",
            )
        )
        if active is not None:
            active.status = "completed"
            active.post_task_energy = payload.post_task_energy
            active.ended_at = datetime.now(UTC)
            db.commit()
        day_schedule = PlanningService._owned_daily_schedule_or_404(db, actor, item.daily_schedule_id)
        return PlanningService._daily_schedule_response(db, day_schedule)

    @staticmethod
    def planner_telemetry_snapshot(db: Session, actor: User) -> dict[str, float | int | None]:
        rows = list(
            db.scalars(
                select(DailyScheduleItem).where(
                    DailyScheduleItem.owner_user_id == actor.id,
                    DailyScheduleItem.outcome_status.in_(["done", "failed", "partial", "postponed", "skipped"]),
                )
            ).all()
        )
        reminder_rows = list(
            db.scalars(
                select(ReminderEvent).where(
                    ReminderEvent.owner_user_id == actor.id,
                    ReminderEvent.response_status.in_(["acknowledged", "snoozed", "dismissed"]),
                )
            ).all()
        )

        reminder_response_seconds = [
            reminder.response_delay_seconds
            for reminder in reminder_rows
            if reminder.response_delay_seconds is not None
        ]
        reminder_metrics = {
            "reminder_response_count": len(reminder_rows),
            "avg_reminder_response_seconds": (
                sum(reminder_response_seconds) / len(reminder_response_seconds) if reminder_response_seconds else None
            ),
        }

        if not rows:
            return {"total_items": 0, "avg_actual_minutes": None, "avg_distraction_count": None, **reminder_metrics}
        actual_minutes = [item.actual_minutes for item in rows if item.actual_minutes is not None]
        distractions = [item.distraction_count for item in rows]
        return {
            "total_items": len(rows),
            "avg_actual_minutes": (sum(actual_minutes) / len(actual_minutes)) if actual_minutes else None,
            "avg_distraction_count": sum(distractions) / len(distractions),
            **reminder_metrics,
        }

    @staticmethod
    def _resolve_source_proposal(db: Session, actor: User, source_proposal_id: str | None, week_start_date: date) -> WeeklyPlanProposal:
        proposal_query = select(WeeklyPlanProposal).where(WeeklyPlanProposal.owner_user_id == actor.id)
        if source_proposal_id is not None:
            proposal_query = proposal_query.where(WeeklyPlanProposal.id == source_proposal_id)
        else:
            proposal_query = proposal_query.where(WeeklyPlanProposal.week_start_date == date.isoformat(week_start_date))
        proposal = db.scalar(proposal_query.order_by(WeeklyPlanProposal.created_at.desc()))
        if proposal is None:
            raise HTTPException(status_code=404, detail="Weekly proposal not found for schedule generation")
        return proposal

    @staticmethod
    def _owned_weekly_schedule_or_404(db: Session, actor: User, weekly_schedule_id: str) -> WeeklySchedule:
        schedule = db.scalar(select(WeeklySchedule).where(WeeklySchedule.id == weekly_schedule_id))
        if schedule is None:
            raise HTTPException(status_code=404, detail="Weekly schedule not found")
        if schedule.owner_user_id != actor.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return schedule

    @staticmethod
    def _owned_daily_schedule_or_404(db: Session, actor: User, daily_schedule_id: str) -> DailySchedule:
        schedule = db.scalar(select(DailySchedule).where(DailySchedule.id == daily_schedule_id))
        if schedule is None:
            raise HTTPException(status_code=404, detail="Daily schedule not found")
        if schedule.owner_user_id != actor.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return schedule

    @staticmethod
    def _owned_day_item_or_404(db: Session, actor: User, daily_schedule_item_id: str) -> DailyScheduleItem:
        item = db.scalar(select(DailyScheduleItem).where(DailyScheduleItem.id == daily_schedule_item_id))
        if item is None:
            raise HTTPException(status_code=404, detail="Daily schedule item not found")
        if item.owner_user_id != actor.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return item

    @staticmethod
    def _weekly_schedule_response(db: Session, schedule: WeeklySchedule) -> WeeklyScheduleResponse:
        days = list(
            db.scalars(
                select(DailySchedule).where(DailySchedule.weekly_schedule_id == schedule.id).order_by(DailySchedule.schedule_date.asc())
            ).all()
        )
        return WeeklyScheduleResponse(
            id=schedule.id,
            week_start_date=schedule.week_start_date,
            status=schedule.status,
            source_proposal_id=schedule.source_proposal_id,
            created_at=schedule.created_at,
            accepted_at=schedule.accepted_at,
            days=[PlanningService._daily_schedule_response(db, day) for day in days],
        )

    @staticmethod
    def _daily_schedule_response(db: Session, schedule: DailySchedule) -> DailyScheduleResponse:
        items = list(
            db.scalars(
                select(DailyScheduleItem)
                .where(DailyScheduleItem.daily_schedule_id == schedule.id)
                .order_by(DailyScheduleItem.order_index.asc(), DailyScheduleItem.created_at.asc())
            ).all()
        )
        return DailyScheduleResponse(
            id=schedule.id,
            weekly_schedule_id=schedule.weekly_schedule_id,
            schedule_date=schedule.schedule_date,
            status=schedule.status,
            mood_score=schedule.mood_score,
            morning_energy=schedule.morning_energy,
            evening_energy=schedule.evening_energy,
            self_evaluation=schedule.self_evaluation,
            items=[
                {
                    "id": item.id,
                    "task_id": item.task_id,
                    "planned_minutes": item.planned_minutes,
                    "actual_minutes": item.actual_minutes,
                    "outcome_status": item.outcome_status,
                    "order_index": item.order_index,
                    "distraction_count": item.distraction_count,
                    "distraction_notes": item.distraction_notes,
                    "postponed_to_date": item.postponed_to_date,
                    "failure_reason": item.failure_reason,
                }
                for item in items
            ],
        )


def default_week_start() -> str:
    now = datetime.now(UTC).date()
    monday = now - timedelta(days=now.weekday())
    return date.isoformat(monday)
