"""SPEC-031: owner-scoped investment classifications and allocation targets."""

import sqlalchemy as sa
from alembic import op

revision = "027_investment_allocation"
down_revision = "026_net_worth_snapshots"
branch_labels = None
depends_on = None

CLASSES = "'fixed_income', 'stocks', 'fiis', 'savings', 'other'"


def upgrade():
    op.create_table(
        "investment_asset_classes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "asset_id",
            sa.Uuid(),
            sa.ForeignKey("net_worth_items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("asset_class", sa.String(20), nullable=False),
        sa.UniqueConstraint("user_id", "asset_id", name="uq_investment_asset_class_owner"),
        sa.CheckConstraint(
            "asset_class IN ('fixed_income', 'stocks', 'fiis', 'savings', 'other')",
            name="valid_investment_asset_class",
        ),
    )
    op.create_index("ix_investment_asset_classes_user_id", "investment_asset_classes", ["user_id"])
    op.create_table(
        "investment_allocation_targets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("asset_class", sa.String(20), nullable=False),
        sa.Column("target_percent", sa.Numeric(5, 2), nullable=False),
        sa.UniqueConstraint("user_id", "asset_class", name="uq_allocation_target_owner_class"),
        sa.CheckConstraint(
            "asset_class IN ('fixed_income', 'stocks', 'fiis', 'savings', 'other')",
            name="valid_allocation_target_class",
        ),
        sa.CheckConstraint(
            "target_percent >= 0 AND target_percent <= 100", name="target_pct_range"
        ),
    )
    op.create_index(
        "ix_investment_allocation_targets_user_id", "investment_allocation_targets", ["user_id"]
    )


def downgrade():
    op.drop_index(
        "ix_investment_allocation_targets_user_id",
        table_name="investment_allocation_targets",
    )
    op.drop_table("investment_allocation_targets")
    op.drop_index("ix_investment_asset_classes_user_id", table_name="investment_asset_classes")
    op.drop_table("investment_asset_classes")
