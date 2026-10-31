"""Persist profile email-pending state and user presentation preferences."""

import sqlalchemy as sa
from alembic import op

revision = "005_profile_preferences"
down_revision = "004_session_management"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("pending_email_encrypted", sa.LargeBinary(), nullable=True))
    op.add_column("users", sa.Column("pending_email_lookup", sa.String(length=64), nullable=True))
    op.create_unique_constraint("uq_users_pending_email_lookup", "users", ["pending_email_lookup"])
    op.drop_constraint(
        "valid_email_confirmation_purpose", "email_confirmation_tokens", type_="check"
    )
    op.create_check_constraint(
        "valid_email_confirmation_purpose",
        "email_confirmation_tokens",
        "purpose IN ('email_confirmation', 'email_change')",
    )
    op.create_table(
        "user_preferences",
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column("language", sa.String(length=2), nullable=False, server_default="pt"),
        sa.Column("theme", sa.String(length=10), nullable=False, server_default="light"),
        sa.Column("in_app_notifications", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_notifications", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("push_notifications", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.CheckConstraint("language IN ('pt', 'en')", name="valid_preference_language"),
        sa.CheckConstraint("theme IN ('light', 'dark')", name="valid_preference_theme"),
    )


def downgrade():
    op.drop_table("user_preferences")
    op.drop_constraint(
        "valid_email_confirmation_purpose",
        "email_confirmation_tokens",
        type_="check",
    )
    op.create_check_constraint(
        "valid_email_confirmation_purpose",
        "email_confirmation_tokens",
        "purpose = 'email_confirmation'",
    )
    op.drop_constraint("uq_users_pending_email_lookup", "users", type_="unique")
    op.drop_column("users", "pending_email_lookup")
    op.drop_column("users", "pending_email_encrypted")
