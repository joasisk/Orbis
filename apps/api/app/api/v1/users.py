from fastapi import APIRouter, Depends

from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.schemas.user import UserMeResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserMeResponse:
    return UserMeResponse.model_validate(current_user, from_attributes=True)


@router.get("/owner-only", response_model=UserMeResponse)
def owner_only(current_user: User = Depends(require_roles("owner"))) -> UserMeResponse:
    return UserMeResponse.model_validate(current_user, from_attributes=True)
