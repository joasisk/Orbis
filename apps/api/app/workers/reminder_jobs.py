from datetime import UTC, datetime

from sqlalchemy import select

from app.core.db import SessionLocal
from app.models.user import User
from app.services.reminders import ReminderService


def run_due_reminder_scan(now: datetime | None = None) -> int:
    reference_time = now or datetime.now(UTC)
    total = 0
    with SessionLocal() as db:
        owners = list(db.scalars(select(User).where(User.role == "owner")).all())
        for owner in owners:
            created = ReminderService.schedule_due_events(db=db, actor=owner, now=reference_time)
            total += len(created)
    return total
