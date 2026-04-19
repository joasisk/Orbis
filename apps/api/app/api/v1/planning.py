from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_roles
from app.models.user import User
from app.schemas.planning import (
    DailyScheduleItemFocusEndRequest,
    DailyScheduleItemFocusStartRequest,
    DailyScheduleItemPatchRequest,
    DailySchedulePatchRequest,
    DailyScheduleResponse,
    NoteExtractionDecisionRequest,
    NoteExtractionPreviewRequest,
    NoteExtractionResponse,
    SpouseDashboardResponse,
    WeeklyPlanApproveRequest,
    WeeklyPlanGenerateRequest,
    WeeklyPlanProposalResponse,
    WeeklyScheduleGenerateRequest,
    WeeklyScheduleResponse,
)
from app.services.planning import PlanningService, default_week_start

router = APIRouter(tags=["planning"])


@router.post("/planning/weekly-proposals/generate", response_model=WeeklyPlanProposalResponse)
def generate_weekly_proposal(
    payload: WeeklyPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> WeeklyPlanProposalResponse:
    return PlanningService.generate_weekly_proposal(db=db, actor=current_user, payload=payload)


@router.post("/planning/weekly-proposals/generate-default", response_model=WeeklyPlanProposalResponse)
def generate_weekly_proposal_default(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> WeeklyPlanProposalResponse:
    return PlanningService.generate_weekly_proposal(
        db=db,
        actor=current_user,
        payload=WeeklyPlanGenerateRequest(week_start_date=default_week_start()),
    )


@router.get("/planning/weekly-proposals/latest", response_model=WeeklyPlanProposalResponse)
def get_latest_weekly_proposal(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> WeeklyPlanProposalResponse:
    return PlanningService.get_latest_weekly_proposal(db=db, actor=current_user)


@router.post("/planning/weekly-proposals/{proposal_id}/approve", response_model=WeeklyPlanProposalResponse)
def approve_weekly_proposal(
    proposal_id: str,
    payload: WeeklyPlanApproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> WeeklyPlanProposalResponse:
    return PlanningService.approve_weekly_proposal(db=db, actor=current_user, proposal_id=proposal_id, payload=payload)


@router.post("/planning/note-extractions/preview", response_model=NoteExtractionResponse)
def preview_note_extraction(
    payload: NoteExtractionPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> NoteExtractionResponse:
    return PlanningService.preview_note_extraction(
        db=db,
        actor=current_user,
        source_title=payload.source_title,
        source_ref=payload.source_ref,
        note_content=payload.note_content,
    )


@router.post("/planning/note-extractions/{extraction_id}/decision", response_model=NoteExtractionResponse)
def decide_note_extraction(
    extraction_id: str,
    payload: NoteExtractionDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> NoteExtractionResponse:
    return PlanningService.decide_note_extraction(db=db, actor=current_user, extraction_id=extraction_id, payload=payload)


@router.post("/schedules/weeks/generate", response_model=WeeklyScheduleResponse)
def generate_weekly_schedule(
    payload: WeeklyScheduleGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> WeeklyScheduleResponse:
    return PlanningService.generate_weekly_schedule(db=db, actor=current_user, payload=payload)


@router.get("/schedules/weeks/{week_start_date}", response_model=WeeklyScheduleResponse)
def get_weekly_schedule(
    week_start_date: date, db: Session = Depends(get_db), current_user: User = Depends(require_roles("owner"))
) -> WeeklyScheduleResponse:
    return PlanningService.get_weekly_schedule_by_date(db=db, actor=current_user, week_start_date=week_start_date)


@router.post("/schedules/weeks/{weekly_schedule_id}/accept", response_model=WeeklyScheduleResponse)
def accept_weekly_schedule(
    weekly_schedule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> WeeklyScheduleResponse:
    return PlanningService.accept_weekly_schedule(db=db, actor=current_user, weekly_schedule_id=weekly_schedule_id)


@router.post("/schedules/weeks/{weekly_schedule_id}/reject", response_model=WeeklyScheduleResponse)
def reject_weekly_schedule(
    weekly_schedule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> WeeklyScheduleResponse:
    return PlanningService.reject_weekly_schedule(db=db, actor=current_user, weekly_schedule_id=weekly_schedule_id)


@router.get("/schedules/days/{schedule_date}", response_model=DailyScheduleResponse)
def get_daily_schedule(
    schedule_date: date, db: Session = Depends(get_db), current_user: User = Depends(require_roles("owner"))
) -> DailyScheduleResponse:
    return PlanningService.get_daily_schedule_by_date(db=db, actor=current_user, schedule_date=schedule_date)


@router.get("/schedules/spouse-dashboard", response_model=SpouseDashboardResponse)
def get_spouse_dashboard(
    week_start_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("spouse")),
) -> SpouseDashboardResponse:
    return PlanningService.spouse_dashboard_by_week(db=db, actor=current_user, week_start_date=week_start_date)


@router.post("/schedules/days/{daily_schedule_id}/accept", response_model=DailyScheduleResponse)
def accept_daily_schedule(
    daily_schedule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> DailyScheduleResponse:
    return PlanningService.accept_daily_schedule(db=db, actor=current_user, daily_schedule_id=daily_schedule_id)


@router.patch("/schedules/days/{daily_schedule_id}", response_model=DailyScheduleResponse)
def patch_daily_schedule(
    daily_schedule_id: str,
    payload: DailySchedulePatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> DailyScheduleResponse:
    return PlanningService.patch_daily_schedule(db=db, actor=current_user, daily_schedule_id=daily_schedule_id, payload=payload)


@router.patch("/schedules/day-items/{daily_schedule_item_id}", response_model=DailyScheduleResponse)
def patch_daily_schedule_item(
    daily_schedule_item_id: str,
    payload: DailyScheduleItemPatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> DailyScheduleResponse:
    return PlanningService.patch_daily_schedule_item(
        db=db, actor=current_user, daily_schedule_item_id=daily_schedule_item_id, payload=payload
    )


@router.post("/schedules/day-items/{daily_schedule_item_id}/start-focus", response_model=DailyScheduleResponse)
def start_day_item_focus(
    daily_schedule_item_id: str,
    payload: DailyScheduleItemFocusStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> DailyScheduleResponse:
    return PlanningService.start_day_item_focus(db=db, actor=current_user, daily_schedule_item_id=daily_schedule_item_id, payload=payload)


@router.post("/schedules/day-items/{daily_schedule_item_id}/end-focus", response_model=DailyScheduleResponse)
def end_day_item_focus(
    daily_schedule_item_id: str,
    payload: DailyScheduleItemFocusEndRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> DailyScheduleResponse:
    return PlanningService.end_day_item_focus(db=db, actor=current_user, daily_schedule_item_id=daily_schedule_item_id, payload=payload)
