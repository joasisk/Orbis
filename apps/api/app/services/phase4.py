from datetime import UTC, date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.phase2 import Task
from app.models.phase4 import NoteExtraction, WeeklyPlanItem, WeeklyPlanProposal
from app.models.user import User
from app.schemas.phase4 import (
    NoteExtractionDecisionRequest,
    NoteExtractionResponse,
    NoteTaskCandidateResponse,
    WeeklyPlanApproveRequest,
    WeeklyPlanGenerateRequest,
    WeeklyPlanItemResponse,
    WeeklyPlanProposalResponse,
)
from app.services.ai import PROMPT_TEMPLATE_VERSION, get_default_provider

TERMINAL_TASK_STATUSES = {"done", "completed", "cancelled", "archived"}


class Phase4Service:
    @staticmethod
    def generate_weekly_proposal(db: Session, actor: User, payload: WeeklyPlanGenerateRequest) -> WeeklyPlanProposalResponse:
        provider = get_default_provider()

        tasks = list(
            db.scalars(
                select(Task).where(
                    Task.owner_user_id == actor.id,
                )
            ).all()
        )
        candidates = [task for task in tasks if task.status.lower() not in TERMINAL_TASK_STATUSES]
        suggestions = provider.generate_weekly_plan(candidates)

        proposal = WeeklyPlanProposal(
            owner_user_id=actor.id,
            week_start_date=payload.week_start_date,
            status="proposed",
            provider_key=provider.provider_key,
            prompt_template_version=PROMPT_TEMPLATE_VERSION,
            evaluation_log={
                "candidate_task_count": len(candidates),
                "proposed_item_count": len(suggestions),
                "generated_at": datetime.now(UTC).isoformat(),
            },
        )
        db.add(proposal)
        db.flush()

        items: list[WeeklyPlanItem] = []
        for rank, suggestion in enumerate(suggestions, start=1):
            item = WeeklyPlanItem(
                proposal_id=proposal.id,
                owner_user_id=actor.id,
                task_id=suggestion.task_id,
                suggested_day=suggestion.suggested_day,
                suggested_minutes=suggestion.suggested_minutes,
                rationale=suggestion.rationale,
                rank=rank,
            )
            db.add(item)
            items.append(item)

        db.commit()
        db.refresh(proposal)
        for item in items:
            db.refresh(item)

        return Phase4Service._proposal_response(proposal, items)

    @staticmethod
    def get_latest_weekly_proposal(db: Session, actor: User) -> WeeklyPlanProposalResponse:
        proposal = db.scalar(
            select(WeeklyPlanProposal)
            .where(WeeklyPlanProposal.owner_user_id == actor.id)
            .order_by(WeeklyPlanProposal.created_at.desc())
            .limit(1)
        )
        if proposal is None:
            raise HTTPException(status_code=404, detail="No weekly proposal found")

        items = list(
            db.scalars(
                select(WeeklyPlanItem)
                .where(WeeklyPlanItem.proposal_id == proposal.id)
                .order_by(WeeklyPlanItem.rank.asc(), WeeklyPlanItem.created_at.asc())
            ).all()
        )
        return Phase4Service._proposal_response(proposal, items)

    @staticmethod
    def approve_weekly_proposal(
        db: Session,
        actor: User,
        proposal_id: str,
        payload: WeeklyPlanApproveRequest,
    ) -> WeeklyPlanProposalResponse:
        proposal = db.scalar(select(WeeklyPlanProposal).where(WeeklyPlanProposal.id == proposal_id))
        if proposal is None:
            raise HTTPException(status_code=404, detail="Weekly proposal not found")
        if proposal.owner_user_id != actor.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        if proposal.status != "proposed":
            raise HTTPException(status_code=409, detail="Proposal is no longer pending approval")

        items = list(db.scalars(select(WeeklyPlanItem).where(WeeklyPlanItem.proposal_id == proposal.id)).all())
        item_lookup = {item.id: item for item in items}

        for edit in payload.edits:
            item = item_lookup.get(edit.item_id)
            if item is None:
                raise HTTPException(status_code=404, detail=f"Proposal item not found: {edit.item_id}")
            if edit.suggested_day is not None:
                item.suggested_day = edit.suggested_day
            if edit.suggested_minutes is not None:
                item.suggested_minutes = edit.suggested_minutes
            if edit.rationale is not None:
                item.rationale = edit.rationale

        proposal.status = "approved"
        proposal.approved_at = datetime.now(UTC)
        db.commit()
        db.refresh(proposal)
        for item in items:
            db.refresh(item)

        return Phase4Service._proposal_response(proposal, items)

    @staticmethod
    def preview_note_extraction(
        db: Session,
        actor: User,
        source_title: str,
        source_ref: str | None,
        note_content: str,
    ) -> NoteExtractionResponse:
        provider = get_default_provider()
        candidates = provider.extract_task_candidates(note_content)
        extraction = NoteExtraction(
            owner_user_id=actor.id,
            source_title=source_title,
            source_ref=source_ref,
            note_content=note_content,
            provider_key=provider.provider_key,
            candidate_tasks=[{"title": candidate.title, "notes": candidate.notes} for candidate in candidates],
            status="proposed",
        )
        db.add(extraction)
        db.commit()
        db.refresh(extraction)
        return Phase4Service._extraction_response(extraction)

    @staticmethod
    def decide_note_extraction(
        db: Session,
        actor: User,
        extraction_id: str,
        payload: NoteExtractionDecisionRequest,
    ) -> NoteExtractionResponse:
        extraction = db.scalar(select(NoteExtraction).where(NoteExtraction.id == extraction_id))
        if extraction is None:
            raise HTTPException(status_code=404, detail="Note extraction not found")
        if extraction.owner_user_id != actor.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        if extraction.status != "proposed":
            return Phase4Service._extraction_response(extraction)

        if payload.decision == "dismiss":
            extraction.status = "dismissed"
            extraction.reviewed_at = datetime.now(UTC)
            db.commit()
            db.refresh(extraction)
            return Phase4Service._extraction_response(extraction)

        for index in payload.selected_indices:
            if index < 0 or index >= len(extraction.candidate_tasks):
                raise HTTPException(status_code=422, detail=f"selected index out of range: {index}")
            candidate = extraction.candidate_tasks[index]
            task = Task(
                owner_user_id=actor.id,
                project_id=None,
                title=str(candidate["title"]),
                notes=candidate.get("notes"),
                status="todo",
                is_private=False,
                visibility_scope="shared",
            )
            db.add(task)

        extraction.status = "accepted"
        extraction.reviewed_at = datetime.now(UTC)
        extraction.candidate_tasks = [
            {**candidate, "selected": idx in payload.selected_indices} for idx, candidate in enumerate(extraction.candidate_tasks)
        ]
        db.commit()
        db.refresh(extraction)
        return Phase4Service._extraction_response(extraction)

    @staticmethod
    def _proposal_response(proposal: WeeklyPlanProposal, items: list[WeeklyPlanItem]) -> WeeklyPlanProposalResponse:
        return WeeklyPlanProposalResponse(
            id=proposal.id,
            week_start_date=proposal.week_start_date,
            status=proposal.status,
            provider_key=proposal.provider_key,
            prompt_template_version=proposal.prompt_template_version,
            created_at=proposal.created_at,
            approved_at=proposal.approved_at,
            evaluation_log=proposal.evaluation_log,
            items=[
                WeeklyPlanItemResponse(
                    id=item.id,
                    task_id=item.task_id,
                    suggested_day=item.suggested_day,
                    suggested_minutes=item.suggested_minutes,
                    rationale=item.rationale,
                    rank=item.rank,
                )
                for item in items
            ],
        )

    @staticmethod
    def _extraction_response(extraction: NoteExtraction) -> NoteExtractionResponse:
        return NoteExtractionResponse(
            id=extraction.id,
            source_title=extraction.source_title,
            source_ref=extraction.source_ref,
            status=extraction.status,
            provider_key=extraction.provider_key,
            created_at=extraction.created_at,
            reviewed_at=extraction.reviewed_at,
            candidate_tasks=[
                NoteTaskCandidateResponse(title=str(candidate.get("title", "")), notes=candidate.get("notes"))
                for candidate in extraction.candidate_tasks
            ],
        )


def default_week_start() -> str:
    now = datetime.now(UTC).date()
    monday = now - timedelta(days=now.weekday())
    return date.isoformat(monday)
