"""OPEN-27 / ADR-009: identidade de documento CVM (empresa + tipo + referência + versão)."""

import sqlalchemy as sa
from alembic import op

revision = "037_cvm_document_identity"
down_revision = "036_treasury_bond_rates"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("official_documents", sa.Column("cvm_reference_date", sa.Date()))
    op.add_column("official_documents", sa.Column("cvm_version", sa.Integer()))
    op.create_unique_constraint(
        "uq_official_document_identity",
        "official_documents",
        ["company_id", "document_type", "cvm_reference_date", "cvm_version"],
    )


def downgrade():
    op.drop_constraint("uq_official_document_identity", "official_documents", type_="unique")
    op.drop_column("official_documents", "cvm_version")
    op.drop_column("official_documents", "cvm_reference_date")
