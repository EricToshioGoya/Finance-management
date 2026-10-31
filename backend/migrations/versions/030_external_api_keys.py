"""SPEC-041: external credential grants, never store the raw secret."""

import sqlalchemy as sa
from alembic import op

revision = "030_external_api_keys"
down_revision = "029_confirmed_financings"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "external_api_keys",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("key_digest", sa.String(64), unique=True, nullable=False),
        sa.Column("scopes", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("window_started_at", sa.DateTime(timezone=True)),
        sa.Column("request_count", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint("request_count >= 0", name="nonnegative_external_api_count"),
    )
    op.create_index("ix_external_api_keys_user_id", "external_api_keys", ["user_id"])


def downgrade():
    op.drop_index("ix_external_api_keys_user_id", table_name="external_api_keys")
    op.drop_table("external_api_keys")
