from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class CalendarExternalEvent(Base):
    __tablename__ = "calendar_external_events"
    __table_args__ = (
        UniqueConstraint("owner_user_id", "provider_key", "external_event_id", name="uq_calendar_external_events_provider_event"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_key: Mapped[str] = mapped_column(String(64), nullable=False)
    external_event_id: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class CalendarSoftBlock(Base):
    __tablename__ = "calendar_soft_blocks"
    __table_args__ = (
        CheckConstraint("source_daily_schedule_status = 'accepted'", name="ck_calendar_soft_blocks_accepted_only"),
        UniqueConstraint("daily_schedule_item_id", name="uq_calendar_soft_blocks_day_item"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    daily_schedule_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("daily_schedules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    daily_schedule_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("daily_schedule_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider_key: Mapped[str] = mapped_column(String(64), nullable=False)
    external_block_id: Mapped[str] = mapped_column(String(128), nullable=False)
    block_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source_daily_schedule_status: Mapped[str] = mapped_column(String(16), nullable=False, default="accepted")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
