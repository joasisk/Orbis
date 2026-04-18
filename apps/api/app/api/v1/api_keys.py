from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_roles
from app.models.user import User, UserRole
from app.schemas.api_key import ApiKeyCreateRequest, ApiKeyCreateResponse, ApiKeySummaryResponse
from app.services.api_keys import ApiKeyService

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.get("", response_model=list[ApiKeySummaryResponse])
def list_api_keys(
    current_user: User = Depends(require_roles(UserRole.OWNER.value)),
    db: Session = Depends(get_db),
) -> list[ApiKeySummaryResponse]:
    keys = ApiKeyService.list_keys_for_user(db, current_user.id)
    return [
        ApiKeySummaryResponse(
            id=key.id,
            name=key.name,
            key_prefix=key.key_prefix,
            scopes=ApiKeyService.scopes_from_serialized(key.scopes),
            is_active=key.is_active,
            last_used_at=key.last_used_at,
            created_at=key.created_at,
            revoked_at=key.revoked_at,
        )
        for key in keys
    ]


@router.post("", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: ApiKeyCreateRequest,
    current_user: User = Depends(require_roles(UserRole.OWNER.value)),
    db: Session = Depends(get_db),
) -> ApiKeyCreateResponse:
    key, raw_key = ApiKeyService.create_key(db, current_user.id, payload.name, payload.scopes)
    return ApiKeyCreateResponse(
        id=key.id,
        name=key.name,
        key_prefix=key.key_prefix,
        api_key=raw_key,
        scopes=ApiKeyService.scopes_from_serialized(key.scopes),
        created_at=key.created_at,
    )


@router.post("/{key_id}/revoke", response_model=ApiKeySummaryResponse)
def revoke_api_key(
    key_id: str,
    current_user: User = Depends(require_roles(UserRole.OWNER.value)),
    db: Session = Depends(get_db),
) -> ApiKeySummaryResponse:
    key = ApiKeyService.revoke_key(db, current_user.id, key_id)
    return ApiKeySummaryResponse(
        id=key.id,
        name=key.name,
        key_prefix=key.key_prefix,
        scopes=ApiKeyService.scopes_from_serialized(key.scopes),
        is_active=key.is_active,
        last_used_at=key.last_used_at,
        created_at=key.created_at,
        revoked_at=key.revoked_at,
    )
