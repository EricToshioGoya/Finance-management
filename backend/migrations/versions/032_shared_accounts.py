"""SPEC-044/045: vínculo entre usuários, despesas compartilhadas e acertos."""

import sqlalchemy as sa
from alembic import op

revision = "032_shared_accounts"
down_revision = "031_webhook_subscriptions"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "shared_links",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "inviter_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "invitee_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("responded_at", sa.DateTime(timezone=True)),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("inviter_id <> invitee_id", name="distinct_shared_members"),
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'declined', 'cancelled', 'expired', 'ended')",
            name="valid_shared_link_status",
        ),
    )
    op.create_index("ix_shared_links_inviter_id", "shared_links", ["inviter_id"])
    op.create_index("ix_shared_links_invitee_id", "shared_links", ["invitee_id"])
    op.create_table(
        "shared_expenses",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "link_id",
            sa.Uuid(),
            sa.ForeignKey("shared_links.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "expense_id",
            sa.Uuid(),
            sa.ForeignKey("expenses.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "payer_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("payer_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "payer_percent > 0 AND payer_percent < 100", name="valid_shared_payer_percent"
        ),
    )
    op.create_index("ix_shared_expenses_link_id", "shared_expenses", ["link_id"])
    op.create_table(
        "shared_settlements",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "link_id",
            sa.Uuid(),
            sa.ForeignKey("shared_links.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "payer_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "receiver_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount > 0", name="positive_settlement"),
        sa.UniqueConstraint(
            "link_id", "payer_id", "idempotency_key", name="uq_settlement_idempotency"
        ),
    )
    op.create_index("ix_shared_settlements_link_id", "shared_settlements", ["link_id"])


def downgrade():
    op.drop_table("shared_settlements")
    op.drop_table("shared_expenses")
    op.drop_table("shared_links")
