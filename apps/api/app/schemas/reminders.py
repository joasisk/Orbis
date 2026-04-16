from datetime import datetime
from typing import Literal

from pydantic import BaseModel

ReminderDeliveryChannel = Literal["in_app", "email", "push"]
ReminderResponseStatus = Literal["pending", "acknowledged", "snoozed", "dismissed"]


class ReminderEventCreateRequest(BaseModel):
    daily_schedule_id: str | None = None
    daily_schedule_item_id: str | None = None
    delivery_channel: ReminderDeliveryChannel = "in_app"


class ReminderEventResponsePatchRequest(BaseModel):
    response_status: Literal["acknowledged", "snoozed", "dismissed"]


class ReminderEventResponse(BaseModel):
    id: str
    daily_schedule_id: str | None
    daily_schedule_item_id: str | None
    delivery_channel: ReminderDeliveryChannel
    response_status: ReminderResponseStatus
    sent_at: datetime
    responded_at: datetime | None
    response_delay_seconds: int | None
