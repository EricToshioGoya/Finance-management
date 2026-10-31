"""Add owned accounts and credit cards.

Revision ID: 008_accounts_cards
Revises: 007_categories
"""

import sqlalchemy as sa
from alembic import op

revision = "008_accounts_cards"
down_revision = "007_categories"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("initial_balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("account_type", sa.String(20), nullable=False),
        sa.CheckConstraint(
            "account_type IN ('checking', 'savings', 'cash', 'investment')",
            name="valid_account_type",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_accounts_user_id", "accounts", ["user_id"])
    op.create_table(
        "credit_cards",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("credit_limit", sa.Numeric(14, 2), nullable=False),
        sa.Column("closing_day", sa.Integer(), nullable=False),
        sa.Column("due_day", sa.Integer(), nullable=False),
        sa.CheckConstraint("credit_limit > 0", name="positive_credit_limit"),
        sa.CheckConstraint("closing_day BETWEEN 1 AND 31", name="valid_closing_day"),
        sa.CheckConstraint("due_day BETWEEN 1 AND 31", name="valid_due_day"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_credit_cards_user_id", "credit_cards", ["user_id"])


def downgrade():
    op.drop_table("credit_cards")
    op.drop_table("accounts")
