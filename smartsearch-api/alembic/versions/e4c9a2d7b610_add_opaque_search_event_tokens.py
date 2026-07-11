"""Add opaque public search event tokens.

Revision ID: e4c9a2d7b610
Revises: d8b2f1a6c540
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e4c9a2d7b610"
down_revision: str | None = "d8b2f1a6c540"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("search_query_logs", sa.Column("event_token", sa.String(), nullable=True))
    op.execute(
        "UPDATE search_query_logs SET event_token = gen_random_uuid()::text "
        "WHERE event_token IS NULL"
    )
    op.alter_column("search_query_logs", "event_token", nullable=False)
    op.create_index(
        "ix_search_query_logs_event_token",
        "search_query_logs",
        ["event_token"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_search_query_logs_event_token", table_name="search_query_logs")
    op.drop_column("search_query_logs", "event_token")
