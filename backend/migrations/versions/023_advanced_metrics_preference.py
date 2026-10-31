"""Persist manual access to advanced historical metrics for SPEC-025."""

import sqlalchemy as sa
from alembic import op

revision = "023_advanced_metrics_preference"
down_revision = "022_notification_center"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "advanced_metrics_preferences",
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade():
    op.drop_table("advanced_metrics_preferences")
