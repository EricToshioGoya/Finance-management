"""Persist configurable educational health-score weights and monthly history (SPEC-034)."""

import sqlalchemy as sa
from alembic import op

revision = "021_health_scores"
down_revision = "020_net_worth_items"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "health_score_rules",
        sa.Column("key", sa.String(20), primary_key=True),
        sa.Column("spending_weight", sa.Numeric(5, 2), nullable=False),
        sa.Column("reserve_weight", sa.Numeric(5, 2), nullable=False),
        sa.Column("debt_weight", sa.Numeric(5, 2), nullable=False),
        sa.Column("goals_weight", sa.Numeric(5, 2), nullable=False),
        sa.Column("version", sa.String(30), nullable=False),
    )
    op.bulk_insert(
        sa.table(
            "health_score_rules",
            sa.column("key", sa.String()),
            sa.column("spending_weight", sa.Numeric()),
            sa.column("reserve_weight", sa.Numeric()),
            sa.column("debt_weight", sa.Numeric()),
            sa.column("goals_weight", sa.Numeric()),
            sa.column("version", sa.String()),
        ),
        [
            {
                "key": "default",
                "spending_weight": "35",
                "reserve_weight": "25",
                "debt_weight": "25",
                "goals_weight": "15",
                "version": "2026-10-local-v1",
            }
        ],
    )
    op.create_table(
        "health_scores",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("competence", sa.Date(), nullable=False),
        sa.Column("score", sa.Numeric(5, 2), nullable=False),
        sa.Column("classification", sa.String(20), nullable=False),
        sa.Column("factors", sa.JSON(), nullable=False),
        sa.Column("rule_version", sa.String(30), nullable=False),
        sa.UniqueConstraint("user_id", "competence", name="uq_health_score_month"),
    )
    op.create_index("ix_health_scores_user_id", "health_scores", ["user_id"])


def downgrade():
    op.drop_index("ix_health_scores_user_id", table_name="health_scores")
    op.drop_table("health_scores")
    op.drop_table("health_score_rules")
