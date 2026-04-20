from datetime import datetime
from typing import Literal
from zoneinfo import available_timezones

from pydantic import BaseModel, Field, model_validator

UiLanguage = Literal["en", "sk", "de", "it", "es", "pl"]
NotesScanFrequency = Literal["daily", "weekly"]


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
    app_timezone: str
    weekly_planning_enabled: bool
    weekly_planning_day_of_week: int
    weekly_planning_time_local: str
    notes_scan_enabled: bool
    notes_scan_frequency: NotesScanFrequency
    notes_scan_day_of_week: int | None
    notes_scan_time_local: str | None
    reminder_scan_interval_minutes: int
    automation_pause_until: datetime | None
    ui_language: UiLanguage
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
    app_timezone: str | None = Field(default=None, max_length=64)
    weekly_planning_enabled: bool | None = None
    weekly_planning_day_of_week: int | None = Field(default=None, ge=0, le=6)
    weekly_planning_time_local: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    notes_scan_enabled: bool | None = None
    notes_scan_frequency: NotesScanFrequency | None = None
    notes_scan_day_of_week: int | None = Field(default=None, ge=0, le=6)
    notes_scan_time_local: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    reminder_scan_interval_minutes: int | None = Field(default=None, ge=5, le=240)
    automation_pause_until: datetime | None = None
    ui_language: UiLanguage | None = None
    session_note: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_approval_guardrails(self) -> "UserSettingsPatchRequest":
        if self.ai_auto_generate_weekly and self.ai_require_manual_approval is False:
            raise ValueError("ai_auto_generate_weekly requires ai_require_manual_approval=true")
        if self.app_timezone is not None and self.app_timezone not in available_timezones():
            raise ValueError("app_timezone must be a valid IANA timezone")
        if self.notes_scan_frequency == "daily" and self.notes_scan_day_of_week is not None:
            raise ValueError("notes_scan_day_of_week must be null when notes_scan_frequency=daily")
        if self.notes_scan_frequency == "weekly" and self.notes_scan_enabled and self.notes_scan_day_of_week is None:
            raise ValueError("notes_scan_day_of_week is required when weekly notes scan is enabled")
        return self
