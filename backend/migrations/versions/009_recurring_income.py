"""Add idempotent recurring income sources.

Revision ID: 009_recurring_income
Revises: 008_accounts_cards
"""

import sqlalchemy as sa
from alembic import op

revision = "009_recurring_income"
down_revision = "008_accounts_cards"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "recurring_incomes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=True),
        sa.Column("description_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.CheckConstraint("amount > 0", name="positive_recurring_income"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_recurring_income_owner_key"),
    )
    op.create_index("ix_recurring_incomes_user_id", "recurring_incomes", ["user_id"])


def downgrade():
    op.drop_table("recurring_incomes")
