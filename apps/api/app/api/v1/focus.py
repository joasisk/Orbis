from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.focus import (
    BlockerEventResponse,
    DailyPlanResponse,
    FocusSessionResponse,
    FocusSidetrackRequest,
    FocusStartRequest,
    FocusStopRequest,
    FocusUnableRequest,
)
from app.services.focus import FocusService

router = APIRouter(tags=["focus"])


@router.get("/planning/daily-plan", response_model=DailyPlanResponse)
def get_daily_plan(
    limit: int = Query(default=5, ge=1, le=20),
    current_energy: float | None = Query(default=None, ge=0, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DailyPlanResponse:
    return FocusService.get_daily_plan(db=db, actor=current_user, limit=limit, current_energy=current_energy)


@router.post("/focus/start", response_model=FocusSessionResponse)
def start_focus_session(
    payload: FocusStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FocusSessionResponse:
    session = FocusService.start_focus_session(db, current_user, payload.task_id, payload.pre_task_energy)
    return FocusSessionResponse.model_validate(session, from_attributes=True)


@router.post("/focus/stop", response_model=FocusSessionResponse)
def stop_focus_session(
    payload: FocusStopRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FocusSessionResponse:
    session = FocusService.stop_focus_session(db, current_user, payload.session_id, payload.post_task_energy)
    return FocusSessionResponse.model_validate(session, from_attributes=True)


@router.post("/focus/sidetrack", response_model=BlockerEventResponse)
def sidetrack_focus_session(
    payload: FocusSidetrackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BlockerEventResponse:
    _, event = FocusService.sidetrack_focus_session(
        db,
        current_user,
        payload.session_id,
        payload.blocker_reason,
        payload.note,
    )
    return BlockerEventResponse.model_validate(event, from_attributes=True)


@router.post("/focus/unable", response_model=BlockerEventResponse)
def unable_focus_session(
    payload: FocusUnableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BlockerEventResponse:
    _, event = FocusService.unable_focus_session(
        db,
        current_user,
        payload.session_id,
        payload.unable_reason,
        payload.blocker_reason,
        payload.post_task_energy,
        payload.note,
    )
    return BlockerEventResponse.model_validate(event, from_attributes=True)
