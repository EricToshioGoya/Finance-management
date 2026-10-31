"""SPEC-038: independently owned, immutable financing origin and optional expense."""

import sqlalchemy as sa
from alembic import op

revision = "029_confirmed_financings"
down_revision = "028_named_asset_goals"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "confirmed_financings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("principal", sa.Numeric(14, 2), nullable=False),
        sa.Column("asset_value", sa.Numeric(14, 2), nullable=False),
        sa.Column("down_payment", sa.Numeric(14, 2), nullable=False),
        sa.Column("installments", sa.Integer(), nullable=False),
        sa.Column("annual_rate", sa.Numeric(9, 6), nullable=False),
        sa.Column("installment_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("first_payment_on", sa.Date(), nullable=True),
        sa.Column("expense_id", sa.Uuid(), sa.ForeignKey("expenses.id", ondelete="RESTRICT")),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("request_digest", sa.String(64), nullable=False),
        sa.Column(
            "confirmed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("user_id", "idempotency_key", name="uq_financing_user_request"),
        sa.CheckConstraint("principal > 0", name="positive_confirmed_financing_principal"),
    )
    op.create_index("ix_confirmed_financings_user_id", "confirmed_financings", ["user_id"])


def downgrade():
    op.drop_index("ix_confirmed_financings_user_id", table_name="confirmed_financings")
    op.drop_table("confirmed_financings")
