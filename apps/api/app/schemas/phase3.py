from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

OverloadRiskLevel = Literal["low", "medium", "high"]
FocusSessionStatus = Literal["active", "completed", "unable"]
BlockerReason = Literal[
    "unclear_requirement",
    "missing_dependency",
    "external_wait",
    "low_energy_focus",
    "time_fragmentation",
    "mental_resistance",
    "context_not_available",
]


class DailyPlanScoreBreakdown(BaseModel):
    deadlines: float = 0
    priority: float = 0
    urgency: float = 0
    energy_fit: float = 0
    dependency_readiness: float = 0
    spouse_influence: float = 0


class DailyPlanRecommendation(BaseModel):
    task_id: str
    title: str
    status: str
    score: float
    reasons: list[str] = Field(default_factory=list)
    score_breakdown: DailyPlanScoreBreakdown


class DailyPlanResponse(BaseModel):
    generated_at: datetime
    recommendations: list[DailyPlanRecommendation]
    primary_recommendation: DailyPlanRecommendation | None = None
    fallback_recommendations: list[DailyPlanRecommendation] = Field(default_factory=list)
    overload_risk_level: OverloadRiskLevel
    drivers: list[str] = Field(default_factory=list)
    recommended_reset_actions: list[str] = Field(default_factory=list)


class FocusStartRequest(BaseModel):
    task_id: str
    pre_task_energy: float = Field(ge=0, le=10)


class FocusStopRequest(BaseModel):
    session_id: str
    post_task_energy: float = Field(ge=0, le=10)


class FocusSidetrackRequest(BaseModel):
    session_id: str
    blocker_reason: BlockerReason
    note: str | None = None


class FocusUnableRequest(BaseModel):
    session_id: str
    unable_reason: str = Field(min_length=3, max_length=500)
    blocker_reason: BlockerReason
    post_task_energy: float = Field(ge=0, le=10)
    note: str | None = None


class FocusSessionResponse(BaseModel):
    id: str
    task_id: str
    status: FocusSessionStatus
    started_at: datetime
    ended_at: datetime | None
    pre_task_energy: float
    post_task_energy: float | None
    sidetrack_count: int
    sidetrack_note: str | None
    unable_reason: str | None


class BlockerEventResponse(BaseModel):
    id: str
    task_id: str
    focus_session_id: str | None
    blocker_reason: BlockerReason
    note: str | None
    created_at: datetime
