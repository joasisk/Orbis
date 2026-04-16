"""add reminder events table

Revision ID: 20260416_0009
Revises: 20260416_0008
Create Date: 2026-04-16 00:50:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260416_0009"
down_revision: str | None = "20260416_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reminder_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("daily_schedule_id", sa.String(length=36), nullable=True),
        sa.Column("daily_schedule_item_id", sa.String(length=36), nullable=True),
        sa.Column("delivery_channel", sa.String(length=16), nullable=False),
        sa.Column("response_status", sa.String(length=16), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("response_delay_seconds", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "delivery_channel IN ('in_app','email','push')",
            name="ck_reminder_events_delivery_channel",
        ),
        sa.CheckConstraint(
            "response_status IN ('pending','acknowledged','snoozed','dismissed')",
            name="ck_reminder_events_response_status",
        ),
        sa.CheckConstraint(
            "(daily_schedule_item_id IS NOT NULL) OR (daily_schedule_id IS NOT NULL)",
            name="ck_reminder_events_schedule_ref_required",
        ),
        sa.CheckConstraint(
            "response_delay_seconds IS NULL OR response_delay_seconds >= 0",
            name="ck_reminder_events_response_delay_non_negative",
        ),
        sa.ForeignKeyConstraint(["daily_schedule_id"], ["daily_schedules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["daily_schedule_item_id"], ["daily_schedule_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reminder_events_owner_user_id"), "reminder_events", ["owner_user_id"], unique=False)
    op.create_index(op.f("ix_reminder_events_daily_schedule_id"), "reminder_events", ["daily_schedule_id"], unique=False)
    op.create_index(op.f("ix_reminder_events_daily_schedule_item_id"), "reminder_events", ["daily_schedule_item_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reminder_events_daily_schedule_item_id"), table_name="reminder_events")
    op.drop_index(op.f("ix_reminder_events_daily_schedule_id"), table_name="reminder_events")
    op.drop_index(op.f("ix_reminder_events_owner_user_id"), table_name="reminder_events")
    op.drop_table("reminder_events")
