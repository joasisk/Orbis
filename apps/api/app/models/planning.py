from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import JSON, CheckConstraint, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class WeeklyPlanProposal(Base):
    __tablename__ = "weekly_plan_proposals"
    __table_args__ = (CheckConstraint("status IN ('proposed','approved','rejected')", name="ck_weekly_plan_proposals_status"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    week_start_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="proposed", index=True)
    provider_key: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt_template_version: Mapped[str] = mapped_column(String(64), nullable=False)
    evaluation_log: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WeeklyPlanItem(Base):
    __tablename__ = "weekly_plan_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    proposal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("weekly_plan_proposals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    suggested_day: Mapped[str] = mapped_column(String(16), nullable=False)
    suggested_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class NoteExtraction(Base):
    __tablename__ = "note_extractions"
    __table_args__ = (CheckConstraint("status IN ('proposed','accepted','dismissed')", name="ck_note_extractions_status"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_title: Mapped[str] = mapped_column(String(200), nullable=False)
    source_ref: Mapped[str | None] = mapped_column(String(400), nullable=True)
    note_content: Mapped[str] = mapped_column(Text, nullable=False)
    provider_key: Mapped[str] = mapped_column(String(64), nullable=False)
    candidate_tasks: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="proposed", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WeeklySchedule(Base):
    __tablename__ = "weekly_schedules"
    __table_args__ = (
        CheckConstraint("status IN ('proposed','accepted','rejected')", name="ck_weekly_schedules_status"),
        UniqueConstraint("owner_user_id", "week_start_date", name="uq_weekly_schedules_owner_week"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="proposed", index=True)
    source_proposal_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("weekly_plan_proposals.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DailySchedule(Base):
    __tablename__ = "daily_schedules"
    __table_args__ = (
        CheckConstraint("status IN ('proposed','accepted','adjusted')", name="ck_daily_schedules_status"),
        CheckConstraint("mood_score IS NULL OR (mood_score >= 1 AND mood_score <= 5)", name="ck_daily_schedules_mood_score"),
        CheckConstraint(
            "morning_energy IS NULL OR (morning_energy >= 0 AND morning_energy <= 1)", name="ck_daily_schedules_morning_energy"
        ),
        CheckConstraint(
            "evening_energy IS NULL OR (evening_energy >= 0 AND evening_energy <= 1)", name="ck_daily_schedules_evening_energy"
        ),
        UniqueConstraint("weekly_schedule_id", "schedule_date", name="uq_daily_schedules_week_day"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    weekly_schedule_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("weekly_schedules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    schedule_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="proposed", index=True)
    mood_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    morning_energy: Mapped[float | None] = mapped_column(Float, nullable=True)
    evening_energy: Mapped[float | None] = mapped_column(Float, nullable=True)
    self_evaluation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class DailyScheduleItem(Base):
    __tablename__ = "daily_schedule_items"
    __table_args__ = (
        CheckConstraint(
            "outcome_status IN ('planned','done','postponed','failed','partial','skipped')",
            name="ck_daily_schedule_items_outcome_status",
        ),
        CheckConstraint("planned_minutes > 0", name="ck_daily_schedule_items_planned_minutes"),
        CheckConstraint("actual_minutes IS NULL OR actual_minutes >= 0", name="ck_daily_schedule_items_actual_minutes"),
        CheckConstraint("distraction_count >= 0", name="ck_daily_schedule_items_distraction_count"),
        CheckConstraint(
            "(outcome_status = 'postponed' AND postponed_to_date IS NOT NULL) OR (outcome_status != 'postponed' AND postponed_to_date IS NULL)",
            name="ck_daily_schedule_items_postponed_date",
        ),
        UniqueConstraint("daily_schedule_id", "order_index", name="uq_daily_schedule_items_day_order"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    daily_schedule_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("daily_schedules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    planned_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    outcome_status: Mapped[str] = mapped_column(String(16), nullable=False, default="planned", index=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    distraction_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    distraction_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    postponed_to_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
