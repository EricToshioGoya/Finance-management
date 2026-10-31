"""Persist owner-scoped manual real assets and liabilities for SPEC-028."""

import sqlalchemy as sa
from alembic import op

revision = "020_net_worth_items"
down_revision = "019_market_quote_reference"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "net_worth_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("kind", sa.String(12), nullable=False),
        sa.Column("name_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("value", sa.Numeric(14, 2), nullable=False),
        sa.Column("annual_rate", sa.Numeric(8, 4)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("kind IN ('asset', 'liability')", name="valid_net_worth_item_kind"),
        sa.CheckConstraint("value > 0", name="positive_net_worth_item_value"),
        sa.CheckConstraint(
            "annual_rate IS NULL OR annual_rate >= 0", name="nonnegative_net_worth_item_rate"
        ),
    )
    op.create_index("ix_net_worth_items_user_id", "net_worth_items", ["user_id"])


def downgrade():
    op.drop_index("ix_net_worth_items_user_id", table_name="net_worth_items")
    op.drop_table("net_worth_items")
