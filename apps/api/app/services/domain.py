from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.domain import AreaOfLife, EntityVersion, Project, RecurringCommitment, Task, TaskDependency
from app.models.user import User

TASK_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "staged": {"primed", "scrubbed"},
    "primed": {"in_flight", "holding", "scrubbed"},
    "in_flight": {"holding", "mission_complete", "scrubbed"},
    "holding": {"primed", "in_flight", "scrubbed"},
    "mission_complete": set(),
    "scrubbed": {"staged"},
}

TASK_STATUS_ACTION_TARGET: dict[str, str] = {
    "prime": "primed",
    "start": "in_flight",
    "hold": "holding",
    "complete": "mission_complete",
    "scrub": "scrubbed",
    "restage": "staged",
}


class DomainService:
    @staticmethod
    def _jsonable(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {k: DomainService._jsonable(v) for k, v in value.items()}
        if isinstance(value, list):
            return [DomainService._jsonable(item) for item in value]
        return value

    @staticmethod
    def _can_view(user: User, entity_owner_id: str, is_private: bool, visibility_scope: str | None) -> bool:
        if user.id == entity_owner_id:
            return True
        if is_private:
            return False
        if user.role == "spouse" and visibility_scope in {"spouse", "shared"}:
            return True
        return False

    @staticmethod
    def _log_version(
        db: Session,
        owner_user_id: str,
        entity_type: str,
        entity_id: str,
        actor_user_id: str,
        event_type: str,
        changed_fields: dict[str, Any],
    ) -> None:
        if not changed_fields and event_type == "update":
            return
        db.add(
            EntityVersion(
                owner_user_id=owner_user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                actor_user_id=actor_user_id,
                event_type=event_type,
                changed_fields=DomainService._jsonable(changed_fields),
            )
        )

    @staticmethod
    def _ensure_owner_or_spouse(user: User, owner_user_id: str) -> None:
        if user.id == owner_user_id:
            return
        if user.role == "spouse":
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    @staticmethod
    def _ensure_owner_only(user: User, owner_user_id: str) -> None:
        if user.id == owner_user_id and user.role == "owner":
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    @staticmethod
    def create_area(db: Session, actor: User, payload: dict[str, Any]) -> AreaOfLife:
        entity = AreaOfLife(owner_user_id=actor.id, **payload)
        db.add(entity)
        db.flush()
        DomainService._log_version(db, actor.id, "area", entity.id, actor.id, "create", payload)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def list_areas(db: Session, actor: User) -> list[AreaOfLife]:
        stmt: Select[tuple[AreaOfLife]] = select(AreaOfLife)
        if actor.role not in {"owner", "spouse"}:
            stmt = stmt.where(AreaOfLife.owner_user_id == actor.id)
        return list(db.scalars(stmt.order_by(AreaOfLife.created_at.desc())).all())

    @staticmethod
    def update_area(db: Session, actor: User, area_id: str, payload: dict[str, Any]) -> AreaOfLife:
        entity = db.scalar(select(AreaOfLife).where(AreaOfLife.id == area_id))
        if entity is None:
            raise HTTPException(status_code=404, detail="Area not found")
        DomainService._ensure_owner_or_spouse(actor, entity.owner_user_id)
        changes = {}
        for key, value in payload.items():
            if getattr(entity, key) != value:
                changes[key] = {"from": getattr(entity, key), "to": value}
                setattr(entity, key, value)
        DomainService._log_version(db, entity.owner_user_id, "area", entity.id, actor.id, "update", changes)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def delete_area(db: Session, actor: User, area_id: str) -> None:
        entity = db.scalar(select(AreaOfLife).where(AreaOfLife.id == area_id))
        if entity is None:
            raise HTTPException(status_code=404, detail="Area not found")
        DomainService._ensure_owner_or_spouse(actor, entity.owner_user_id)
        DomainService._log_version(db, entity.owner_user_id, "area", entity.id, actor.id, "delete", {"id": area_id})
        db.delete(entity)
        db.commit()

    @staticmethod
    def create_project(db: Session, actor: User, payload: dict[str, Any]) -> Project:
        area = db.scalar(select(AreaOfLife).where(AreaOfLife.id == payload["area_id"]))
        if area is None:
            raise HTTPException(status_code=404, detail="Area not found")
        DomainService._ensure_owner_only(actor, area.owner_user_id)
        entity = Project(owner_user_id=area.owner_user_id, **payload)
        db.add(entity)
        db.flush()
        DomainService._log_version(db, entity.owner_user_id, "project", entity.id, actor.id, "create", payload)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def list_projects(db: Session, actor: User, area_id: str | None, status_value: str | None, privacy: str | None) -> list[Project]:
        stmt: Select[tuple[Project]] = select(Project)
        if area_id:
            stmt = stmt.where(Project.area_id == area_id)
        if status_value:
            stmt = stmt.where(Project.status == status_value)
        if privacy == "private":
            stmt = stmt.where(Project.is_private.is_(True))
        elif privacy == "public":
            stmt = stmt.where(Project.is_private.is_(False))
        entities = list(db.scalars(stmt.order_by(Project.created_at.desc())).all())
        return [item for item in entities if DomainService._can_view(actor, item.owner_user_id, item.is_private, item.visibility_scope)]

    @staticmethod
    def get_project(db: Session, actor: User, project_id: str) -> Project:
        entity = db.scalar(select(Project).where(Project.id == project_id))
        if entity is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if not DomainService._can_view(actor, entity.owner_user_id, entity.is_private, entity.visibility_scope):
            raise HTTPException(status_code=403, detail="Forbidden")
        return entity

    @staticmethod
    def update_project(db: Session, actor: User, project_id: str, payload: dict[str, Any]) -> Project:
        entity = DomainService.get_project(db, actor, project_id)
        DomainService._ensure_owner_only(actor, entity.owner_user_id)
        changes = {}
        for key, value in payload.items():
            if getattr(entity, key) != value:
                changes[key] = {"from": getattr(entity, key), "to": value}
                setattr(entity, key, value)
        DomainService._log_version(db, entity.owner_user_id, "project", entity.id, actor.id, "update", changes)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def delete_project(db: Session, actor: User, project_id: str) -> None:
        entity = DomainService.get_project(db, actor, project_id)
        DomainService._ensure_owner_only(actor, entity.owner_user_id)
        DomainService._log_version(db, entity.owner_user_id, "project", entity.id, actor.id, "delete", {"id": project_id})
        db.delete(entity)
        db.commit()

    @staticmethod
    def create_task(db: Session, actor: User, payload: dict[str, Any]) -> Task:
        owner_user_id = actor.id
        payload = payload.copy()
        payload["status"] = "staged"
        if payload.get("project_id"):
            project = db.scalar(select(Project).where(Project.id == payload["project_id"]))
            if project is None:
                raise HTTPException(status_code=404, detail="Project not found")
            DomainService._ensure_owner_only(actor, project.owner_user_id)
            owner_user_id = project.owner_user_id
        entity = Task(owner_user_id=owner_user_id, **payload)
        db.add(entity)
        db.flush()
        DomainService._log_version(db, entity.owner_user_id, "task", entity.id, actor.id, "create", payload)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def list_tasks(
        db: Session, actor: User, project_id: str | None, status_value: str | None, priority: str | None, privacy: str | None
    ) -> list[Task]:
        stmt: Select[tuple[Task]] = select(Task)
        if project_id:
            stmt = stmt.where(Task.project_id == project_id)
        if status_value:
            stmt = stmt.where(Task.status == status_value)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        if privacy == "private":
            stmt = stmt.where(Task.is_private.is_(True))
        elif privacy == "public":
            stmt = stmt.where(Task.is_private.is_(False))
        entities = list(db.scalars(stmt.order_by(Task.created_at.desc())).all())
        return [item for item in entities if DomainService._can_view(actor, item.owner_user_id, item.is_private, item.visibility_scope)]

    @staticmethod
    def get_task(db: Session, actor: User, task_id: str) -> Task:
        entity = db.scalar(select(Task).where(Task.id == task_id))
        if entity is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if not DomainService._can_view(actor, entity.owner_user_id, entity.is_private, entity.visibility_scope):
            raise HTTPException(status_code=403, detail="Forbidden")
        return entity

    @staticmethod
    def update_task(db: Session, actor: User, task_id: str, payload: dict[str, Any]) -> Task:
        entity = DomainService.get_task(db, actor, task_id)
        changes = {}
        payload = payload.copy()
        payload.pop("status", None)
        if actor.role == "owner":
            for field in ("spouse_priority", "spouse_urgency", "spouse_deadline", "spouse_deadline_type"):
                payload.pop(field, None)
            DomainService._ensure_owner_only(actor, entity.owner_user_id)
        elif actor.role == "spouse":
            allowed_fields = {"spouse_priority", "spouse_urgency", "spouse_deadline", "spouse_deadline_type"}
            payload = {k: v for k, v in payload.items() if k in allowed_fields}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        for key, value in payload.items():
            if getattr(entity, key) != value:
                changes[key] = {"from": getattr(entity, key), "to": value}
                setattr(entity, key, value)
        DomainService._log_version(db, entity.owner_user_id, "task", entity.id, actor.id, "update", changes)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def transition_task_status(db: Session, actor: User, task_id: str, action: str) -> Task:
        entity = DomainService.get_task(db, actor, task_id)
        DomainService._ensure_owner_only(actor, entity.owner_user_id)
        target_status = TASK_STATUS_ACTION_TARGET[action]
        current_status = entity.status
        allowed_targets = TASK_STATUS_TRANSITIONS.get(current_status, set())
        if target_status not in allowed_targets:
            raise HTTPException(status_code=422, detail="Invalid status transition")
        entity.status = target_status
        DomainService._log_version(
            db,
            entity.owner_user_id,
            "task",
            entity.id,
            actor.id,
            "status_transition",
            {"status": {"from": current_status, "to": target_status}, "action": action},
        )
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def update_task_spouse_influence(db: Session, actor: User, task_id: str, payload: dict[str, Any]) -> Task:
        entity = DomainService.get_task(db, actor, task_id)
        if actor.role != "spouse":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        allowed_fields = {"spouse_priority", "spouse_urgency", "spouse_deadline", "spouse_deadline_type"}
        changes = {}
        for key, value in payload.items():
            if key not in allowed_fields:
                continue
            if getattr(entity, key) != value:
                changes[key] = {"from": getattr(entity, key), "to": value}
                setattr(entity, key, value)
        DomainService._log_version(
            db,
            entity.owner_user_id,
            "task",
            entity.id,
            actor.id,
            "spouse_influence_update",
            changes,
        )
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def delete_task(db: Session, actor: User, task_id: str) -> None:
        entity = DomainService.get_task(db, actor, task_id)
        DomainService._ensure_owner_only(actor, entity.owner_user_id)
        DomainService._log_version(db, entity.owner_user_id, "task", entity.id, actor.id, "delete", {"id": task_id})
        db.delete(entity)
        db.commit()

    @staticmethod
    def create_recurring_commitment(db: Session, actor: User, payload: dict[str, Any]) -> RecurringCommitment:
        entity = RecurringCommitment(owner_user_id=actor.id, **payload)
        db.add(entity)
        db.flush()
        DomainService._log_version(db, actor.id, "recurring_commitment", entity.id, actor.id, "create", payload)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def list_recurring_commitments(db: Session, actor: User) -> list[RecurringCommitment]:
        rows = list(db.scalars(select(RecurringCommitment)).all())
        return [row for row in rows if actor.id == row.owner_user_id or actor.role == "spouse"]

    @staticmethod
    def get_recurring_commitment(db: Session, actor: User, commitment_id: str) -> RecurringCommitment:
        entity = db.scalar(select(RecurringCommitment).where(RecurringCommitment.id == commitment_id))
        if entity is None:
            raise HTTPException(status_code=404, detail="Recurring commitment not found")
        if actor.id != entity.owner_user_id and actor.role != "spouse":
            raise HTTPException(status_code=403, detail="Forbidden")
        return entity

    @staticmethod
    def update_recurring_commitment(db: Session, actor: User, commitment_id: str, payload: dict[str, Any]) -> RecurringCommitment:
        entity = db.scalar(select(RecurringCommitment).where(RecurringCommitment.id == commitment_id))
        if entity is None:
            raise HTTPException(status_code=404, detail="Recurring commitment not found")
        DomainService._ensure_owner_only(actor, entity.owner_user_id)
        changes = {}
        for key, value in payload.items():
            if getattr(entity, key) != value:
                changes[key] = {"from": getattr(entity, key), "to": value}
                setattr(entity, key, value)
        DomainService._log_version(
            db,
            entity.owner_user_id,
            "recurring_commitment",
            entity.id,
            actor.id,
            "update",
            changes,
        )
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def delete_recurring_commitment(db: Session, actor: User, commitment_id: str) -> None:
        entity = db.scalar(select(RecurringCommitment).where(RecurringCommitment.id == commitment_id))
        if entity is None:
            raise HTTPException(status_code=404, detail="Recurring commitment not found")
        DomainService._ensure_owner_only(actor, entity.owner_user_id)
        DomainService._log_version(
            db,
            entity.owner_user_id,
            "recurring_commitment",
            entity.id,
            actor.id,
            "delete",
            {"id": commitment_id},
        )
        db.delete(entity)
        db.commit()

    @staticmethod
    def create_task_dependency(db: Session, actor: User, task_id: str, depends_on_task_id: str) -> TaskDependency:
        task = DomainService.get_task(db, actor, task_id)
        dependency = DomainService.get_task(db, actor, depends_on_task_id)
        DomainService._ensure_owner_only(actor, task.owner_user_id)
        if task.id == dependency.id:
            raise HTTPException(status_code=422, detail="Task cannot depend on itself")
        if task.owner_user_id != dependency.owner_user_id:
            raise HTTPException(status_code=422, detail="Dependencies must be within the same owner scope")
        if DomainService._would_create_dependency_cycle(db, task.id, dependency.id):
            raise HTTPException(status_code=422, detail="Task dependency cycle detected")
        entity = TaskDependency(owner_user_id=task.owner_user_id, task_id=task.id, depends_on_task_id=dependency.id)
        db.add(entity)
        db.flush()
        DomainService._log_version(
            db,
            entity.owner_user_id,
            "task_dependency",
            entity.id,
            actor.id,
            "create",
            {"task_id": task.id, "depends_on_task_id": dependency.id},
        )
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def list_task_dependencies(db: Session, actor: User, task_id: str | None) -> list[TaskDependency]:
        stmt = select(TaskDependency)
        if task_id:
            stmt = stmt.where(TaskDependency.task_id == task_id)
        rows = list(db.scalars(stmt.order_by(TaskDependency.created_at.desc())).all())
        tasks = {
            task.id: task
            for task in db.scalars(
                select(Task).where(Task.id.in_([row.task_id for row in rows] + [row.depends_on_task_id for row in rows]))
            ).all()
        }
        visible_rows = []
        for row in rows:
            task_item = tasks.get(row.task_id)
            dependency_item = tasks.get(row.depends_on_task_id)
            if task_item is None or dependency_item is None:
                continue
            if not DomainService._can_view(actor, task_item.owner_user_id, task_item.is_private, task_item.visibility_scope):
                continue
            if not DomainService._can_view(
                actor,
                dependency_item.owner_user_id,
                dependency_item.is_private,
                dependency_item.visibility_scope,
            ):
                continue
            visible_rows.append(row)
        return visible_rows

    @staticmethod
    def delete_task_dependency(db: Session, actor: User, dependency_id: str) -> None:
        entity = db.scalar(select(TaskDependency).where(TaskDependency.id == dependency_id))
        if entity is None:
            raise HTTPException(status_code=404, detail="Dependency not found")
        DomainService._ensure_owner_only(actor, entity.owner_user_id)
        DomainService._log_version(
            db,
            entity.owner_user_id,
            "task_dependency",
            entity.id,
            actor.id,
            "delete",
            {"id": dependency_id},
        )
        db.delete(entity)
        db.commit()

    @staticmethod
    def get_entity_history(db: Session, actor: User, entity_type: str, entity_id: str) -> list[EntityVersion]:
        rows = list(
            db.scalars(
                select(EntityVersion)
                .where(EntityVersion.entity_type == entity_type, EntityVersion.entity_id == entity_id)
                .order_by(EntityVersion.created_at.desc())
            ).all()
        )
        if actor.role == "spouse":
            if actor.linked_owner_user_id is None:
                return []
            return [row for row in rows if row.owner_user_id == actor.linked_owner_user_id]
        return [row for row in rows if actor.id == row.owner_user_id]

    @staticmethod
    def _would_create_dependency_cycle(db: Session, task_id: str, depends_on_task_id: str) -> bool:
        frontier = [depends_on_task_id]
        visited: set[str] = set()
        while frontier:
            current_task_id = frontier.pop()
            if current_task_id == task_id:
                return True
            if current_task_id in visited:
                continue
            visited.add(current_task_id)
            next_ids = list(db.scalars(select(TaskDependency.depends_on_task_id).where(TaskDependency.task_id == current_task_id)).all())
            frontier.extend(next_ids)
        return False
