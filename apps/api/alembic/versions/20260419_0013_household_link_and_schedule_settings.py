"""add spouse-owner link and schedule settings fields

Revision ID: 20260419_0013
Revises: 20260419_0012
Create Date: 2026-04-19 01:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260419_0013"
down_revision = "20260419_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("linked_owner_user_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        "fk_users_linked_owner_user_id_users",
        "users",
        "users",
        ["linked_owner_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("user_settings", sa.Column("app_timezone", sa.String(length=64), nullable=False, server_default="UTC"))
    op.add_column("user_settings", sa.Column("weekly_planning_enabled", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("user_settings", sa.Column("weekly_planning_day_of_week", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("user_settings", sa.Column("weekly_planning_time_local", sa.String(length=5), nullable=False, server_default="20:00"))
    op.add_column("user_settings", sa.Column("notes_scan_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("user_settings", sa.Column("notes_scan_frequency", sa.String(length=16), nullable=False, server_default="weekly"))
    op.add_column("user_settings", sa.Column("notes_scan_day_of_week", sa.Integer(), nullable=True))
    op.add_column("user_settings", sa.Column("notes_scan_time_local", sa.String(length=5), nullable=True))
    op.add_column(
        "user_settings",
        sa.Column("reminder_scan_interval_minutes", sa.Integer(), nullable=False, server_default="60"),
    )
    op.add_column("user_settings", sa.Column("automation_pause_until", sa.DateTime(timezone=True), nullable=True))

    op.alter_column("user_settings", "app_timezone", server_default=None)
    op.alter_column("user_settings", "weekly_planning_enabled", server_default=None)
    op.alter_column("user_settings", "weekly_planning_day_of_week", server_default=None)
    op.alter_column("user_settings", "weekly_planning_time_local", server_default=None)
    op.alter_column("user_settings", "notes_scan_enabled", server_default=None)
    op.alter_column("user_settings", "notes_scan_frequency", server_default=None)
    op.alter_column("user_settings", "reminder_scan_interval_minutes", server_default=None)


def downgrade() -> None:
    op.drop_column("user_settings", "automation_pause_until")
    op.drop_column("user_settings", "reminder_scan_interval_minutes")
    op.drop_column("user_settings", "notes_scan_time_local")
    op.drop_column("user_settings", "notes_scan_day_of_week")
    op.drop_column("user_settings", "notes_scan_frequency")
    op.drop_column("user_settings", "notes_scan_enabled")
    op.drop_column("user_settings", "weekly_planning_time_local")
    op.drop_column("user_settings", "weekly_planning_day_of_week")
    op.drop_column("user_settings", "weekly_planning_enabled")
    op.drop_column("user_settings", "app_timezone")

    op.drop_constraint("fk_users_linked_owner_user_id_users", "users", type_="foreignkey")
    op.drop_column("users", "linked_owner_user_id")
