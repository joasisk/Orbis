from datetime import date, datetime

from pydantic import BaseModel


class CalendarImportRequest(BaseModel):
    start_date: date
    end_date: date


class CalendarExternalEventResponse(BaseModel):
    id: str
    provider_key: str
    external_event_id: str
    title: str
    start_at: datetime
    end_at: datetime
    source_updated_at: datetime


class CalendarImportResponse(BaseModel):
    imported_count: int
    events: list[CalendarExternalEventResponse]


class CalendarSoftBlockResponse(BaseModel):
    id: str
    daily_schedule_id: str
    daily_schedule_item_id: str
    provider_key: str
    external_block_id: str
    block_date: date
    created_at: datetime


class CalendarSoftBlockExportResponse(BaseModel):
    exported_count: int
    blocks: list[CalendarSoftBlockResponse]
