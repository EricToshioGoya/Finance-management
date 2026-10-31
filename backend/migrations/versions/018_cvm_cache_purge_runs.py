"""Persist aggregated execution evidence for automatic CVM cache expiry (SPEC-054)."""

import sqlalchemy as sa
from alembic import op

revision = "018_cvm_cache_purge_runs"
down_revision = "017_cvm_financial_indicators"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cvm_cache_purge_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("documents_expunged", sa.Integer(), nullable=False),
        sa.Column("indicators_expunged", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(12), nullable=False),
        sa.CheckConstraint("status = 'completed'", name="valid_cvm_purge_status"),
    )


def downgrade():
    op.drop_table("cvm_cache_purge_runs")
