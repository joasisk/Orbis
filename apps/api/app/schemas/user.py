from datetime import datetime

from pydantic import BaseModel


class UserMeResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
