from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.phase3 import DailyPlanResponse
from app.services.phase3 import Phase3Service

router = APIRouter(prefix="/planning", tags=["phase3"])


@router.get("/daily-plan", response_model=DailyPlanResponse)
def get_daily_plan(
    limit: int = Query(default=5, ge=1, le=20),
    current_energy: float | None = Query(default=None, ge=0, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DailyPlanResponse:
    return Phase3Service.get_daily_plan(db=db, actor=current_user, limit=limit, current_energy=current_energy)
