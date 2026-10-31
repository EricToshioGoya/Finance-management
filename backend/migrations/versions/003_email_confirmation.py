"""Pending/verified address state and one-time confirmation digests."""

import sqlalchemy as sa
from alembic import op

revision = "003_email_confirmation"
down_revision = "002_login_attempts"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users", sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_table(
        "email_confirmation_tokens",
        sa.Column("digest", sa.String(64), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("purpose", sa.String(40), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "purpose = 'email_confirmation'", name="valid_email_confirmation_purpose"
        ),
    )
    op.create_index(
        "ix_email_confirmation_tokens_user_id", "email_confirmation_tokens", ["user_id"]
    )
    op.create_index(
        "ix_email_confirmation_tokens_expires_at", "email_confirmation_tokens", ["expires_at"]
    )


def downgrade():
    op.drop_table("email_confirmation_tokens")
    op.drop_column("users", "email_verified_at")
