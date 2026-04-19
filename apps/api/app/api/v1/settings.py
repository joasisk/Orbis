from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_roles
from app.models.user import User
from app.schemas.audit import AuditEventResponse
from app.schemas.user_settings import UserSettingsPatchRequest, UserSettingsResponse
from app.services.audit import AuditService
from app.services.user_settings import UserSettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/me", response_model=UserSettingsResponse)
def get_my_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner", "spouse")),
) -> UserSettingsResponse:
    settings = UserSettingsService.get_or_create(db=db, actor=current_user)
    return UserSettingsResponse.model_validate(settings, from_attributes=True)


@router.patch("/me", response_model=UserSettingsResponse)
def patch_my_settings(
    payload: UserSettingsPatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner", "spouse")),
) -> UserSettingsResponse:
    settings = UserSettingsService.patch(db=db, actor=current_user, payload=payload.model_dump(exclude_unset=True))
    return UserSettingsResponse.model_validate(settings, from_attributes=True)


@router.get("/audit-events", response_model=list[AuditEventResponse])
def get_audit_events(
    limit: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> list[AuditEventResponse]:
    events = AuditService.list_events(db=db, limit=limit)
    return [AuditEventResponse.model_validate(event, from_attributes=True) for event in events]
