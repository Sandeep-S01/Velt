"""Harden store indexing state defaults.

Revision ID: f0a2c4e6b810
Revises: d9b5f2a7e160
"""

from alembic import op
import sqlalchemy as sa


revision: str = "f0a2c4e6b810"
down_revision: str | None = "d9b5f2a7e160"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE stores SET index_status = 'pending' WHERE index_status IS NULL")
    op.execute("UPDATE stores SET index_progress_percent = 0 WHERE index_progress_percent IS NULL")
    op.execute("UPDATE stores SET total_product_count = 0 WHERE total_product_count IS NULL")
    op.execute("UPDATE stores SET indexed_product_count = 0 WHERE indexed_product_count IS NULL")

    op.alter_column(
        "stores",
        "index_status",
        existing_type=sa.String(),
        nullable=False,
        server_default="pending",
    )
    for column_name in (
        "index_progress_percent",
        "total_product_count",
        "indexed_product_count",
    ):
        op.alter_column(
            "stores",
            column_name,
            existing_type=sa.Integer(),
            nullable=False,
            server_default="0",
        )


def downgrade() -> None:
    for column_name in (
        "indexed_product_count",
        "total_product_count",
        "index_progress_percent",
    ):
        op.alter_column(
            "stores",
            column_name,
            existing_type=sa.Integer(),
            nullable=True,
            server_default=None,
        )
    op.alter_column(
        "stores",
        "index_status",
        existing_type=sa.String(),
        nullable=True,
        server_default=None,
    )
