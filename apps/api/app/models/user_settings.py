from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
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
    session_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
