"""Store local PTAX references and allow SPEC-026 simulations."""

import sqlalchemy as sa
from alembic import op

revision = "024_foreign_currency"
down_revision = "023_advanced_metrics_preference"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "exchange_rates",
        sa.Column("currency", sa.String(length=3), primary_key=True),
        sa.Column("rate_to_brl", sa.Numeric(14, 6), nullable=False),
        sa.Column("reference_date", sa.Date(), nullable=False),
        sa.Column("referenced_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_name", sa.String(length=120), nullable=False),
        sa.Column("availability", sa.String(length=20), nullable=False, server_default="available"),
        sa.CheckConstraint("currency IN ('USD', 'EUR')", name="valid_exchange_currency"),
        sa.CheckConstraint("rate_to_brl > 0", name="positive_exchange_rate"),
        sa.CheckConstraint(
            "availability IN ('available', 'unavailable')", name="valid_exchange_availability"
        ),
    )
    op.drop_constraint("valid_simulation_kind", "simulations", type_="check")
    op.create_check_constraint(
        "valid_simulation_kind",
        "simulations",
        "kind IN ('fixed_income', 'variable_income', 'foreign_currency')",
    )


def downgrade():
    op.drop_constraint("valid_simulation_kind", "simulations", type_="check")
    op.create_check_constraint(
        "valid_simulation_kind", "simulations", "kind IN ('fixed_income', 'variable_income')"
    )
    op.drop_table("exchange_rates")
