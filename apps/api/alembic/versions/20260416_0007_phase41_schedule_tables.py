"""add phase4.1 schedule tables and telemetry fields

Revision ID: 20260416_0007
Revises: 20260415_0006
Create Date: 2026-04-16 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260416_0007"
down_revision = "20260415_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "weekly_schedules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("week_start_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("source_proposal_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('proposed','accepted','rejected')", name="ck_weekly_schedules_status"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_proposal_id"], ["weekly_plan_proposals.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_user_id", "week_start_date", name="uq_weekly_schedules_owner_week"),
    )
    op.create_index("ix_weekly_schedules_owner_user_id", "weekly_schedules", ["owner_user_id"])
    op.create_index("ix_weekly_schedules_week_start_date", "weekly_schedules", ["week_start_date"])
    op.create_index("ix_weekly_schedules_status", "weekly_schedules", ["status"])
    op.create_index("ix_weekly_schedules_source_proposal_id", "weekly_schedules", ["source_proposal_id"])

    op.create_table(
        "daily_schedules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("weekly_schedule_id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("schedule_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("mood_score", sa.Integer(), nullable=True),
        sa.Column("morning_energy", sa.Float(), nullable=True),
        sa.Column("evening_energy", sa.Float(), nullable=True),
        sa.Column("self_evaluation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('proposed','accepted','adjusted')", name="ck_daily_schedules_status"),
        sa.CheckConstraint("mood_score IS NULL OR (mood_score >= 1 AND mood_score <= 5)", name="ck_daily_schedules_mood_score"),
        sa.CheckConstraint(
            "morning_energy IS NULL OR (morning_energy >= 0 AND morning_energy <= 1)",
            name="ck_daily_schedules_morning_energy",
        ),
        sa.CheckConstraint(
            "evening_energy IS NULL OR (evening_energy >= 0 AND evening_energy <= 1)",
            name="ck_daily_schedules_evening_energy",
        ),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["weekly_schedule_id"], ["weekly_schedules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("weekly_schedule_id", "schedule_date", name="uq_daily_schedules_week_day"),
    )
    op.create_index("ix_daily_schedules_weekly_schedule_id", "daily_schedules", ["weekly_schedule_id"])
    op.create_index("ix_daily_schedules_owner_user_id", "daily_schedules", ["owner_user_id"])
    op.create_index("ix_daily_schedules_schedule_date", "daily_schedules", ["schedule_date"])
    op.create_index("ix_daily_schedules_status", "daily_schedules", ["status"])

    op.create_table(
        "daily_schedule_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("daily_schedule_id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("planned_minutes", sa.Integer(), nullable=False),
        sa.Column("actual_minutes", sa.Integer(), nullable=True),
        sa.Column("outcome_status", sa.String(length=16), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("distraction_count", sa.Integer(), nullable=False),
        sa.Column("distraction_notes", sa.Text(), nullable=True),
        sa.Column("postponed_to_date", sa.Date(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("planned_minutes > 0", name="ck_daily_schedule_items_planned_minutes"),
        sa.CheckConstraint("actual_minutes IS NULL OR actual_minutes >= 0", name="ck_daily_schedule_items_actual_minutes"),
        sa.CheckConstraint("distraction_count >= 0", name="ck_daily_schedule_items_distraction_count"),
        sa.CheckConstraint(
            "(outcome_status = 'postponed' AND postponed_to_date IS NOT NULL) OR (outcome_status != 'postponed' AND postponed_to_date IS NULL)",
            name="ck_daily_schedule_items_postponed_date",
        ),
        sa.CheckConstraint(
            "outcome_status IN ('planned','done','postponed','failed','partial','skipped')",
            name="ck_daily_schedule_items_outcome_status",
        ),
        sa.ForeignKeyConstraint(["daily_schedule_id"], ["daily_schedules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("daily_schedule_id", "order_index", name="uq_daily_schedule_items_day_order"),
    )
    op.create_index("ix_daily_schedule_items_daily_schedule_id", "daily_schedule_items", ["daily_schedule_id"])
    op.create_index("ix_daily_schedule_items_owner_user_id", "daily_schedule_items", ["owner_user_id"])
    op.create_index("ix_daily_schedule_items_task_id", "daily_schedule_items", ["task_id"])
    op.create_index("ix_daily_schedule_items_outcome_status", "daily_schedule_items", ["outcome_status"])


def downgrade() -> None:
    op.drop_index("ix_daily_schedule_items_outcome_status", table_name="daily_schedule_items")
    op.drop_index("ix_daily_schedule_items_task_id", table_name="daily_schedule_items")
    op.drop_index("ix_daily_schedule_items_owner_user_id", table_name="daily_schedule_items")
    op.drop_index("ix_daily_schedule_items_daily_schedule_id", table_name="daily_schedule_items")
    op.drop_table("daily_schedule_items")

    op.drop_index("ix_daily_schedules_status", table_name="daily_schedules")
    op.drop_index("ix_daily_schedules_schedule_date", table_name="daily_schedules")
    op.drop_index("ix_daily_schedules_owner_user_id", table_name="daily_schedules")
    op.drop_index("ix_daily_schedules_weekly_schedule_id", table_name="daily_schedules")
    op.drop_table("daily_schedules")

    op.drop_index("ix_weekly_schedules_source_proposal_id", table_name="weekly_schedules")
    op.drop_index("ix_weekly_schedules_status", table_name="weekly_schedules")
    op.drop_index("ix_weekly_schedules_week_start_date", table_name="weekly_schedules")
    op.drop_index("ix_weekly_schedules_owner_user_id", table_name="weekly_schedules")
    op.drop_table("weekly_schedules")
