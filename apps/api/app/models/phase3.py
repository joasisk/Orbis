from datetime import datetime
from uuid import uuid4

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class FocusSession(Base):
    __tablename__ = "focus_sessions"
    __table_args__ = (CheckConstraint("status IN ('active','completed','unable')", name="ck_focus_sessions_status"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active", index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pre_task_energy: Mapped[float] = mapped_column(Float, nullable=False)
    post_task_energy: Mapped[float | None] = mapped_column(Float, nullable=True)
    sidetrack_count: Mapped[int] = mapped_column(nullable=False, default=0)
    sidetrack_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    unable_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class BlockerEvent(Base):
    __tablename__ = "blocker_events"
    __table_args__ = (
        CheckConstraint(
            "blocker_reason IN ('unclear_requirement','missing_dependency','external_wait','low_energy_focus','time_fragmentation','mental_resistance','context_not_available')",
            name="ck_blocker_events_reason",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    focus_session_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("focus_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    blocker_reason: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
