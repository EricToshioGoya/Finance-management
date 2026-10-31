"""Identity, revocable sessions, rotating refresh and shared rate limits."""

import sqlalchemy as sa
from alembic import op

revision = "001_identity"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("email_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("email_lookup", sa.String(64), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.CheckConstraint("role IN ('usuario', 'administrador')", name="valid_user_role"),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("digest", sa.String(64), primary_key=True),
        sa.Column(
            "session_id",
            sa.Uuid(),
            sa.ForeignKey("auth_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("used", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_refresh_tokens_session_id", "refresh_tokens", ["session_id"])
    op.create_table(
        "auth_rate_buckets",
        sa.Column("client_endpoint", sa.String(64), primary_key=True),
        sa.Column("window", sa.Integer(), primary_key=True),
        sa.Column("count", sa.Integer(), nullable=False),
    )


def downgrade():
    for name in ("auth_rate_buckets", "refresh_tokens", "auth_sessions", "users"):
        op.drop_table(name)
