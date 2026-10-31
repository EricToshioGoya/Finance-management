"""Add one-time income and bonus/PLR records.

Revision ID: 010_variable_income_bonus
Revises: 009_recurring_income
"""

import sqlalchemy as sa
from alembic import op

revision = "010_variable_income_bonus"
down_revision = "009_recurring_income"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "one_time_incomes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=True),
        sa.Column("description_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.CheckConstraint("amount > 0", name="positive_one_time_income"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_one_time_income_owner_key"),
    )
    op.create_index("ix_one_time_incomes_user_id", "one_time_incomes", ["user_id"])
    op.create_table(
        "bonuses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("description_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("periodicity", sa.String(10), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("reference_month", sa.Integer(), nullable=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.CheckConstraint("amount >= 0", name="nonnegative_bonus"),
        sa.CheckConstraint("periodicity IN ('monthly', 'annual')", name="valid_bonus_periodicity"),
        sa.CheckConstraint(
            "(periodicity = 'monthly' AND reference_month IS NULL) OR "
            "(periodicity = 'annual' AND reference_month BETWEEN 1 AND 12)",
            name="valid_bonus_reference_month",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_bonus_owner_key"),
    )
    op.create_index("ix_bonuses_user_id", "bonuses", ["user_id"])


def downgrade():
    op.drop_table("bonuses")
    op.drop_table("one_time_incomes")
