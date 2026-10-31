"""Add indicator cache, simulations and budget goals for Specs 004/007-010/013/021-024."""

import sqlalchemy as sa
from alembic import op

revision = "012_simulations_indicators_goals"
down_revision = "011_expenses"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "market_indicators",
        sa.Column("code", sa.String(10), primary_key=True),
        sa.Column("value", sa.Numeric(14, 6), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("reference_date", sa.Date(), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(120), nullable=False),
        sa.CheckConstraint("code IN ('selic', 'cdi', 'ipca')", name="valid_indicator_code"),
    )
    op.create_table(
        "simulations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("label_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("final_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.CheckConstraint(
            "kind IN ('fixed_income', 'variable_income')", name="valid_simulation_kind"
        ),
    )
    op.create_index("ix_simulations_user_id", "simulations", ["user_id"])
    op.create_table(
        "budget_goals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("category_key", sa.String(80)),
        sa.Column("target", sa.Numeric(14, 2), nullable=False),
        sa.Column("alert_threshold", sa.Numeric(5, 2), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.CheckConstraint("target > 0", name="positive_budget_goal"),
        sa.CheckConstraint(
            "kind IN ('expense_total', 'income_total', 'category_expense')",
            name="valid_budget_goal_kind",
        ),
        sa.CheckConstraint(
            "(kind = 'category_expense' AND category_key IS NOT NULL) OR "
            "(kind <> 'category_expense' AND category_key IS NULL)",
            name="valid_budget_goal_category",
        ),
        sa.CheckConstraint(
            "alert_threshold >= 70 AND alert_threshold <= 100", name="valid_budget_alert_threshold"
        ),
    )
    op.create_index("ix_budget_goals_user_id", "budget_goals", ["user_id"])


def downgrade():
    op.drop_table("budget_goals")
    op.drop_table("simulations")
    op.drop_table("market_indicators")
