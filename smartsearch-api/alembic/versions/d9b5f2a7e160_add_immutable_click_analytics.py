"""Add immutable click events and measured search latency.

Revision ID: d9b5f2a7e160
Revises: c8a4e1f6d050
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d9b5f2a7e160"
down_revision: str | None = "c8a4e1f6d050"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("search_query_logs", sa.Column("duration_ms", sa.Float(), nullable=True))
    op.create_table(
        "search_click_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("query_log_id", sa.Integer(), nullable=False),
        sa.Column("store_id", sa.String(), nullable=False),
        sa.Column("product_external_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["query_log_id"], ["search_query_logs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("query_log_id", name="uq_search_click_events_query_log"),
    )
    op.create_index("ix_search_click_events_store_created", "search_click_events", ["store_id", "created_at"])

    # Preserve historical click attribution before retiring mutable writes.
    op.execute(
        "INSERT INTO search_click_events (id, query_log_id, store_id, product_external_id) "
        "SELECT gen_random_uuid()::text, id, store_id, clicked_product_id "
        "FROM search_query_logs WHERE clicked_product_id IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_index("ix_search_click_events_store_created", table_name="search_click_events")
    op.drop_table("search_click_events")
    op.drop_column("search_query_logs", "duration_ms")
