from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.calendar import CalendarExternalEvent, CalendarSoftBlock
from app.models.planning import DailySchedule, DailyScheduleItem
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.calendar import CalendarImportResponse, CalendarSoftBlockExportResponse


@dataclass
class ProviderEvent:
    external_event_id: str
    title: str
    start_at: datetime
    end_at: datetime
    source_updated_at: datetime


class MockCalendarAdapter:
    provider_key = "mock-calendar"

    def list_events(self, owner_id: str, start_date: date, end_date: date) -> list[ProviderEvent]:
        events: list[ProviderEvent] = []
        cursor = start_date
        idx = 1
        while cursor <= end_date:
            if cursor.weekday() < 5:
                start_at = datetime.combine(cursor, datetime.min.time(), tzinfo=UTC).replace(hour=9)
                events.append(
                    ProviderEvent(
                        external_event_id=f"{owner_id[:8]}-{cursor.isoformat()}-{idx}",
                        title=f"Existing commitment ({cursor.strftime('%a')})",
                        start_at=start_at,
                        end_at=start_at + timedelta(minutes=30),
                        source_updated_at=datetime.now(UTC),
                    )
                )
                idx += 1
            cursor = cursor + timedelta(days=1)
        return events

    def create_soft_block(self, owner_id: str, day_item_id: str, schedule_date: date, planned_minutes: int) -> str:
        return f"{owner_id[:8]}-{schedule_date.isoformat()}-{day_item_id[:8]}-{planned_minutes}"


class CalendarService:
    @staticmethod
    def _resolved_provider(db: Session, actor: User) -> MockCalendarAdapter:
        settings = db.scalar(select(UserSettings).where(UserSettings.owner_user_id == actor.id))
        if settings is None or not settings.calendar_connected:
            raise HTTPException(status_code=409, detail="Calendar integration is not connected")
        if settings.calendar_provider != "mock-calendar":
            raise HTTPException(status_code=422, detail="Only mock-calendar provider is currently supported")
        return MockCalendarAdapter()

    @staticmethod
    def import_external_events(db: Session, actor: User, start_date: date, end_date: date) -> CalendarImportResponse:
        if end_date < start_date:
            raise HTTPException(status_code=422, detail="end_date must be greater than or equal to start_date")

        provider = CalendarService._resolved_provider(db, actor)
        provider_events = provider.list_events(owner_id=actor.id, start_date=start_date, end_date=end_date)

        imported: list[CalendarExternalEvent] = []
        for source_event in provider_events:
            existing = db.scalar(
                select(CalendarExternalEvent).where(
                    CalendarExternalEvent.owner_user_id == actor.id,
                    CalendarExternalEvent.provider_key == provider.provider_key,
                    CalendarExternalEvent.external_event_id == source_event.external_event_id,
                )
            )
            if existing is None:
                existing = CalendarExternalEvent(
                    owner_user_id=actor.id,
                    provider_key=provider.provider_key,
                    external_event_id=source_event.external_event_id,
                    title=source_event.title,
                    start_at=source_event.start_at,
                    end_at=source_event.end_at,
                    source_updated_at=source_event.source_updated_at,
                )
                db.add(existing)
            else:
                existing.title = source_event.title
                existing.start_at = source_event.start_at
                existing.end_at = source_event.end_at
                existing.source_updated_at = source_event.source_updated_at
                existing.imported_at = datetime.utcnow()
            imported.append(existing)

        db.commit()
        for event in imported:
            db.refresh(event)

        return CalendarImportResponse(
            imported_count=len(imported),
            events=[
                {
                    "id": event.id,
                    "provider_key": event.provider_key,
                    "external_event_id": event.external_event_id,
                    "title": event.title,
                    "start_at": event.start_at,
                    "end_at": event.end_at,
                    "source_updated_at": event.source_updated_at,
                }
                for event in imported
            ],
        )

    @staticmethod
    def export_daily_schedule_soft_blocks(db: Session, actor: User, daily_schedule_id: str) -> CalendarSoftBlockExportResponse:
        provider = CalendarService._resolved_provider(db, actor)
        schedule = db.scalar(select(DailySchedule).where(DailySchedule.id == daily_schedule_id))
        if schedule is None:
            raise HTTPException(status_code=404, detail="Daily schedule not found")
        if schedule.owner_user_id != actor.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        if schedule.status != "accepted":
            raise HTTPException(status_code=409, detail="Only accepted daily schedules can be exported")

        day_items = list(
            db.scalars(
                select(DailyScheduleItem)
                .where(DailyScheduleItem.daily_schedule_id == schedule.id)
                .order_by(DailyScheduleItem.order_index.asc())
            ).all()
        )

        exported: list[CalendarSoftBlock] = []
        for day_item in day_items:
            existing = db.scalar(select(CalendarSoftBlock).where(CalendarSoftBlock.daily_schedule_item_id == day_item.id))
            if existing is not None:
                exported.append(existing)
                continue

            block = CalendarSoftBlock(
                owner_user_id=actor.id,
                daily_schedule_id=schedule.id,
                daily_schedule_item_id=day_item.id,
                provider_key=provider.provider_key,
                external_block_id=provider.create_soft_block(
                    owner_id=actor.id,
                    day_item_id=day_item.id,
                    schedule_date=schedule.schedule_date,
                    planned_minutes=day_item.planned_minutes,
                ),
                block_date=schedule.schedule_date,
                source_daily_schedule_status=schedule.status,
            )
            db.add(block)
            exported.append(block)

        db.commit()
        for block in exported:
            db.refresh(block)

        return CalendarSoftBlockExportResponse(
            exported_count=len(exported),
            blocks=[
                {
                    "id": block.id,
                    "daily_schedule_id": block.daily_schedule_id,
                    "daily_schedule_item_id": block.daily_schedule_item_id,
                    "provider_key": block.provider_key,
                    "external_block_id": block.external_block_id,
                    "block_date": block.block_date,
                    "created_at": block.created_at,
                }
                for block in exported
            ],
        )
