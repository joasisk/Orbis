from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Task, TaskDependency
from app.models.focus import BlockerEvent, FocusSession
from app.models.user import User
from app.schemas.focus import (
    BlockerReason,
    DailyPlanRecommendation,
    DailyPlanResponse,
    DailyPlanScoreBreakdown,
)
from app.services.domain import DomainService

TERMINAL_TASK_STATUSES = {"done", "completed", "cancelled", "archived"}


class FocusService:
    @staticmethod
    def get_daily_plan(
        db: Session,
        actor: User,
        limit: int,
        current_energy: float | None,
    ) -> DailyPlanResponse:
        all_tasks = list(db.scalars(select(Task)).all())
        visible_tasks = [
            task for task in all_tasks if DomainService._can_view(actor, task.owner_user_id, task.is_private, task.visibility_scope)
        ]
        candidate_tasks = [task for task in visible_tasks if task.status.lower() not in TERMINAL_TASK_STATUSES]

        dependencies = list(
            db.scalars(select(TaskDependency).where(TaskDependency.task_id.in_([task.id for task in candidate_tasks]))).all()
        )
        task_lookup = {task.id: task for task in all_tasks}
        deps_by_task: dict[str, list[TaskDependency]] = {}
        for dep in dependencies:
            deps_by_task.setdefault(dep.task_id, []).append(dep)

        recommendations: list[DailyPlanRecommendation] = []
        for task in candidate_tasks:
            rec = FocusService._score_task(
                task=task,
                task_lookup=task_lookup,
                task_dependencies=deps_by_task.get(task.id, []),
                current_energy=current_energy,
            )
            recommendations.append(rec)

        recommendations.sort(
            key=lambda item: (
                -item.score,
                item.task_id,
            )
        )
        top = recommendations[:limit]
        overload = FocusService._compute_overload_signals(db, actor)

        return DailyPlanResponse(
            generated_at=datetime.now(UTC),
            recommendations=top,
            primary_recommendation=top[0] if top else None,
            fallback_recommendations=top[1:] if len(top) > 1 else [],
            overload_risk_level=overload["level"],
            drivers=overload["drivers"],
            recommended_reset_actions=overload["actions"],
        )

    @staticmethod
    def start_focus_session(db: Session, actor: User, task_id: str, pre_task_energy: float) -> FocusSession:
        task = db.scalar(select(Task).where(Task.id == task_id))
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if not DomainService._can_view(actor, task.owner_user_id, task.is_private, task.visibility_scope):
            raise HTTPException(status_code=403, detail="Forbidden")
        active = db.scalar(select(FocusSession).where(FocusSession.owner_user_id == actor.id, FocusSession.status == "active"))
        if active is not None:
            if active.task_id == task_id:
                return active
            raise HTTPException(status_code=409, detail="An active focus session already exists")

        session = FocusSession(owner_user_id=actor.id, task_id=task_id, pre_task_energy=pre_task_energy, status="active")
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def stop_focus_session(db: Session, actor: User, session_id: str, post_task_energy: float) -> FocusSession:
        session = FocusService._owned_session_or_404(db, actor, session_id)
        if session.status != "active":
            return session
        session.status = "completed"
        session.post_task_energy = post_task_energy
        session.ended_at = datetime.now(UTC)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def sidetrack_focus_session(
        db: Session,
        actor: User,
        session_id: str,
        blocker_reason: BlockerReason,
        note: str | None,
    ) -> tuple[FocusSession, BlockerEvent]:
        session = FocusService._owned_session_or_404(db, actor, session_id)
        if session.status != "active":
            raise HTTPException(status_code=409, detail="Sidetrack is only valid for an active session")

        event = BlockerEvent(
            owner_user_id=actor.id,
            task_id=session.task_id,
            focus_session_id=session.id,
            blocker_reason=blocker_reason,
            note=note,
        )
        session.sidetrack_count += 1
        if note:
            session.sidetrack_note = note
        db.add(event)
        db.commit()
        db.refresh(session)
        db.refresh(event)
        return session, event

    @staticmethod
    def unable_focus_session(
        db: Session,
        actor: User,
        session_id: str,
        unable_reason: str,
        blocker_reason: BlockerReason,
        post_task_energy: float,
        note: str | None,
    ) -> tuple[FocusSession, BlockerEvent]:
        session = FocusService._owned_session_or_404(db, actor, session_id)
        if session.status != "active":
            return session, FocusService._latest_blocker_event(db, session.id)

        event = BlockerEvent(
            owner_user_id=actor.id,
            task_id=session.task_id,
            focus_session_id=session.id,
            blocker_reason=blocker_reason,
            note=note,
        )
        session.status = "unable"
        session.unable_reason = unable_reason
        session.post_task_energy = post_task_energy
        session.ended_at = datetime.now(UTC)
        db.add(event)
        db.commit()
        db.refresh(session)
        db.refresh(event)
        return session, event

    @staticmethod
    def _owned_session_or_404(db: Session, actor: User, session_id: str) -> FocusSession:
        session = db.scalar(select(FocusSession).where(FocusSession.id == session_id))
        if session is None:
            raise HTTPException(status_code=404, detail="Focus session not found")
        if session.owner_user_id != actor.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return session

    @staticmethod
    def _latest_blocker_event(db: Session, session_id: str) -> BlockerEvent:
        event = db.scalar(
            select(BlockerEvent).where(BlockerEvent.focus_session_id == session_id).order_by(BlockerEvent.created_at.desc()).limit(1)
        )
        if event is None:
            raise HTTPException(status_code=409, detail="Session is no longer active")
        return event

    @staticmethod
    def _compute_overload_signals(db: Session, actor: User) -> dict[str, list[str] | str]:
        now = datetime.now(UTC)
        window_start = now - timedelta(days=7)
        sessions = list(
            db.scalars(
                select(FocusSession).where(
                    FocusSession.owner_user_id == actor.id,
                    FocusSession.created_at >= window_start,
                )
            ).all()
        )
        blockers_count = db.query(BlockerEvent).filter(BlockerEvent.owner_user_id == actor.id).count()

        unable_count = len([s for s in sessions if s.status == "unable"])
        low_post_energy_count = len([s for s in sessions if s.post_task_energy is not None and s.post_task_energy <= 3])
        active_count = len([s for s in sessions if s.status == "active"])

        drivers: list[str] = []
        actions: list[str] = []
        score = 0

        if unable_count >= 2:
            score += 2
            drivers.append("repeated_unable_to_finish")
            actions.append("choose_one_smaller_task")
        if blockers_count >= 3:
            score += 1
            drivers.append("high_blocker_frequency")
            actions.append("clear_dependencies_first")
        if low_post_energy_count >= 2:
            score += 2
            drivers.append("persistently_low_post_task_energy")
            actions.append("schedule_20_min_recovery_break")
        if active_count > 1:
            score += 1
            drivers.append("too_many_open_focus_sessions")
            actions.append("close_or_stop_current_session")

        if score >= 4:
            level = "high"
        elif score >= 2:
            level = "medium"
        else:
            level = "low"

        if level == "low" and not actions:
            actions = ["keep_current_pace"]

        return {"level": level, "drivers": drivers, "actions": actions}

    @staticmethod
    def _score_task(
        task: Task,
        task_lookup: dict[str, Task],
        task_dependencies: list[TaskDependency],
        current_energy: float | None,
    ) -> DailyPlanRecommendation:
        reasons: list[str] = []
        breakdown = DailyPlanScoreBreakdown()

        if task.deadline is not None:
            now = datetime.now(UTC)
            deadline = task.deadline
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=UTC)
            days_until = (deadline - now).total_seconds() / 86400
            if task.deadline_type == "hard":
                if days_until <= 0:
                    breakdown.deadlines += 130
                    reasons.append("hard_deadline_overdue")
                elif days_until <= 1:
                    breakdown.deadlines += 115
                    reasons.append("hard_deadline_within_24h")
                elif days_until <= 3:
                    breakdown.deadlines += 95
                    reasons.append("hard_deadline_soon")
                else:
                    breakdown.deadlines += 80
                    reasons.append("has_hard_deadline")
            else:
                if days_until <= 0:
                    breakdown.deadlines += 90
                    reasons.append("soft_deadline_overdue")
                elif days_until <= 3:
                    breakdown.deadlines += 70
                    reasons.append("soft_deadline_soon")
                else:
                    breakdown.deadlines += 50
                    reasons.append("has_soft_deadline")

        if task.priority is not None:
            breakdown.priority += float(task.priority) * 4
            if task.priority >= 7:
                reasons.append("high_priority")

        if task.urgency is not None:
            breakdown.urgency += float(task.urgency) * 3
            if task.urgency >= 7:
                reasons.append("high_urgency")

        spouse_priority = float(task.spouse_priority) if task.spouse_priority is not None else 0.0
        spouse_urgency = float(task.spouse_urgency) if task.spouse_urgency is not None else 0.0
        spouse_deadline_pressure = 0.0
        if task.spouse_deadline is not None:
            spouse_deadline = task.spouse_deadline
            if spouse_deadline.tzinfo is None:
                spouse_deadline = spouse_deadline.replace(tzinfo=UTC)
            spouse_days_until = (spouse_deadline - datetime.now(UTC)).total_seconds() / 86400
            if task.spouse_deadline_type == "hard":
                if spouse_days_until <= 1:
                    spouse_deadline_pressure = 26.0
                    reasons.append("spouse_hard_deadline_within_24h")
                elif spouse_days_until <= 3:
                    spouse_deadline_pressure = 18.0
                    reasons.append("spouse_hard_deadline_soon")
            elif spouse_days_until <= 3:
                spouse_deadline_pressure = 8.0
                reasons.append("spouse_soft_deadline_soon")

        critical_household_signal = (
            spouse_priority >= 8 or spouse_urgency >= 8 or (task.spouse_deadline_type == "hard" and spouse_deadline_pressure > 0)
        )
        spouse_weight = 1.75 if critical_household_signal else 1.0
        spouse_influence_raw = (spouse_priority * 2.0) + (spouse_urgency * 1.5) + spouse_deadline_pressure
        breakdown.spouse_influence += spouse_influence_raw * spouse_weight
        if spouse_priority >= 7:
            reasons.append("high_spouse_priority")
        if spouse_urgency >= 7:
            reasons.append("high_spouse_urgency")
        if critical_household_signal and spouse_influence_raw > 0:
            reasons.append("critical_household_weight_applied")

        unresolved_dependencies = 0
        for dep in task_dependencies:
            depends_on = task_lookup.get(dep.depends_on_task_id)
            if depends_on is None:
                unresolved_dependencies += 1
                continue
            if depends_on.status.lower() not in TERMINAL_TASK_STATUSES:
                unresolved_dependencies += 1

        if unresolved_dependencies > 0:
            breakdown.dependency_readiness -= unresolved_dependencies * 40
            reasons.append("dependency_not_ready")
        else:
            breakdown.dependency_readiness += 15
            reasons.append("dependencies_ready")

        if current_energy is not None:
            energy_demand = float(task.urgency) if task.urgency is not None else 5.0
            energy_gap = current_energy - energy_demand
            if energy_gap >= 2:
                breakdown.energy_fit += 15
                reasons.append("good_energy_fit")
            elif energy_gap >= -1:
                breakdown.energy_fit += 5
                reasons.append("acceptable_energy_fit")
            else:
                breakdown.energy_fit -= 12
                reasons.append("poor_energy_fit")

        score = (
            breakdown.deadlines
            + breakdown.priority
            + breakdown.urgency
            + breakdown.energy_fit
            + breakdown.dependency_readiness
            + breakdown.spouse_influence
        )

        return DailyPlanRecommendation(
            task_id=task.id,
            title=task.title,
            status=task.status,
            score=round(score, 2),
            reasons=reasons,
            score_breakdown=breakdown,
        )
