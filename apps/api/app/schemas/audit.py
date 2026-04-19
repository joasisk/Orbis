from datetime import datetime

from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    id: str
    actor_user_id: str | None
    event_type: str
    event_metadata: dict
    created_at: datetime
