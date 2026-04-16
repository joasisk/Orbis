from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.planning import DailySchedule, DailyScheduleItem
from app.models.reminder import ReminderEvent
from app.models.user import User
from app.schemas.reminders import ReminderEventCreateRequest, ReminderEventResponsePatchRequest


class ReminderService:
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
        db.commit()
        db.refresh(event)
        return event
