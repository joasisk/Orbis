"""add ui language to user settings

Revision ID: 20260419_0012
Revises: 20260418_0011
Create Date: 2026-04-19 00:12:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260419_0012"
down_revision = "20260418_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_settings", sa.Column("ui_language", sa.String(length=8), nullable=False, server_default="en"))
    op.alter_column("user_settings", "ui_language", server_default=None)


def downgrade() -> None:
    op.drop_column("user_settings", "ui_language")
