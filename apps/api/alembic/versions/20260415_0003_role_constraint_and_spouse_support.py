"""add role constraint for users

Revision ID: 20260415_0003
Revises: 20260415_0002
Create Date: 2026-04-15 01:00:00
"""

from alembic import op


revision = "20260415_0003"
down_revision = "20260415_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE users SET role = lower(trim(role))")
    op.execute("UPDATE users SET role = 'owner' WHERE role IS NULL OR role NOT IN ('owner', 'spouse')")
    op.create_check_constraint("ck_users_role_valid", "users", "role IN ('owner', 'spouse')")


def downgrade() -> None:
    op.drop_constraint("ck_users_role_valid", "users", type_="check")
