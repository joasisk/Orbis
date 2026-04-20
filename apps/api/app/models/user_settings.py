from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    reminder_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    reminder_window_start: Mapped[str] = mapped_column(String(5), nullable=False, default="08:00")
    reminder_window_end: Mapped[str] = mapped_column(String(5), nullable=False, default="20:00")

    calendar_connected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    calendar_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes_connected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)

    ai_planning_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ai_auto_generate_weekly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ai_require_manual_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ai_preferred_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    app_timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")
    weekly_planning_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    weekly_planning_day_of_week: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    weekly_planning_time_local: Mapped[str] = mapped_column(String(5), nullable=False, default="20:00")
    notes_scan_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes_scan_frequency: Mapped[str] = mapped_column(String(16), nullable=False, default="weekly")
    notes_scan_day_of_week: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes_scan_time_local: Mapped[str | None] = mapped_column(String(5), nullable=True)
    reminder_scan_interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    automation_pause_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ui_language: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
    session_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
