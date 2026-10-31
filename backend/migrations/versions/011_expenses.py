"""Add owned categorized expenses.

Revision ID: 011_expenses
Revises: 010_variable_income_bonus
"""

import sqlalchemy as sa
from alembic import op

revision = "011_expenses"
down_revision = "010_variable_income_bonus"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "expenses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=True),
        sa.Column("credit_card_id", sa.Uuid(), nullable=True),
        sa.Column("category_key", sa.String(80), nullable=False),
        sa.Column("description_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.Column("recurring", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.CheckConstraint("amount > 0", name="positive_expense"),
        sa.CheckConstraint(
            "(account_id IS NOT NULL) <> (credit_card_id IS NOT NULL)", name="one_expense_source"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["credit_card_id"], ["credit_cards.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_expense_owner_key"),
    )
    op.create_index("ix_expenses_user_id", "expenses", ["user_id"])


def downgrade():
    op.drop_table("expenses")
