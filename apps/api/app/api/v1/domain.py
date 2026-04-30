from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.schemas.domain import (
    AreaCreate,
    AreaRead,
    AreaUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    RecurringCommitmentCreate,
    RecurringCommitmentRead,
    RecurringCommitmentUpdate,
    TaskCreate,
    TaskDependencyCreate,
    TaskDependencyRead,
    TaskRead,
    TaskSpouseInfluenceUpdate,
    TaskStatusTransition,
    TaskUpdate,
    VersionResponse,
)
from app.services.domain import DomainService

router = APIRouter(tags=["domain"])


@router.post("/areas", response_model=AreaRead, status_code=status.HTTP_201_CREATED)
def create_area(payload: AreaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> AreaRead:
    area = DomainService.create_area(db, current_user, payload.model_dump())
    return AreaRead.model_validate(area, from_attributes=True)


@router.get("/areas", response_model=list[AreaRead])
def list_areas(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[AreaRead]:
    rows = DomainService.list_areas(db, current_user)
    return [AreaRead.model_validate(item, from_attributes=True) for item in rows]


@router.patch("/areas/{area_id}", response_model=AreaRead)
def update_area(
    area_id: str,
    payload: AreaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AreaRead:
    area = DomainService.update_area(db, current_user, area_id, payload.model_dump(exclude_unset=True))
    return AreaRead.model_validate(area, from_attributes=True)


@router.delete("/areas/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_area(area_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Response:
    DomainService.delete_area(db, current_user, area_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    project = DomainService.create_project(db, current_user, payload.model_dump())
    return ProjectRead.model_validate(project, from_attributes=True)


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(
    area_id: str | None = None,
    status_value: str | None = Query(default=None, alias="status"),
    privacy: str | None = Query(default=None, pattern="^(private|public)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectRead]:
    rows = DomainService.list_projects(db, current_user, area_id, status_value, privacy)
    return [ProjectRead.model_validate(item, from_attributes=True) for item in rows]


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ProjectRead:
    row = DomainService.get_project(db, current_user, project_id)
    return ProjectRead.model_validate(row, from_attributes=True)


@router.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    row = DomainService.update_project(db, current_user, project_id, payload.model_dump(exclude_unset=True))
    return ProjectRead.model_validate(row, from_attributes=True)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    DomainService.delete_project(db, current_user, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TaskRead:
    row = DomainService.create_task(db, current_user, payload.model_dump())
    return TaskRead.model_validate(row, from_attributes=True)


@router.get("/tasks", response_model=list[TaskRead])
def list_tasks(
    project_id: str | None = None,
    status_value: str | None = Query(default=None, alias="status"),
    priority: str | None = Query(default=None, pattern="^(core|major|minor|ambient)$"),
    privacy: str | None = Query(default=None, pattern="^(private|public)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskRead]:
    rows = DomainService.list_tasks(db, current_user, project_id, status_value, priority, privacy)
    return [TaskRead.model_validate(row, from_attributes=True) for row in rows]


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TaskRead:
    row = DomainService.get_task(db, current_user, task_id)
    return TaskRead.model_validate(row, from_attributes=True)


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    row = DomainService.update_task(db, current_user, task_id, payload.model_dump(exclude_unset=True))
    return TaskRead.model_validate(row, from_attributes=True)


@router.post("/tasks/{task_id}/status-transition", response_model=TaskRead)
def transition_task_status(
    task_id: str,
    payload: TaskStatusTransition,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    row = DomainService.transition_task_status(db, current_user, task_id, payload.action)
    return TaskRead.model_validate(row, from_attributes=True)


@router.patch("/tasks/{task_id}/spouse-influence", response_model=TaskRead)
def update_task_spouse_influence(
    task_id: str,
    payload: TaskSpouseInfluenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("spouse")),
) -> TaskRead:
    row = DomainService.update_task_spouse_influence(db, current_user, task_id, payload.model_dump(exclude_unset=True))
    return TaskRead.model_validate(row, from_attributes=True)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Response:
    DomainService.delete_task(db, current_user, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/recurring-commitments", response_model=RecurringCommitmentRead, status_code=status.HTTP_201_CREATED)
def create_recurring_commitment(
    payload: RecurringCommitmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecurringCommitmentRead:
    row = DomainService.create_recurring_commitment(db, current_user, payload.model_dump())
    return RecurringCommitmentRead.model_validate(row, from_attributes=True)


@router.get("/recurring-commitments", response_model=list[RecurringCommitmentRead])
def list_recurring_commitments(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[RecurringCommitmentRead]:
    rows = DomainService.list_recurring_commitments(db, current_user)
    return [RecurringCommitmentRead.model_validate(row, from_attributes=True) for row in rows]


@router.get("/recurring-commitments/{commitment_id}", response_model=RecurringCommitmentRead)
def get_recurring_commitment(
    commitment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecurringCommitmentRead:
    row = DomainService.get_recurring_commitment(db, current_user, commitment_id)
    return RecurringCommitmentRead.model_validate(row, from_attributes=True)


@router.patch("/recurring-commitments/{commitment_id}", response_model=RecurringCommitmentRead)
def update_recurring_commitment(
    commitment_id: str,
    payload: RecurringCommitmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecurringCommitmentRead:
    row = DomainService.update_recurring_commitment(db, current_user, commitment_id, payload.model_dump(exclude_unset=True))
    return RecurringCommitmentRead.model_validate(row, from_attributes=True)


@router.delete("/recurring-commitments/{commitment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_commitment(
    commitment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    DomainService.delete_recurring_commitment(db, current_user, commitment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/task-dependencies", response_model=TaskDependencyRead, status_code=status.HTTP_201_CREATED)
def create_task_dependency(
    payload: TaskDependencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskDependencyRead:
    row = DomainService.create_task_dependency(db, current_user, payload.task_id, payload.depends_on_task_id)
    return TaskDependencyRead.model_validate(row, from_attributes=True)


@router.get("/task-dependencies", response_model=list[TaskDependencyRead])
def list_task_dependencies(
    task_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskDependencyRead]:
    rows = DomainService.list_task_dependencies(db, current_user, task_id)
    return [TaskDependencyRead.model_validate(row, from_attributes=True) for row in rows]


@router.delete("/task-dependencies/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_dependency(
    dependency_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    DomainService.delete_task_dependency(db, current_user, dependency_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/history/{entity_type}/{entity_id}", response_model=list[VersionResponse])
def get_entity_history(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[VersionResponse]:
    rows = DomainService.get_entity_history(db, current_user, entity_type, entity_id)
    return [VersionResponse.model_validate(row, from_attributes=True) for row in rows]
