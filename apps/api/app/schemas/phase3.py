from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

OverloadRiskLevel = Literal["low", "medium", "high"]


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
    overload_risk_level: OverloadRiskLevel
    drivers: list[str] = Field(default_factory=list)
    recommended_reset_actions: list[str] = Field(default_factory=list)
