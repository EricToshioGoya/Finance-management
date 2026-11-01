"""OPEN-12 (2026-10-31): alerta de limite configurável por cartão e compras parceladas."""

import sqlalchemy as sa
from alembic import op

revision = "038_card_cycle_installments"
down_revision = "037_cvm_document_identity"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "credit_cards",
        sa.Column("alert_threshold", sa.Numeric(5, 2), nullable=False, server_default="80"),
    )
    op.create_check_constraint(
        "valid_card_alert_threshold", "credit_cards", "alert_threshold BETWEEN 70 AND 100"
    )
    op.add_column("expenses", sa.Column("installment_group", sa.Uuid()))
    op.add_column("expenses", sa.Column("installment_number", sa.Integer()))
    op.add_column("expenses", sa.Column("installment_count", sa.Integer()))
    op.create_check_constraint(
        "valid_expense_installment",
        "expenses",
        "(installment_group IS NULL AND installment_number IS NULL AND installment_count IS NULL)"
        " OR (installment_group IS NOT NULL AND credit_card_id IS NOT NULL AND NOT recurring"
        " AND installment_count BETWEEN 2 AND 48"
        " AND installment_number BETWEEN 1 AND installment_count)",
    )
    op.create_index("ix_expenses_installment_group", "expenses", ["installment_group"])


def downgrade():
    op.drop_index("ix_expenses_installment_group", "expenses")
    op.drop_constraint("valid_expense_installment", "expenses", type_="check")
    op.drop_column("expenses", "installment_count")
    op.drop_column("expenses", "installment_number")
    op.drop_column("expenses", "installment_group")
    op.drop_constraint("valid_card_alert_threshold", "credit_cards", type_="check")
    op.drop_column("credit_cards", "alert_threshold")
