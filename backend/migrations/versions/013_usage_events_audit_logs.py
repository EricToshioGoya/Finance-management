"""Add minimal use events and protected operational audit records for SPEC-060."""

import sqlalchemy as sa
from alembic import op

revision = "013_usage_events_audit_logs"
down_revision = "012_simulations_indicators_goals"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "usage_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("module", sa.String(20), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint(
            "module IN ('dashboard', 'simulator', 'financial', 'profile')",
            name="valid_usage_event_module",
        ),
        sa.CheckConstraint("action IN ('opened', 'viewed')", name="valid_usage_event_action"),
    )
    op.create_index("ix_usage_events_user_id", "usage_events", ["user_id"])
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint(
            "action IN ('password_changed', 'sessions_revoked', 'account_deleted')",
            name="valid_audit_action",
        ),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])


def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("usage_events")
