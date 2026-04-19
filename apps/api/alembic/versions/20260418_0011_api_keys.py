"""add api client keys table

Revision ID: 20260418_0011
Revises: 20260417_0010
Create Date: 2026-04-18 00:11:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260418_0011"
down_revision = "20260417_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_client_keys",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("key_prefix", sa.String(length=16), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("scopes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_api_client_keys_user_id", "api_client_keys", ["user_id"], unique=False)
    op.create_index("ix_api_client_keys_key_hash", "api_client_keys", ["key_hash"], unique=True)
    op.create_index("ix_api_client_keys_key_prefix", "api_client_keys", ["key_prefix"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_api_client_keys_key_prefix", table_name="api_client_keys")
    op.drop_index("ix_api_client_keys_key_hash", table_name="api_client_keys")
    op.drop_index("ix_api_client_keys_user_id", table_name="api_client_keys")
    op.drop_table("api_client_keys")
