from datetime import datetime

from pydantic import BaseModel, Field

from app.models.user import UserRole


class UserMeResponse(BaseModel):
    id: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime


class SpouseStatusResponse(BaseModel):
    spouse: UserMeResponse | None


class CreateSpouseRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)
