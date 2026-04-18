from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

DeadlineType = Literal["soft", "hard"]
VisibilityScope = Literal["owner", "spouse", "shared"]
Cadence = Literal["daily", "weekly", "monthly"]


class VersionResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    event_type: str
    changed_fields: dict
    created_at: datetime


class AreaBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None


class AreaCreate(AreaBase):
    pass


class AreaUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None


class AreaRead(AreaBase):
    id: str
    owner_user_id: str
    created_at: datetime
    updated_at: datetime


class PrioritizedFields(BaseModel):
    priority: int | None = Field(default=None, ge=0, le=10)
    urgency: int | None = Field(default=None, ge=0, le=10)
    deadline: datetime | None = None
    deadline_type: DeadlineType | None = None
    spouse_priority: int | None = Field(default=None, ge=0, le=10)
    spouse_urgency: int | None = Field(default=None, ge=0, le=10)
    spouse_deadline: datetime | None = None
    spouse_deadline_type: DeadlineType | None = None
    is_private: bool = False
    visibility_scope: VisibilityScope = "shared"

    @model_validator(mode="after")
    def validate_privacy(self) -> "PrioritizedFields":
        if self.is_private and self.visibility_scope != "owner":
            raise ValueError("is_private=true requires visibility_scope='owner'")
        return self


class ProjectBase(PrioritizedFields):
    area_id: str
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    status: str = Field(default="active", min_length=1, max_length=32)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    area_id: str | None = None
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    status: str | None = Field(default=None, min_length=1, max_length=32)
    priority: int | None = Field(default=None, ge=0, le=10)
    urgency: int | None = Field(default=None, ge=0, le=10)
    deadline: datetime | None = None
    deadline_type: DeadlineType | None = None
    spouse_priority: int | None = Field(default=None, ge=0, le=10)
    spouse_urgency: int | None = Field(default=None, ge=0, le=10)
    spouse_deadline: datetime | None = None
    spouse_deadline_type: DeadlineType | None = None
    is_private: bool | None = None
    visibility_scope: VisibilityScope | None = None


class ProjectRead(ProjectBase):
    id: str
    owner_user_id: str
    created_at: datetime
    updated_at: datetime


class TaskBase(PrioritizedFields):
    project_id: str | None = None
    title: str = Field(min_length=1, max_length=200)
    notes: str | None = None
    status: str = Field(default="todo", min_length=1, max_length=32)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    project_id: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    notes: str | None = None
    status: str | None = Field(default=None, min_length=1, max_length=32)
    priority: int | None = Field(default=None, ge=0, le=10)
    urgency: int | None = Field(default=None, ge=0, le=10)
    deadline: datetime | None = None
    deadline_type: DeadlineType | None = None
    spouse_priority: int | None = Field(default=None, ge=0, le=10)
    spouse_urgency: int | None = Field(default=None, ge=0, le=10)
    spouse_deadline: datetime | None = None
    spouse_deadline_type: DeadlineType | None = None
    is_private: bool | None = None
    visibility_scope: VisibilityScope | None = None


class TaskSpouseInfluenceUpdate(BaseModel):
    spouse_priority: int | None = Field(default=None, ge=0, le=10)
    spouse_urgency: int | None = Field(default=None, ge=0, le=10)
    spouse_deadline: datetime | None = None
    spouse_deadline_type: DeadlineType | None = None


class TaskRead(TaskBase):
    id: str
    owner_user_id: str
    created_at: datetime
    updated_at: datetime


class RecurringCommitmentBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    cadence: Cadence
    interval_count: int = Field(default=1, ge=1, le=365)
    duration_minutes: int | None = Field(default=None, ge=5, le=24 * 60)
    energy_weight: float | None = Field(default=None, ge=0, le=10)
    starts_on: datetime
    ends_on: datetime | None = None

    @model_validator(mode="after")
    def validate_range(self) -> "RecurringCommitmentBase":
        if self.ends_on is not None and self.ends_on <= self.starts_on:
            raise ValueError("ends_on must be later than starts_on")
        return self


class RecurringCommitmentCreate(RecurringCommitmentBase):
    pass


class RecurringCommitmentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    cadence: Cadence | None = None
    interval_count: int | None = Field(default=None, ge=1, le=365)
    duration_minutes: int | None = Field(default=None, ge=5, le=24 * 60)
    energy_weight: float | None = Field(default=None, ge=0, le=10)
    starts_on: datetime | None = None
    ends_on: datetime | None = None


class RecurringCommitmentRead(RecurringCommitmentBase):
    id: str
    owner_user_id: str
    created_at: datetime
    updated_at: datetime


class TaskDependencyCreate(BaseModel):
    task_id: str
    depends_on_task_id: str

    @model_validator(mode="after")
    def validate_no_self(self) -> "TaskDependencyCreate":
        if self.task_id == self.depends_on_task_id:
            raise ValueError("task_id and depends_on_task_id cannot match")
        return self


class TaskDependencyRead(BaseModel):
    id: str
    owner_user_id: str
    task_id: str
    depends_on_task_id: str
    created_at: datetime
