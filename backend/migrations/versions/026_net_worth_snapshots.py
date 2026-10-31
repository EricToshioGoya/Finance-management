"""Persist real monthly net-worth snapshots for SPEC-029."""

import sqlalchemy as sa
from alembic import op

revision = "026_net_worth_snapshots"
down_revision = "025_watchlist"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "net_worth_snapshots",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("competence", sa.Date(), nullable=False),
        sa.Column("total_assets", sa.Numeric(16, 2), nullable=False),
        sa.Column("total_liabilities", sa.Numeric(16, 2), nullable=False),
        sa.Column("net_worth", sa.Numeric(16, 2), nullable=False),
        sa.Column(
            "captured_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "competence", name="uq_net_worth_snapshot_month"),
        sa.CheckConstraint("total_liabilities >= 0", name="nonnegative_snapshot_liabilities"),
        sa.CheckConstraint(
            "net_worth = total_assets - total_liabilities",
            name="consistent_snapshot_net_worth",
        ),
    )
    op.create_index("ix_net_worth_snapshots_user_id", "net_worth_snapshots", ["user_id"])


def downgrade():
    op.drop_index("ix_net_worth_snapshots_user_id", table_name="net_worth_snapshots")
    op.drop_table("net_worth_snapshots")
