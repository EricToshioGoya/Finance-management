"""SPEC-007-R04 / ADR-009: cache local das taxas de compra do Tesouro Direto."""

import sqlalchemy as sa
from alembic import op

revision = "036_treasury_bond_rates"
down_revision = "035_channels_and_monthly_summary"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "treasury_bond_rates",
        sa.Column("bond_type", sa.String(80), primary_key=True),
        sa.Column("maturity", sa.Date(), primary_key=True),
        sa.Column("buy_rate", sa.Numeric(10, 4), nullable=False),
        sa.Column("reference_date", sa.Date(), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(120), nullable=False),
        sa.CheckConstraint("buy_rate > 0", name="positive_treasury_rate"),
    )


def downgrade():
    op.drop_table("treasury_bond_rates")
