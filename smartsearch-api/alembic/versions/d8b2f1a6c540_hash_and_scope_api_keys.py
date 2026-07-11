"""Hash and scope API keys.

Revision ID: d8b2f1a6c540
Revises: c3a7d9e2f401
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d8b2f1a6c540"
down_revision: str | None = "c3a7d9e2f401"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("api_keys", sa.Column("key_hash", sa.String(), nullable=True))
    op.add_column("api_keys", sa.Column("key_prefix", sa.String(), nullable=True))
    op.add_column(
        "api_keys",
        sa.Column("scopes", sa.String(), server_default="search,ingest", nullable=False),
    )
    op.add_column("api_keys", sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"], unique=True)
    op.create_index("ix_api_keys_key_prefix", "api_keys", ["key_prefix"])

    # PostgreSQL production migration: convert legacy plaintext keys before clearing them.
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute(
        "UPDATE api_keys SET key_hash = encode(digest(key, 'sha256'), 'hex'), "
        "key_prefix = left(key, 16) WHERE key IS NOT NULL"
    )
    op.alter_column("api_keys", "key", existing_type=sa.String(), nullable=True)
    op.execute("UPDATE api_keys SET key = NULL WHERE key_hash IS NOT NULL")


def downgrade() -> None:
    raise RuntimeError("API key hashing is irreversible; rotate keys instead of downgrading")
