"""SPEC-061/040: dispositivos push, tentativas de entrega externa e resumo mensal."""

import sqlalchemy as sa
from alembic import op

revision = "035_channels_and_monthly_summary"
down_revision = "034_engagement_features"
branch_labels = None
depends_on = None

STATUS = "status IN ('sent', 'failed', 'provider_unavailable', 'no_destination')"


def user_fk():
    return sa.ForeignKey("users.id", ondelete="CASCADE")


def upgrade():
    op.create_table(
        "push_devices",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), user_fk(), nullable=False),
        sa.Column("token_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("token_lookup", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "token_lookup", name="uq_push_device_token"),
    )
    op.create_index("ix_push_devices_user_id", "push_devices", ["user_id"])
    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), user_fk(), nullable=False),
        sa.Column(
            "notification_id", sa.Uuid(), sa.ForeignKey("notifications.id", ondelete="CASCADE")
        ),
        sa.Column("source", sa.String(40), nullable=False),
        sa.Column("channel", sa.String(10), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("channel IN ('email', 'push')", name="valid_delivery_channel"),
        sa.CheckConstraint(STATUS, name="valid_delivery_status"),
    )
    op.create_index("ix_notification_deliveries_user_id", "notification_deliveries", ["user_id"])
    op.create_table(
        "report_settings",
        sa.Column("user_id", sa.Uuid(), user_fk(), primary_key=True),
        sa.Column("monthly_summary_enabled", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "monthly_summaries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), user_fk(), nullable=False),
        sa.Column("competence", sa.Date(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "competence", name="uq_monthly_summary"),
        sa.CheckConstraint(STATUS, name="valid_monthly_summary_status"),
    )
    op.create_index("ix_monthly_summaries_user_id", "monthly_summaries", ["user_id"])


def downgrade():
    op.drop_table("monthly_summaries")
    op.drop_table("report_settings")
    op.drop_table("notification_deliveries")
    op.drop_table("push_devices")
