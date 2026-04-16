from datetime import datetime
from uuid import uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ReminderEvent(Base):
    __tablename__ = "reminder_events"
    __table_args__ = (
        CheckConstraint(
            "delivery_channel IN ('in_app','email','push')",
            name="ck_reminder_events_delivery_channel",
        ),
        CheckConstraint(
            "response_status IN ('pending','acknowledged','snoozed','dismissed')",
            name="ck_reminder_events_response_status",
        ),
        CheckConstraint(
            "(daily_schedule_item_id IS NOT NULL) OR (daily_schedule_id IS NOT NULL)",
            name="ck_reminder_events_schedule_ref_required",
        ),
        CheckConstraint(
            "response_delay_seconds IS NULL OR response_delay_seconds >= 0",
            name="ck_reminder_events_response_delay_non_negative",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    daily_schedule_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("daily_schedules.id", ondelete="CASCADE"), nullable=True, index=True
    )
    daily_schedule_item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("daily_schedule_items.id", ondelete="CASCADE"), nullable=True, index=True
    )
    delivery_channel: Mapped[str] = mapped_column(String(16), nullable=False, default="in_app")
    response_status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    response_delay_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
