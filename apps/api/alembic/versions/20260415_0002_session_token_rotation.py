"""add session token rotation fields

Revision ID: 20260415_0002
Revises: 20260415_0001
Create Date: 2026-04-15 00:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260415_0002"
down_revision = "20260415_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("session_tokens", sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_session_tokens_token_hash", "session_tokens", ["token_hash"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_session_tokens_token_hash", table_name="session_tokens")
    op.drop_column("session_tokens", "revoked_at")
