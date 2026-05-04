from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

WeeklyProposalStatus = Literal["proposed", "approved", "rejected"]
WeeklyScheduleStatus = Literal["proposed", "accepted", "rejected"]
DailyScheduleStatus = Literal["proposed", "accepted", "adjusted"]
DailyScheduleItemOutcome = Literal["planned", "done", "postponed", "failed", "partial", "skipped"]
NoteExtractionStatus = Literal["proposed", "accepted", "dismissed"]
NoteExtractionDecision = Literal["accept", "dismiss"]


class WeeklyPlanItemResponse(BaseModel):
    id: str
    task_id: str
    task_title: str | None = None
    suggested_day: str
    suggested_date: date | None = None
    suggested_minutes: int
    rationale: str
    rank: int


class WeeklyPlanProposalResponse(BaseModel):
    id: str
    week_start_date: str
    status: WeeklyProposalStatus
    provider_key: str
    prompt_template_version: str
    created_at: datetime
    approved_at: datetime | None
    evaluation_log: dict
    items: list[WeeklyPlanItemResponse] = Field(default_factory=list)


class WeeklyPlanGenerateRequest(BaseModel):
    week_start_date: str = Field(min_length=10, max_length=10)


class WeeklyPlanApprovalEdit(BaseModel):
    item_id: str
    suggested_day: str | None = Field(default=None, min_length=3, max_length=16)
    suggested_minutes: int | None = Field(default=None, ge=10, le=360)
    rationale: str | None = Field(default=None, min_length=3, max_length=500)


class WeeklyPlanApproveRequest(BaseModel):
    edits: list[WeeklyPlanApprovalEdit] = Field(default_factory=list)


class NoteExtractionPreviewRequest(BaseModel):
    source_title: str = Field(min_length=1, max_length=200)
    source_ref: str | None = Field(default=None, max_length=400)
    note_content: str = Field(min_length=1, max_length=20000)


class NoteTaskCandidateResponse(BaseModel):
    title: str
    notes: str | None = None


class NoteExtractionResponse(BaseModel):
    id: str
    source_title: str
    source_ref: str | None
    status: NoteExtractionStatus
    provider_key: str
    created_at: datetime
    reviewed_at: datetime | None
    candidate_tasks: list[NoteTaskCandidateResponse] = Field(default_factory=list)


class NoteExtractionDecisionRequest(BaseModel):
    decision: NoteExtractionDecision
    selected_indices: list[int] = Field(default_factory=list)


class WeeklyScheduleGenerateRequest(BaseModel):
    week_start_date: date
    source_proposal_id: str | None = None


class DailyScheduleItemResponse(BaseModel):
    id: str
    task_id: str
    planned_minutes: int
    actual_minutes: int | None
    outcome_status: DailyScheduleItemOutcome
    order_index: int
    distraction_count: int
    distraction_notes: str | None
    postponed_to_date: date | None
    failure_reason: str | None


class DailyScheduleResponse(BaseModel):
    id: str
    weekly_schedule_id: str
    schedule_date: date
    status: DailyScheduleStatus
    mood_score: int | None
    morning_energy: float | None
    evening_energy: float | None
    self_evaluation: str | None
    items: list[DailyScheduleItemResponse] = Field(default_factory=list)


class WeeklyScheduleResponse(BaseModel):
    id: str
    week_start_date: date
    status: WeeklyScheduleStatus
    source_proposal_id: str | None
    created_at: datetime
    accepted_at: datetime | None
    days: list[DailyScheduleResponse] = Field(default_factory=list)


class SpouseDashboardItemResponse(BaseModel):
    id: str
    task_id: str
    task_title: str
    planned_minutes: int
    outcome_status: DailyScheduleItemOutcome
    owner_priority: int | None
    owner_urgency: int | None
    spouse_priority: int | None
    spouse_urgency: int | None
    spouse_deadline: datetime | None
    spouse_deadline_type: Literal["soft", "hard"] | None


class SpouseDashboardDayResponse(BaseModel):
    daily_schedule_id: str
    schedule_date: date
    status: DailyScheduleStatus
    visible_items: list[SpouseDashboardItemResponse] = Field(default_factory=list)
    compressed_item_count: int = 0


class SpouseDashboardResponse(BaseModel):
    weekly_schedule_id: str
    week_start_date: date
    accepted_at: datetime | None
    days: list[SpouseDashboardDayResponse] = Field(default_factory=list)


class DailySchedulePatchRequest(BaseModel):
    mood_score: int | None = Field(default=None, ge=1, le=5)
    morning_energy: float | None = Field(default=None, ge=0, le=1)
    evening_energy: float | None = Field(default=None, ge=0, le=1)
    self_evaluation: str | None = Field(default=None, max_length=2000)


class DailyScheduleItemPatchRequest(BaseModel):
    outcome_status: DailyScheduleItemOutcome | None = None
    actual_minutes: int | None = Field(default=None, ge=0)
    distraction_count: int | None = Field(default=None, ge=0)
    distraction_notes: str | None = Field(default=None, max_length=2000)
    postponed_to_date: date | None = None
    failure_reason: str | None = Field(default=None, max_length=2000)


class DailyScheduleItemFocusStartRequest(BaseModel):
    pre_task_energy: float = Field(ge=0, le=10)


class DailyScheduleItemFocusEndRequest(BaseModel):
    post_task_energy: float = Field(ge=0, le=10)
