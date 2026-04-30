"""migrate task priority and urgency to enums and constrain task status

Revision ID: 20260430_0014
Revises: 20260419_0013
Create Date: 2026-04-30 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260430_0014"
down_revision = "20260419_0013"
branch_labels = None
depends_on = None


PRIORITY_CASE = """
CASE
    WHEN {column} IS NULL THEN NULL
    WHEN {column} >= 4 THEN 'core'
    WHEN {column} = 3 THEN 'major'
    WHEN {column} = 2 THEN 'minor'
    ELSE 'ambient'
END
"""

URGENCY_CASE = """
CASE
    WHEN {column} IS NULL THEN NULL
    WHEN {column} >= 4 THEN 'immediate'
    WHEN {column} = 3 THEN 'near'
    WHEN {column} = 2 THEN 'planned'
    ELSE 'flexible'
END
"""


def upgrade() -> None:
    op.execute("UPDATE tasks SET status = 'staged' WHERE status = 'todo' OR status IS NULL")

    op.alter_column(
        "tasks",
        "priority",
        existing_type=sa.Integer(),
        type_=sa.String(length=16),
        existing_nullable=True,
        postgresql_using=PRIORITY_CASE.format(column="priority"),
    )
    op.alter_column(
        "tasks",
        "urgency",
        existing_type=sa.Integer(),
        type_=sa.String(length=16),
        existing_nullable=True,
        postgresql_using=URGENCY_CASE.format(column="urgency"),
    )
    op.alter_column(
        "tasks",
        "spouse_priority",
        existing_type=sa.Integer(),
        type_=sa.String(length=16),
        existing_nullable=True,
        postgresql_using=PRIORITY_CASE.format(column="spouse_priority"),
    )
    op.alter_column(
        "tasks",
        "spouse_urgency",
        existing_type=sa.Integer(),
        type_=sa.String(length=16),
        existing_nullable=True,
        postgresql_using=URGENCY_CASE.format(column="spouse_urgency"),
    )

    op.alter_column("tasks", "status", existing_type=sa.String(length=32), server_default="staged", existing_nullable=False)

    op.create_check_constraint("ck_tasks_priority", "tasks", "priority IN ('core','major','minor','ambient')")
    op.create_check_constraint("ck_tasks_urgency", "tasks", "urgency IN ('immediate','near','planned','flexible')")
    op.create_check_constraint("ck_tasks_spouse_priority", "tasks", "spouse_priority IN ('core','major','minor','ambient')")
    op.create_check_constraint(
        "ck_tasks_spouse_urgency", "tasks", "spouse_urgency IN ('immediate','near','planned','flexible')"
    )
    op.create_check_constraint(
        "ck_tasks_status",
        "tasks",
        "status IN ('staged','primed','in_flight','holding','mission_complete','scrubbed')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_tasks_status", "tasks", type_="check")
    op.drop_constraint("ck_tasks_spouse_urgency", "tasks", type_="check")
    op.drop_constraint("ck_tasks_spouse_priority", "tasks", type_="check")
    op.drop_constraint("ck_tasks_urgency", "tasks", type_="check")
    op.drop_constraint("ck_tasks_priority", "tasks", type_="check")

    op.alter_column("tasks", "status", existing_type=sa.String(length=32), server_default="todo", existing_nullable=False)
    op.execute("UPDATE tasks SET status = 'todo' WHERE status = 'staged'")

    op.alter_column(
        "tasks",
        "spouse_urgency",
        existing_type=sa.String(length=16),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="""
        CASE spouse_urgency
            WHEN 'immediate' THEN 4
            WHEN 'near' THEN 3
            WHEN 'planned' THEN 2
            WHEN 'flexible' THEN 1
            ELSE NULL
        END
        """,
    )
    op.alter_column(
        "tasks",
        "spouse_priority",
        existing_type=sa.String(length=16),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="""
        CASE spouse_priority
            WHEN 'core' THEN 4
            WHEN 'major' THEN 3
            WHEN 'minor' THEN 2
            WHEN 'ambient' THEN 1
            ELSE NULL
        END
        """,
    )
    op.alter_column(
        "tasks",
        "urgency",
        existing_type=sa.String(length=16),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="""
        CASE urgency
            WHEN 'immediate' THEN 4
            WHEN 'near' THEN 3
            WHEN 'planned' THEN 2
            WHEN 'flexible' THEN 1
            ELSE NULL
        END
        """,
    )
    op.alter_column(
        "tasks",
        "priority",
        existing_type=sa.String(length=16),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="""
        CASE priority
            WHEN 'core' THEN 4
            WHEN 'major' THEN 3
            WHEN 'minor' THEN 2
            WHEN 'ambient' THEN 1
            ELSE NULL
        END
        """,
    )
