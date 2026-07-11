"""Add revocable public widget tokens.

Revision ID: f5d1b8c3a720
Revises: e4c9a2d7b610
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f5d1b8c3a720"
down_revision: str | None = "e4c9a2d7b610"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("stores", sa.Column("widget_token", sa.String(), nullable=True))
    op.execute(
        "UPDATE stores SET widget_token = 'ss_widget_' || replace(gen_random_uuid()::text, '-', '') "
        "WHERE widget_token IS NULL"
    )
    op.alter_column("stores", "widget_token", nullable=False)
    op.create_unique_constraint("uq_stores_widget_token", "stores", ["widget_token"])


def downgrade() -> None:
    op.drop_constraint("uq_stores_widget_token", "stores", type_="unique")
    op.drop_column("stores", "widget_token")
