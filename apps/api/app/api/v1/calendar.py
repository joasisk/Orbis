from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_roles
from app.models.user import User
from app.schemas.calendar import CalendarImportRequest, CalendarImportResponse, CalendarSoftBlockExportResponse
from app.services.calendar import CalendarService

router = APIRouter(tags=["calendar"])


@router.post("/calendar/events/import", response_model=CalendarImportResponse)
def import_calendar_events(
    payload: CalendarImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> CalendarImportResponse:
    return CalendarService.import_external_events(
        db=db,
        actor=current_user,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )


@router.post("/calendar/daily-schedules/{daily_schedule_id}/soft-blocks/export", response_model=CalendarSoftBlockExportResponse)
def export_daily_schedule_soft_blocks(
    daily_schedule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> CalendarSoftBlockExportResponse:
    return CalendarService.export_daily_schedule_soft_blocks(db=db, actor=current_user, daily_schedule_id=daily_schedule_id)
