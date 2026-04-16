"""add focus sessions and blocker events

Revision ID: 20260415_0005
Revises: 20260415_0004
Create Date: 2026-04-15 03:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260415_0005"
down_revision = "20260415_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "focus_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pre_task_energy", sa.Float(), nullable=False),
        sa.Column("post_task_energy", sa.Float(), nullable=True),
        sa.Column("sidetrack_count", sa.Integer(), nullable=False),
        sa.Column("sidetrack_note", sa.Text(), nullable=True),
        sa.Column("unable_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('active','completed','unable')", name="ck_focus_sessions_status"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_focus_sessions_owner_user_id", "focus_sessions", ["owner_user_id"])
    op.create_index("ix_focus_sessions_task_id", "focus_sessions", ["task_id"])
    op.create_index("ix_focus_sessions_status", "focus_sessions", ["status"])

    op.create_table(
        "blocker_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("focus_session_id", sa.String(length=36), nullable=True),
        sa.Column("blocker_reason", sa.String(length=32), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "blocker_reason IN ('unclear_requirement','missing_dependency','external_wait','low_energy_focus','time_fragmentation','mental_resistance','context_not_available')",
            name="ck_blocker_events_reason",
        ),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["focus_session_id"], ["focus_sessions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_blocker_events_owner_user_id", "blocker_events", ["owner_user_id"])
    op.create_index("ix_blocker_events_task_id", "blocker_events", ["task_id"])
    op.create_index("ix_blocker_events_focus_session_id", "blocker_events", ["focus_session_id"])
    op.create_index("ix_blocker_events_blocker_reason", "blocker_events", ["blocker_reason"])


def downgrade() -> None:
    op.drop_index("ix_blocker_events_blocker_reason", table_name="blocker_events")
    op.drop_index("ix_blocker_events_focus_session_id", table_name="blocker_events")
    op.drop_index("ix_blocker_events_task_id", table_name="blocker_events")
    op.drop_index("ix_blocker_events_owner_user_id", table_name="blocker_events")
    op.drop_table("blocker_events")

    op.drop_index("ix_focus_sessions_status", table_name="focus_sessions")
    op.drop_index("ix_focus_sessions_task_id", table_name="focus_sessions")
    op.drop_index("ix_focus_sessions_owner_user_id", table_name="focus_sessions")
    op.drop_table("focus_sessions")
