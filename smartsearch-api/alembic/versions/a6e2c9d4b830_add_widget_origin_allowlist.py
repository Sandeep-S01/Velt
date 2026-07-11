"""Add optional widget storefront origin allowlist.

Revision ID: a6e2c9d4b830
Revises: f5d1b8c3a720
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a6e2c9d4b830"
down_revision: str | None = "f5d1b8c3a720"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("stores", sa.Column("widget_allowed_origins", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("stores", "widget_allowed_origins")
