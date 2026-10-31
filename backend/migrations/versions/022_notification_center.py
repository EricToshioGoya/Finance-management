"""Persist owner-only in-app notifications and granular opt-outs for SPEC-039."""

import sqlalchemy as sa
from alembic import op

revision = "022_notification_center"
down_revision = "021_health_scores"
branch_labels = None
depends_on = None

KINDS = "'invoice_due', 'budget_goal_exceeded', 'watchlist_document', 'recurring_expense_due'"


def upgrade():
    op.create_table(
        "notification_preferences",
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column("kind", sa.String(40), primary_key=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.CheckConstraint(f"kind IN ({KINDS})", name="valid_notification_preference_kind"),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("source_key", sa.String(128), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("message", sa.String(280), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(f"kind IN ({KINDS})", name="valid_notification_kind"),
        sa.UniqueConstraint("user_id", "kind", "source_key", name="uq_notification_event"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade():
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_table("notification_preferences")
