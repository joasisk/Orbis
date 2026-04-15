from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.phase2 import Task, TaskDependency
from app.models.user import User
from app.schemas.phase3 import (
    DailyPlanRecommendation,
    DailyPlanResponse,
    DailyPlanScoreBreakdown,
)
from app.services.phase2 import Phase2Service

TERMINAL_TASK_STATUSES = {"done", "completed", "cancelled", "archived"}


class Phase3Service:
    @staticmethod
    def get_daily_plan(
        db: Session,
        actor: User,
        limit: int,
        current_energy: float | None,
    ) -> DailyPlanResponse:
        all_tasks = list(db.scalars(select(Task)).all())
        visible_tasks = [
            task
            for task in all_tasks
            if Phase2Service._can_view(actor, task.owner_user_id, task.is_private, task.visibility_scope)
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
            rec = Phase3Service._score_task(
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

        return DailyPlanResponse(
            generated_at=datetime.now(UTC),
            recommendations=top,
            overload_risk_level="low",
            drivers=[],
            recommended_reset_actions=[],
        )

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

        if task.spouse_priority is not None:
            breakdown.spouse_influence += float(task.spouse_priority) * 2
            if task.spouse_priority >= 7:
                reasons.append("high_spouse_priority")

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
