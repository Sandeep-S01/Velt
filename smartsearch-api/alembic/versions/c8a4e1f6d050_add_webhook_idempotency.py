"""Add Shopify webhook idempotency constraint.

Revision ID: c8a4e1f6d050
Revises: b7f3d0e5c940
Create Date: 2026-07-11
"""

from collections.abc import Sequence

from alembic import op

revision: str = "c8a4e1f6d050"
down_revision: str | None = "b7f3d0e5c940"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_webhook_events_source_external_id",
        "webhook_events",
        ["source", "external_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_webhook_events_source_external_id",
        "webhook_events",
        type_="unique",
    )
