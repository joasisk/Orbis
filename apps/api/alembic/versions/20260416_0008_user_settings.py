"""add user settings table

Revision ID: 20260416_0008
Revises: 20260416_0007
Create Date: 2026-04-16 00:08:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260416_0008"
down_revision: str | Sequence[str] | None = "20260416_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_settings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("reminder_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("reminder_window_start", sa.String(length=5), nullable=False, server_default="08:00"),
        sa.Column("reminder_window_end", sa.String(length=5), nullable=False, server_default="20:00"),
        sa.Column("calendar_connected", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("calendar_provider", sa.String(length=64), nullable=True),
        sa.Column("notes_connected", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("notes_provider", sa.String(length=64), nullable=True),
        sa.Column("ai_planning_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("ai_auto_generate_weekly", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("ai_require_manual_approval", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("ai_preferred_provider", sa.String(length=64), nullable=True),
        sa.Column("session_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_settings")
