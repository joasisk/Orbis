"""add calendar integration tables

Revision ID: 20260417_0010
Revises: 20260416_0009
Create Date: 2026-04-17 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260417_0010"
down_revision: str | None = "20260416_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "calendar_external_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("provider_key", sa.String(length=64), nullable=False),
        sa.Column("external_event_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "owner_user_id", "provider_key", "external_event_id", name="uq_calendar_external_events_provider_event"
        ),
    )
    op.create_index(op.f("ix_calendar_external_events_owner_user_id"), "calendar_external_events", ["owner_user_id"], unique=False)

    op.create_table(
        "calendar_soft_blocks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("daily_schedule_id", sa.String(length=36), nullable=False),
        sa.Column("daily_schedule_item_id", sa.String(length=36), nullable=False),
        sa.Column("provider_key", sa.String(length=64), nullable=False),
        sa.Column("external_block_id", sa.String(length=128), nullable=False),
        sa.Column("block_date", sa.Date(), nullable=False),
        sa.Column("source_daily_schedule_status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("source_daily_schedule_status = 'accepted'", name="ck_calendar_soft_blocks_accepted_only"),
        sa.ForeignKeyConstraint(["daily_schedule_id"], ["daily_schedules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["daily_schedule_item_id"], ["daily_schedule_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("daily_schedule_item_id", name="uq_calendar_soft_blocks_day_item"),
    )
    op.create_index(op.f("ix_calendar_soft_blocks_owner_user_id"), "calendar_soft_blocks", ["owner_user_id"], unique=False)
    op.create_index(op.f("ix_calendar_soft_blocks_daily_schedule_id"), "calendar_soft_blocks", ["daily_schedule_id"], unique=False)
    op.create_index(
        op.f("ix_calendar_soft_blocks_daily_schedule_item_id"), "calendar_soft_blocks", ["daily_schedule_item_id"], unique=False
    )
    op.create_index(op.f("ix_calendar_soft_blocks_block_date"), "calendar_soft_blocks", ["block_date"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_calendar_soft_blocks_block_date"), table_name="calendar_soft_blocks")
    op.drop_index(op.f("ix_calendar_soft_blocks_daily_schedule_item_id"), table_name="calendar_soft_blocks")
    op.drop_index(op.f("ix_calendar_soft_blocks_daily_schedule_id"), table_name="calendar_soft_blocks")
    op.drop_index(op.f("ix_calendar_soft_blocks_owner_user_id"), table_name="calendar_soft_blocks")
    op.drop_table("calendar_soft_blocks")

    op.drop_index(op.f("ix_calendar_external_events_owner_user_id"), table_name="calendar_external_events")
    op.drop_table("calendar_external_events")
