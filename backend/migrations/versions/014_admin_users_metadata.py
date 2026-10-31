"""Add admin-safe user metadata and admin access audit action for SPEC-011."""

import sqlalchemy as sa
from alembic import op

revision = "014_admin_users_metadata"
down_revision = "013_usage_events_audit_logs"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.add_column(
        "users",
        sa.Column("account_status", sa.String(20), server_default="active", nullable=False),
    )
    op.create_check_constraint("valid_user_account_status", "users", "account_status = 'active'")
    op.drop_constraint("valid_audit_action", "audit_logs", type_="check")
    op.create_check_constraint(
        "valid_audit_action",
        "audit_logs",
        "action IN ('password_changed', 'sessions_revoked', 'account_deleted', "
        "'admin_users_listed')",
    )


def downgrade():
    op.drop_constraint("valid_audit_action", "audit_logs", type_="check")
    op.create_check_constraint(
        "valid_audit_action",
        "audit_logs",
        "action IN ('password_changed', 'sessions_revoked', 'account_deleted')",
    )
    op.drop_constraint("valid_user_account_status", "users", type_="check")
    op.drop_column("users", "account_status")
    op.drop_column("users", "created_at")
