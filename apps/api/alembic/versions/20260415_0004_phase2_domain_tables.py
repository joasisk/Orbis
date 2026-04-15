"""add phase2 domain tables

Revision ID: 20260415_0004
Revises: 20260415_0003
Create Date: 2026-04-15 02:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260415_0004"
down_revision = "20260415_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "areas_of_life",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("area_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False),
        sa.Column("visibility_scope", sa.String(length=16), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("urgency", sa.Integer(), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline_type", sa.String(length=8), nullable=True),
        sa.Column("spouse_priority", sa.Integer(), nullable=True),
        sa.Column("spouse_urgency", sa.Integer(), nullable=True),
        sa.Column("spouse_deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("spouse_deadline_type", sa.String(length=8), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("deadline_type IN ('soft','hard')", name="ck_projects_deadline_type"),
        sa.CheckConstraint("spouse_deadline_type IN ('soft','hard')", name="ck_projects_spouse_deadline_type"),
        sa.CheckConstraint("visibility_scope IN ('owner','spouse','shared')", name="ck_projects_visibility_scope"),
        sa.ForeignKeyConstraint(["area_id"], ["areas_of_life.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_area_id", "projects", ["area_id"])
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_index("ix_projects_visibility_scope", "projects", ["visibility_scope"])

    op.create_table(
        "tasks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False),
        sa.Column("visibility_scope", sa.String(length=16), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("urgency", sa.Integer(), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline_type", sa.String(length=8), nullable=True),
        sa.Column("spouse_priority", sa.Integer(), nullable=True),
        sa.Column("spouse_urgency", sa.Integer(), nullable=True),
        sa.Column("spouse_deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("spouse_deadline_type", sa.String(length=8), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("deadline_type IN ('soft','hard')", name="ck_tasks_deadline_type"),
        sa.CheckConstraint("spouse_deadline_type IN ('soft','hard')", name="ck_tasks_spouse_deadline_type"),
        sa.CheckConstraint("visibility_scope IN ('owner','spouse','shared')", name="ck_tasks_visibility_scope"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tasks_project_id", "tasks", ["project_id"])
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_visibility_scope", "tasks", ["visibility_scope"])

    op.create_table(
        "recurring_commitments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("cadence", sa.String(length=16), nullable=False),
        sa.Column("interval_count", sa.Integer(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("energy_weight", sa.Float(), nullable=True),
        sa.Column("starts_on", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_on", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("cadence IN ('daily','weekly','monthly')", name="ck_recurring_commitments_cadence"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "task_dependencies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("depends_on_task_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("task_id <> depends_on_task_id", name="ck_task_dependencies_not_self"),
        sa.ForeignKeyConstraint(["depends_on_task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id", "depends_on_task_id", name="uq_task_dependency_edge"),
    )
    op.create_index("ix_task_dependencies_task_id", "task_dependencies", ["task_id"])
    op.create_index("ix_task_dependencies_depends_on_task_id", "task_dependencies", ["depends_on_task_id"])

    op.create_table(
        "entity_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_user_id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("actor_user_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("changed_fields", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_entity_versions_owner_user_id", "entity_versions", ["owner_user_id"])
    op.create_index("ix_entity_versions_entity_type", "entity_versions", ["entity_type"])
    op.create_index("ix_entity_versions_entity_id", "entity_versions", ["entity_id"])


def downgrade() -> None:
    op.drop_index("ix_entity_versions_entity_id", table_name="entity_versions")
    op.drop_index("ix_entity_versions_entity_type", table_name="entity_versions")
    op.drop_index("ix_entity_versions_owner_user_id", table_name="entity_versions")
    op.drop_table("entity_versions")

    op.drop_index("ix_task_dependencies_depends_on_task_id", table_name="task_dependencies")
    op.drop_index("ix_task_dependencies_task_id", table_name="task_dependencies")
    op.drop_table("task_dependencies")

    op.drop_table("recurring_commitments")

    op.drop_index("ix_tasks_visibility_scope", table_name="tasks")
    op.drop_index("ix_tasks_status", table_name="tasks")
    op.drop_index("ix_tasks_project_id", table_name="tasks")
    op.drop_table("tasks")

    op.drop_index("ix_projects_visibility_scope", table_name="projects")
    op.drop_index("ix_projects_status", table_name="projects")
    op.drop_index("ix_projects_area_id", table_name="projects")
    op.drop_table("projects")

    op.drop_table("areas_of_life")
