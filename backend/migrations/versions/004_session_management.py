"""Add creation instant to sessions so owners can manage their devices safely."""

import sqlalchemy as sa
from alembic import op

revision = "004_session_management"
down_revision = "003_email_confirmation"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "auth_sessions",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index("ix_auth_sessions_user_created", "auth_sessions", ["user_id", "created_at"])


def downgrade():
    op.drop_index("ix_auth_sessions_user_created", table_name="auth_sessions")
    op.drop_column("auth_sessions", "created_at")
