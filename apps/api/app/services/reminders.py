from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.models.planning import DailySchedule, DailyScheduleItem
from app.models.reminder import ReminderEvent
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.reminders import ReminderEventCreateRequest, ReminderEventResponsePatchRequest


class ReminderService:
    @staticmethod
    def _record_audit_event(
        db: Session,
        *,
        actor_user_id: str | None,
        event_type: str,
        metadata: dict,
    ) -> None:
        db.add(
            AuditEvent(
                actor_user_id=actor_user_id,
                event_type=event_type,
                event_metadata=metadata,
            )
        )

    @staticmethod
    def list_events(db: Session, actor: User, response_status: str | None = "pending") -> list[ReminderEvent]:
        stmt = select(ReminderEvent).where(ReminderEvent.owner_user_id == actor.id)
        if response_status is not None:
            stmt = stmt.where(ReminderEvent.response_status == response_status)
        return list(db.scalars(stmt.order_by(ReminderEvent.sent_at.desc())))

    @staticmethod
    def create_event(db: Session, actor: User, payload: ReminderEventCreateRequest) -> ReminderEvent:
        if payload.daily_schedule_id is None and payload.daily_schedule_item_id is None:
            raise HTTPException(status_code=422, detail="daily_schedule_id or daily_schedule_item_id is required")

        if payload.daily_schedule_id is not None:
            schedule = db.scalar(select(DailySchedule).where(DailySchedule.id == payload.daily_schedule_id))
            if schedule is None:
                raise HTTPException(status_code=404, detail="Daily schedule not found")
            if schedule.owner_user_id != actor.id:
                raise HTTPException(status_code=403, detail="Forbidden")

        if payload.daily_schedule_item_id is not None:
            item = db.scalar(select(DailyScheduleItem).where(DailyScheduleItem.id == payload.daily_schedule_item_id))
            if item is None:
                raise HTTPException(status_code=404, detail="Daily schedule item not found")
            if item.owner_user_id != actor.id:
                raise HTTPException(status_code=403, detail="Forbidden")

        event = ReminderEvent(
            owner_user_id=actor.id,
            daily_schedule_id=payload.daily_schedule_id,
            daily_schedule_item_id=payload.daily_schedule_item_id,
            delivery_channel=payload.delivery_channel,
            response_status="pending",
        )
        db.add(event)
        ReminderService._record_audit_event(
            db,
            actor_user_id=actor.id,
            event_type="reminder.event_created",
            metadata={
                "owner_user_id": actor.id,
                "daily_schedule_id": payload.daily_schedule_id,
                "daily_schedule_item_id": payload.daily_schedule_item_id,
                "delivery_channel": payload.delivery_channel,
            },
        )
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def patch_response(
        db: Session,
        actor: User,
        reminder_event_id: str,
        payload: ReminderEventResponsePatchRequest,
    ) -> ReminderEvent:
        event = db.scalar(select(ReminderEvent).where(ReminderEvent.id == reminder_event_id))
        if event is None:
            raise HTTPException(status_code=404, detail="Reminder event not found")
        if event.owner_user_id != actor.id:
            raise HTTPException(status_code=403, detail="Forbidden")

        event.response_status = payload.response_status
        event.responded_at = datetime.utcnow()
        event.response_delay_seconds = max(0, int((event.responded_at - event.sent_at).total_seconds()))
        ReminderService._record_audit_event(
            db,
            actor_user_id=actor.id,
            event_type="reminder.response_recorded",
            metadata={
                "owner_user_id": actor.id,
                "reminder_event_id": event.id,
                "daily_schedule_id": event.daily_schedule_id,
                "daily_schedule_item_id": event.daily_schedule_item_id,
                "response_status": payload.response_status,
                "response_delay_seconds": event.response_delay_seconds,
            },
        )
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def schedule_due_events(db: Session, actor: User, now: datetime | None = None) -> list[ReminderEvent]:
        current = now or datetime.now(UTC)
        settings = db.scalar(select(UserSettings).where(UserSettings.owner_user_id == actor.id))
        if settings is None or not settings.reminder_enabled:
            return []

        window_start_hour = int(settings.reminder_window_start.split(":")[0])
        window_end_hour = int(settings.reminder_window_end.split(":")[0])
        if current.hour < window_start_hour or current.hour >= window_end_hour:
            return []

        avg_delay_seconds = db.scalar(
            select(func.avg(ReminderEvent.response_delay_seconds)).where(
                ReminderEvent.owner_user_id == actor.id,
                ReminderEvent.response_delay_seconds.is_not(None),
            )
        )
        adaptive_throttle = 90 if avg_delay_seconds is None else max(30, min(180, int(avg_delay_seconds // 60)))
        configured_interval = max(5, min(240, settings.reminder_scan_interval_minutes))
        throttle_minutes = max(configured_interval, adaptive_throttle)

        pending_items = list(
            db.scalars(
                select(DailyScheduleItem)
                .join(DailySchedule, DailySchedule.id == DailyScheduleItem.daily_schedule_id)
                .where(
                    DailySchedule.owner_user_id == actor.id,
                    DailySchedule.status.in_(["accepted", "adjusted"]),
                    DailyScheduleItem.outcome_status == "planned",
                    DailySchedule.schedule_date <= current.date(),
                )
                .order_by(DailySchedule.schedule_date.asc(), DailyScheduleItem.order_index.asc())
            ).all()
        )

        created: list[ReminderEvent] = []
        for item in pending_items:
            recent_event = db.scalar(
                select(ReminderEvent)
                .where(
                    and_(
                        ReminderEvent.owner_user_id == actor.id,
                        ReminderEvent.daily_schedule_item_id == item.id,
                        ReminderEvent.sent_at >= current - timedelta(minutes=throttle_minutes),
                    )
                )
                .order_by(ReminderEvent.sent_at.desc())
            )
            if recent_event is not None:
                continue
            event = ReminderEvent(
                owner_user_id=actor.id,
                daily_schedule_id=item.daily_schedule_id,
                daily_schedule_item_id=item.id,
                delivery_channel="in_app",
                response_status="pending",
            )
            db.add(event)
            created.append(event)
            ReminderService._record_audit_event(
                db,
                actor_user_id=actor.id,
                event_type="reminder.delivered",
                metadata={
                    "owner_user_id": actor.id,
                    "daily_schedule_id": item.daily_schedule_id,
                    "daily_schedule_item_id": item.id,
                    "delivery_channel": "in_app",
                    "scheduled_scan_time": current.isoformat(),
                },
            )

        if created:
            db.commit()
            for event in created:
                db.refresh(event)
        return created
