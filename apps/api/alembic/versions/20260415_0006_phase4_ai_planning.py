"""add phase4 ai planning proposal and note extraction tables

Revision ID: 20260415_0006
Revises: 20260415_0005
Create Date: 2026-04-15 04:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260415_0006"
down_revision = "20260415_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "weekly_plan_proposals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("week_start_date", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("provider_key", sa.String(length=64), nullable=False),
        sa.Column("prompt_template_version", sa.String(length=64), nullable=False),
        sa.Column("evaluation_log", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('proposed','approved','rejected')", name="ck_weekly_plan_proposals_status"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_weekly_plan_proposals_owner_user_id", "weekly_plan_proposals", ["owner_user_id"])
    op.create_index("ix_weekly_plan_proposals_week_start_date", "weekly_plan_proposals", ["week_start_date"])
    op.create_index("ix_weekly_plan_proposals_status", "weekly_plan_proposals", ["status"])

    op.create_table(
        "weekly_plan_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("proposal_id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("suggested_day", sa.String(length=16), nullable=False),
        sa.Column("suggested_minutes", sa.Integer(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["proposal_id"], ["weekly_plan_proposals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_weekly_plan_items_proposal_id", "weekly_plan_items", ["proposal_id"])
    op.create_index("ix_weekly_plan_items_owner_user_id", "weekly_plan_items", ["owner_user_id"])
    op.create_index("ix_weekly_plan_items_task_id", "weekly_plan_items", ["task_id"])

    op.create_table(
        "note_extractions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("source_title", sa.String(length=200), nullable=False),
        sa.Column("source_ref", sa.String(length=400), nullable=True),
        sa.Column("note_content", sa.Text(), nullable=False),
        sa.Column("provider_key", sa.String(length=64), nullable=False),
        sa.Column("candidate_tasks", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('proposed','accepted','dismissed')", name="ck_note_extractions_status"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_note_extractions_owner_user_id", "note_extractions", ["owner_user_id"])
    op.create_index("ix_note_extractions_status", "note_extractions", ["status"])


def downgrade() -> None:
    op.drop_index("ix_note_extractions_status", table_name="note_extractions")
    op.drop_index("ix_note_extractions_owner_user_id", table_name="note_extractions")
    op.drop_table("note_extractions")

    op.drop_index("ix_weekly_plan_items_task_id", table_name="weekly_plan_items")
    op.drop_index("ix_weekly_plan_items_owner_user_id", table_name="weekly_plan_items")
    op.drop_index("ix_weekly_plan_items_proposal_id", table_name="weekly_plan_items")
    op.drop_table("weekly_plan_items")

    op.drop_index("ix_weekly_plan_proposals_status", table_name="weekly_plan_proposals")
    op.drop_index("ix_weekly_plan_proposals_week_start_date", table_name="weekly_plan_proposals")
    op.drop_index("ix_weekly_plan_proposals_owner_user_id", table_name="weekly_plan_proposals")
    op.drop_table("weekly_plan_proposals")
