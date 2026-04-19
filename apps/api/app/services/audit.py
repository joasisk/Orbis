from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


class AuditService:
    @staticmethod
    def list_events(db: Session, limit: int = 25) -> list[AuditEvent]:
        stmt = select(AuditEvent).order_by(desc(AuditEvent.created_at)).limit(limit)
        return list(db.scalars(stmt).all())
