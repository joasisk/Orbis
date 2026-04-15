from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_roles
from app.models.user import User
from app.schemas.phase4 import (
    NoteExtractionDecisionRequest,
    NoteExtractionPreviewRequest,
    NoteExtractionResponse,
    WeeklyPlanApproveRequest,
    WeeklyPlanGenerateRequest,
    WeeklyPlanProposalResponse,
)
from app.services.phase4 import Phase4Service, default_week_start

router = APIRouter(tags=["phase4"])


@router.post("/planning/weekly-proposals/generate", response_model=WeeklyPlanProposalResponse)
def generate_weekly_proposal(
    payload: WeeklyPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> WeeklyPlanProposalResponse:
    return Phase4Service.generate_weekly_proposal(db=db, actor=current_user, payload=payload)


@router.post("/planning/weekly-proposals/generate-default", response_model=WeeklyPlanProposalResponse)
def generate_weekly_proposal_default(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> WeeklyPlanProposalResponse:
    return Phase4Service.generate_weekly_proposal(
        db=db,
        actor=current_user,
        payload=WeeklyPlanGenerateRequest(week_start_date=default_week_start()),
    )


@router.get("/planning/weekly-proposals/latest", response_model=WeeklyPlanProposalResponse)
def get_latest_weekly_proposal(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> WeeklyPlanProposalResponse:
    return Phase4Service.get_latest_weekly_proposal(db=db, actor=current_user)


@router.post("/planning/weekly-proposals/{proposal_id}/approve", response_model=WeeklyPlanProposalResponse)
def approve_weekly_proposal(
    proposal_id: str,
    payload: WeeklyPlanApproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> WeeklyPlanProposalResponse:
    return Phase4Service.approve_weekly_proposal(db=db, actor=current_user, proposal_id=proposal_id, payload=payload)


@router.post("/planning/note-extractions/preview", response_model=NoteExtractionResponse)
def preview_note_extraction(
    payload: NoteExtractionPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner")),
) -> NoteExtractionResponse:
    return Phase4Service.preview_note_extraction(
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
    return Phase4Service.decide_note_extraction(db=db, actor=current_user, extraction_id=extraction_id, payload=payload)
