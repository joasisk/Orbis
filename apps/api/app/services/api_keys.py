from __future__ import annotations

import hashlib
import secrets
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.api_client_key import ApiClientKey
from app.models.user import User


class ApiKeyService:
    @staticmethod
    def _hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    def _encode_scopes(scopes: list[str]) -> str | None:
        cleaned = [scope.strip() for scope in scopes if scope.strip()]
        if not cleaned:
            return None
        return ",".join(sorted(set(cleaned)))

    @staticmethod
    def _decode_scopes(scopes: str | None) -> list[str]:
        if not scopes:
            return []
        return [scope for scope in scopes.split(",") if scope]

    @classmethod
    def create_key(cls, db: Session, user_id: str, name: str, scopes: list[str]) -> tuple[ApiClientKey, str]:
        raw_key = f"orbis_{secrets.token_urlsafe(32)}"
        key = ApiClientKey(
            user_id=user_id,
            name=name,
            key_prefix=raw_key[:12],
            key_hash=cls._hash_key(raw_key),
            scopes=cls._encode_scopes(scopes),
            is_active=True,
        )
        db.add(key)
        db.commit()
        db.refresh(key)
        return key, raw_key

    @classmethod
    def list_keys_for_user(cls, db: Session, user_id: str) -> list[ApiClientKey]:
        return list(db.scalars(select(ApiClientKey).where(ApiClientKey.user_id == user_id).order_by(ApiClientKey.created_at.desc())))

    @classmethod
    def revoke_key(cls, db: Session, user_id: str, key_id: str) -> ApiClientKey:
        key = db.scalar(select(ApiClientKey).where(ApiClientKey.id == key_id, ApiClientKey.user_id == user_id))
        if key is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

        if key.is_active:
            key.is_active = False
            key.revoked_at = datetime.utcnow()
            db.add(key)
            db.commit()
            db.refresh(key)

        return key

    @classmethod
    def resolve_user_from_raw_key(cls, db: Session, raw_key: str) -> User | None:
        key_hash = cls._hash_key(raw_key)
        key = db.scalar(
            select(ApiClientKey).where(
                ApiClientKey.key_hash == key_hash,
                ApiClientKey.is_active.is_(True),
            )
        )
        if key is None:
            return None

        key.last_used_at = datetime.utcnow()
        db.add(key)

        user = db.scalar(select(User).where(User.id == key.user_id, User.is_active.is_(True)))
        if user is None:
            return None

        db.commit()
        return user

    @classmethod
    def scopes_for_key(cls, key: ApiClientKey) -> list[str]:
        return cls._decode_scopes(key.scopes)

    @classmethod
    def scopes_from_serialized(cls, serialized: str | None) -> list[str]:
        return cls._decode_scopes(serialized)
