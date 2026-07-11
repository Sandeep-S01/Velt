"""Add store ownership, store-scoped product identity, and webhook events.

Revision ID: c3a7d9e2f401
Revises: 7dd933600ef3
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c3a7d9e2f401"
down_revision: str | None = "7dd933600ef3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("stores", sa.Column("owner_user_id", sa.String(), nullable=True))
    op.create_foreign_key(
        "fk_stores_owner_user_id_users",
        "stores",
        "users",
        ["owner_user_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_stores_owner_user_id", "stores", ["owner_user_id"])

    op.add_column("products", sa.Column("external_id", sa.String(), nullable=True))
    op.execute("UPDATE products SET external_id = id WHERE external_id IS NULL")
    op.alter_column("products", "external_id", nullable=False)
    op.create_unique_constraint(
        "uq_products_store_external_id",
        "products",
        ["store_id", "external_id"],
    )

    op.create_table(
        "webhook_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("store_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_webhook_events_id", "webhook_events", ["id"])
    op.create_index(
        "ix_webhook_events_store_created",
        "webhook_events",
        ["store_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_webhook_events_store_created", table_name="webhook_events")
    op.drop_index("ix_webhook_events_id", table_name="webhook_events")
    op.drop_table("webhook_events")

    op.drop_constraint("uq_products_store_external_id", "products", type_="unique")
    op.drop_column("products", "external_id")

    op.drop_index("ix_stores_owner_user_id", table_name="stores")
    op.drop_constraint("fk_stores_owner_user_id_users", "stores", type_="foreignkey")
    op.drop_column("stores", "owner_user_id")
