from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class UserSettingsResponse(BaseModel):
    reminder_enabled: bool
    reminder_window_start: str
    reminder_window_end: str
    calendar_connected: bool
    calendar_provider: str | None
    notes_connected: bool
    notes_provider: str | None
    ai_planning_enabled: bool
    ai_auto_generate_weekly: bool
    ai_require_manual_approval: bool
    ai_preferred_provider: str | None
    session_note: str | None
    created_at: datetime
    updated_at: datetime


class UserSettingsPatchRequest(BaseModel):
    reminder_enabled: bool | None = None
    reminder_window_start: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    reminder_window_end: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    calendar_connected: bool | None = None
    calendar_provider: str | None = Field(default=None, max_length=64)
    notes_connected: bool | None = None
    notes_provider: str | None = Field(default=None, max_length=64)
    ai_planning_enabled: bool | None = None
    ai_auto_generate_weekly: bool | None = None
    ai_require_manual_approval: bool | None = None
    ai_preferred_provider: str | None = Field(default=None, max_length=64)
    session_note: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_approval_guardrails(self) -> "UserSettingsPatchRequest":
        if self.ai_auto_generate_weekly and self.ai_require_manual_approval is False:
            raise ValueError("ai_auto_generate_weekly requires ai_require_manual_approval=true")
        return self
