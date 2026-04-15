from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

WeeklyProposalStatus = Literal["proposed", "approved", "rejected"]
NoteExtractionStatus = Literal["proposed", "accepted", "dismissed"]
NoteExtractionDecision = Literal["accept", "dismiss"]


class WeeklyPlanItemResponse(BaseModel):
    id: str
    task_id: str
    suggested_day: str
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
