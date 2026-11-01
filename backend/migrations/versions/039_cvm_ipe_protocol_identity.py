"""OPEN-27 (2026-11-01): documento IPE identificado por protocolo de entrega + versão."""

import sqlalchemy as sa
from alembic import op

revision = "039_cvm_ipe_protocol_identity"
down_revision = "038_card_cycle_installments"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("official_documents", sa.Column("cvm_protocol", sa.String(40)))
    op.drop_constraint("uq_official_document_identity", "official_documents", type_="unique")
    op.create_index(
        "uq_official_document_identity",
        "official_documents",
        ["company_id", "document_type", "cvm_reference_date", "cvm_version"],
        unique=True,
        postgresql_where=sa.text("document_type <> 'IPE'"),
    )
    op.create_index(
        "uq_official_ipe_identity",
        "official_documents",
        ["company_id", "cvm_protocol", "cvm_version"],
        unique=True,
        postgresql_where=sa.text("document_type = 'IPE'"),
    )


def downgrade():
    op.drop_index("uq_official_ipe_identity", "official_documents")
    op.drop_index("uq_official_document_identity", "official_documents")
    op.create_unique_constraint(
        "uq_official_document_identity",
        "official_documents",
        ["company_id", "document_type", "cvm_reference_date", "cvm_version"],
    )
    op.drop_column("official_documents", "cvm_protocol")
