"""SPEC-033: named goals linked to real manual assets."""

import sqlalchemy as sa
from alembic import op

revision = "028_named_asset_goals"
down_revision = "027_investment_allocation"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "named_asset_goals",
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
        sa.Column("name_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("target_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=False),
        sa.Column("annual_rate", sa.Numeric(10, 6), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("target_amount > 0", name="positive_named_asset_goal"),
        sa.CheckConstraint("annual_rate >= 0", name="nonnegative_named_goal_rate"),
    )
    op.create_index("ix_named_asset_goals_user_id", "named_asset_goals", ["user_id"])
    op.create_index("ix_named_asset_goals_asset_id", "named_asset_goals", ["asset_id"])


def downgrade():
    op.drop_index("ix_named_asset_goals_asset_id", table_name="named_asset_goals")
    op.drop_index("ix_named_asset_goals_user_id", table_name="named_asset_goals")
    op.drop_table("named_asset_goals")
