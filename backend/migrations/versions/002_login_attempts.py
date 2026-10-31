"""Shared account login lock, including nonexistent normalized addresses."""

import sqlalchemy as sa
from alembic import op

revision = "002_login_attempts"
down_revision = "001_identity"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auth_login_attempts",
        sa.Column("email_key", sa.String(64), primary_key=True),
        sa.Column("failures", sa.Integer(), nullable=False),
        sa.Column("blocked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("touched_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("failures >= 0 AND failures <= 5", name="valid_failures"),
    )
    op.create_index("ix_auth_login_attempts_touched_at", "auth_login_attempts", ["touched_at"])


def downgrade():
    op.drop_table("auth_login_attempts")
