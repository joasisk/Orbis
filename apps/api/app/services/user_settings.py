from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_settings import UserSettings


class UserSettingsService:
    @staticmethod
    def get_or_create(db: Session, actor: User) -> UserSettings:
        existing = db.execute(select(UserSettings).where(UserSettings.owner_user_id == actor.id)).scalar_one_or_none()
        if existing is not None:
            return existing

        settings = UserSettings(owner_user_id=actor.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
        return settings

    @staticmethod
    def patch(db: Session, actor: User, payload: dict) -> UserSettings:
        settings = UserSettingsService.get_or_create(db, actor)

        if payload.get("ai_auto_generate_weekly") is True and payload.get("ai_require_manual_approval") is False:
            raise HTTPException(status_code=422, detail="ai_auto_generate_weekly requires ai_require_manual_approval=true")

        for key, value in payload.items():
            setattr(settings, key, value)

        if settings.ai_auto_generate_weekly and not settings.ai_require_manual_approval:
            raise HTTPException(status_code=422, detail="Approval-first guardrail cannot be disabled")
        if settings.notes_scan_enabled and settings.notes_scan_frequency == "weekly" and settings.notes_scan_day_of_week is None:
            raise HTTPException(status_code=422, detail="notes_scan_day_of_week is required for weekly notes scan")
        if settings.notes_scan_frequency == "daily":
            settings.notes_scan_day_of_week = None

        db.add(settings)
        db.commit()
        db.refresh(settings)
        return settings
