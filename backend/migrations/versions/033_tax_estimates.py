"""SPEC-048/049: estimativas de IR do titular para lembrete de DARF e resumo anual."""

import sqlalchemy as sa
from alembic import op

revision = "033_tax_estimates"
down_revision = "032_shared_accounts"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tax_estimates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("regime", sa.String(12), nullable=False),
        sa.Column("competence", sa.Date(), nullable=False),
        sa.Column("sales", sa.Numeric(14, 2), nullable=False),
        sa.Column("result", sa.Numeric(14, 2), nullable=False),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False),
        sa.Column("tax", sa.Numeric(14, 2), nullable=False),
        sa.Column("exempt", sa.Boolean(), nullable=False),
        sa.Column("darf_due_on", sa.Date()),
        sa.Column("rule_version", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "regime IN ('fixed_income', 'stock', 'fii', 'day_trade')", name="valid_tax_regime"
        ),
    )
    op.create_index("ix_tax_estimates_user_id", "tax_estimates", ["user_id"])


def downgrade():
    op.drop_table("tax_estimates")
