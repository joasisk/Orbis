from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.audit_event import AuditEvent
from app.models.session import SessionToken
from app.models.user import User, UserRole

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthService:
    @staticmethod
    def requires_bootstrap(db: Session) -> bool:
        existing_user = db.scalar(select(User.id).limit(1))
        return existing_user is None

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def _create_access_token(user: User) -> str:
        expires_delta = timedelta(minutes=settings.api_access_token_expire_minutes)
        expires_at = datetime.now(UTC) + expires_delta
        payload = {
            "sub": user.id,
            "role": user.role,
            "type": "access",
            "exp": expires_at,
        }
        return jwt.encode(payload, settings.api_secret_key, algorithm="HS256")

    @staticmethod
    def _hash_refresh_token(refresh_token: str) -> str:
        return sha256(refresh_token.encode("utf-8")).hexdigest()

    @staticmethod
    def _create_refresh_session(db: Session, user: User) -> str:
        refresh_token = token_urlsafe(48)
        token_hash = AuthService._hash_refresh_token(refresh_token)
        expires_at = datetime.now(UTC) + timedelta(days=settings.api_refresh_token_expire_days)

        session_token = SessionToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        db.add(session_token)
        return refresh_token

    @staticmethod
    def _log_event(db: Session, user_id: str | None, event_type: str, metadata: dict) -> None:
        db.add(
            AuditEvent(
                actor_user_id=user_id,
                event_type=event_type,
                event_metadata=metadata,
            )
        )

    @staticmethod
    def bootstrap_owner(db: Session, email: str, password: str) -> None:
        if not AuthService.requires_bootstrap(db):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Owner already initialized")

        user = User(
            email=email.lower().strip(),
            hashed_password=AuthService.hash_password(password),
            role=UserRole.OWNER.value,
            is_active=True,
        )
        db.add(user)
        db.flush()
        AuthService._log_event(db, user.id, "auth.bootstrap_owner", {"email": user.email})
        db.commit()

    @staticmethod
    def create_spouse(db: Session, actor_user: User, email: str, password: str) -> User:
        normalized_email = email.lower().strip()
        existing_user = db.scalar(select(User).where(User.email == normalized_email))
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        spouse_user = User(
            email=normalized_email,
            hashed_password=AuthService.hash_password(password),
            role=UserRole.SPOUSE.value,
            is_active=True,
        )
        db.add(spouse_user)
        db.flush()
        AuthService._log_event(
            db,
            actor_user.id,
            "auth.create_spouse",
            {"spouse_user_id": spouse_user.id, "email": spouse_user.email},
        )
        db.commit()
        db.refresh(spouse_user)
        return spouse_user

    @staticmethod
    def login(db: Session, email: str, password: str) -> dict[str, str | int]:
        stmt: Select[tuple[User]] = select(User).where(User.email == email.lower().strip())
        user = db.scalar(stmt)

        if user is None or not AuthService.verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

        access_token = AuthService._create_access_token(user)
        refresh_token = AuthService._create_refresh_session(db, user)
        AuthService._log_event(db, user.id, "auth.login", {"email": user.email})
        db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.api_access_token_expire_minutes * 60,
        }

    @staticmethod
    def refresh(db: Session, refresh_token: str) -> dict[str, str | int]:
        token_hash = AuthService._hash_refresh_token(refresh_token)
        now = datetime.now(UTC)

        stmt: Select[tuple[SessionToken]] = select(SessionToken).where(
            SessionToken.token_hash == token_hash,
            SessionToken.revoked_at.is_(None),
            SessionToken.expires_at > now,
        )
        stored_session = db.scalar(stmt)

        if stored_session is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user = db.scalar(select(User).where(User.id == stored_session.user_id))
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        stored_session.revoked_at = now
        new_refresh_token = AuthService._create_refresh_session(db, user)
        access_token = AuthService._create_access_token(user)
        AuthService._log_event(db, user.id, "auth.refresh", {"session_id": stored_session.id})
        db.commit()

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "expires_in": settings.api_access_token_expire_minutes * 60,
        }

    @staticmethod
    def logout(db: Session, refresh_token: str) -> None:
        token_hash = AuthService._hash_refresh_token(refresh_token)
        session = db.scalar(select(SessionToken).where(SessionToken.token_hash == token_hash))
        if session is None:
            return

        session.revoked_at = datetime.now(UTC)
        AuthService._log_event(db, session.user_id, "auth.logout", {"session_id": session.id})
        db.commit()
