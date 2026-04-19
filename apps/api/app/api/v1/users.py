from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.user import CreateSpouseRequest, SpouseStatusResponse, UserMeResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserMeResponse:
    return UserMeResponse.model_validate(current_user, from_attributes=True)


@router.get("/owner-only", response_model=UserMeResponse)
def owner_only(current_user: User = Depends(require_roles("owner"))) -> UserMeResponse:
    return UserMeResponse.model_validate(current_user, from_attributes=True)


@router.get("/household", response_model=UserMeResponse)
def household(current_user: User = Depends(require_roles("owner", "spouse"))) -> UserMeResponse:
    return UserMeResponse.model_validate(current_user, from_attributes=True)


@router.get("/spouse", response_model=SpouseStatusResponse)
def spouse_status(
    current_user: User = Depends(require_roles("owner")),
    db: Session = Depends(get_db),
) -> SpouseStatusResponse:
    spouse_user = db.scalar(select(User).where(User.role == UserRole.SPOUSE.value).order_by(User.created_at.desc()))
    if spouse_user is None:
        return SpouseStatusResponse(spouse=None)
    return SpouseStatusResponse(spouse=UserMeResponse.model_validate(spouse_user, from_attributes=True))


@router.post("/spouse", response_model=UserMeResponse, status_code=status.HTTP_201_CREATED)
def create_spouse(
    payload: CreateSpouseRequest,
    current_user: User = Depends(require_roles("owner")),
    db: Session = Depends(get_db),
) -> UserMeResponse:
    spouse_user = AuthService.create_spouse(db, current_user, payload.email, payload.password)
    return UserMeResponse.model_validate(spouse_user, from_attributes=True)
