from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_roles
from app.models.user import User
from app.schemas.reminders import (
    ReminderEventCreateRequest,
    ReminderEventResponse,
    ReminderEventResponsePatchRequest,
    ReminderResponseStatus,
)
from app.services.reminders import ReminderService

router = APIRouter(tags=["reminders"])


@router.get("/reminders/events", response_model=list[ReminderEventResponse])
def list_reminder_events(
    response_status: ReminderResponseStatus | None = Query(default="pending"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> list[ReminderEventResponse]:
    reminders = ReminderService.list_events(db=db, actor=current_user, response_status=response_status)
    return [ReminderEventResponse.model_validate(reminder, from_attributes=True) for reminder in reminders]


@router.post("/reminders/events", response_model=ReminderEventResponse)
def create_reminder_event(
    payload: ReminderEventCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> ReminderEventResponse:
    reminder = ReminderService.create_event(db=db, actor=current_user, payload=payload)
    return ReminderEventResponse.model_validate(reminder, from_attributes=True)


@router.patch("/reminders/events/{reminder_event_id}/response", response_model=ReminderEventResponse)
def patch_reminder_event_response(
    reminder_event_id: str,
    payload: ReminderEventResponsePatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> ReminderEventResponse:
    reminder = ReminderService.patch_response(db=db, actor=current_user, reminder_event_id=reminder_event_id, payload=payload)
    return ReminderEventResponse.model_validate(reminder, from_attributes=True)
