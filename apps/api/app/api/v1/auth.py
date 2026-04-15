from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.auth import BootstrapOwnerRequest, BootstrapStatusResponse, LoginRequest, RefreshRequest, TokenPairResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/bootstrap-owner", status_code=status.HTTP_201_CREATED)
def bootstrap_owner(payload: BootstrapOwnerRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    AuthService.bootstrap_owner(db, payload.email, payload.password)
    return {"status": "created"}


@router.get("/bootstrap-status", response_model=BootstrapStatusResponse)
def bootstrap_status(db: Session = Depends(get_db)) -> BootstrapStatusResponse:
    return BootstrapStatusResponse(requires_bootstrap=AuthService.requires_bootstrap(db))


@router.post("/login", response_model=TokenPairResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenPairResponse:
    tokens = AuthService.login(db, payload.email, payload.password)
    return TokenPairResponse(**tokens)


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPairResponse:
    tokens = AuthService.refresh(db, payload.refresh_token)
    return TokenPairResponse(**tokens)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)) -> None:
    AuthService.logout(db, payload.refresh_token)
    return None
