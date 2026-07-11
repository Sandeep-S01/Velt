"""Store returned product IDs for click attribution.

Revision ID: b7f3d0e5c940
Revises: a6e2c9d4b830
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b7f3d0e5c940"
down_revision: str | None = "a6e2c9d4b830"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("search_query_logs", sa.Column("result_product_ids", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("search_query_logs", "result_product_ids")
