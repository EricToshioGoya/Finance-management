import sqlalchemy as sa
from alembic import op

revision = "031_webhook_subscriptions"
down_revision = "030_external_api_keys"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "webhook_subscriptions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("url_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("secret_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("disabled_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_webhook_subscriptions_user_id", "webhook_subscriptions", ["user_id"])
    op.create_table(
        "webhook_attempts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "subscription_id",
            sa.Uuid(),
            sa.ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("event_type", sa.String(60), nullable=False),
        sa.Column("payload_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("outcome", sa.String(12), nullable=False),
        sa.Column("status_code", sa.Integer()),
        sa.Column("failure_code", sa.String(40)),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "retry_of_id", sa.Uuid(), sa.ForeignKey("webhook_attempts.id", ondelete="SET NULL")
        ),
        sa.CheckConstraint(
            "outcome IN ('succeeded', 'failed')", name="valid_webhook_attempt_outcome"
        ),
    )
    op.create_index("ix_webhook_attempts_subscription_id", "webhook_attempts", ["subscription_id"])
    op.create_index("ix_webhook_attempts_user_id", "webhook_attempts", ["user_id"])


def downgrade():
    op.drop_index("ix_webhook_attempts_user_id", table_name="webhook_attempts")
    op.drop_index("ix_webhook_attempts_subscription_id", table_name="webhook_attempts")
    op.drop_table("webhook_attempts")
    op.drop_index("ix_webhook_subscriptions_user_id", table_name="webhook_subscriptions")
    op.drop_table("webhook_subscriptions")
