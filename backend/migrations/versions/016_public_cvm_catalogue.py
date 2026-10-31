"""Create the local, metadata-only CVM catalogue for SPEC-012."""

from datetime import UTC, date, datetime

import sqlalchemy as sa
from alembic import op

revision = "016_public_cvm_catalogue"
down_revision = "015_investor_profile_quiz"
branch_labels = None
depends_on = None

PETR4 = "11111111-1111-1111-1111-111111111111"
VALE3 = "22222222-2222-2222-2222-222222222222"


def upgrade():
    op.create_table(
        "public_companies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("ticker", sa.String(12), nullable=False, unique=True),
        sa.Column("cnpj", sa.String(18), nullable=False, unique=True),
        sa.Column("legal_name", sa.String(180), nullable=False),
        sa.Column("sector", sa.String(100), nullable=False),
    )
    op.create_index("ix_public_companies_ticker", "public_companies", ["ticker"])
    op.create_index("ix_public_companies_cnpj", "public_companies", ["cnpj"])
    op.create_index("ix_public_companies_legal_name", "public_companies", ["legal_name"])
    op.create_table(
        "official_documents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Uuid(),
            sa.ForeignKey("public_companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("document_type", sa.String(8), nullable=False),
        sa.Column("subject", sa.String(180), nullable=False),
        sa.Column("reference_period", sa.String(80), nullable=False),
        sa.Column("delivered_at", sa.Date(), nullable=False),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column("official_url", sa.String(1000), nullable=False),
        sa.Column("link_status", sa.String(12), nullable=False, server_default="unchecked"),
        sa.Column("last_checked_at", sa.DateTime(timezone=True)),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "document_type IN ('DFP', 'ITR', 'FRE', 'IPE')", name="valid_document_type"
        ),
        sa.CheckConstraint(
            "status IN ('active', 'restated', 'replaced')", name="valid_official_document_status"
        ),
        sa.CheckConstraint(
            "link_status IN ('unchecked', 'available', 'broken')", name="valid_official_link_status"
        ),
    )
    op.create_index("ix_official_documents_company_id", "official_documents", ["company_id"])

    companies = sa.table(
        "public_companies",
        sa.column("id", sa.Uuid()),
        sa.column("ticker", sa.String()),
        sa.column("cnpj", sa.String()),
        sa.column("legal_name", sa.String()),
        sa.column("sector", sa.String()),
    )
    documents = sa.table(
        "official_documents",
        sa.column("id", sa.Uuid()),
        sa.column("company_id", sa.Uuid()),
        sa.column("document_type", sa.String()),
        sa.column("subject", sa.String()),
        sa.column("reference_period", sa.String()),
        sa.column("delivered_at", sa.Date()),
        sa.column("status", sa.String()),
        sa.column("official_url", sa.String()),
        sa.column("link_status", sa.String()),
        sa.column("synced_at", sa.DateTime(timezone=True)),
    )
    now = datetime(2026, 10, 28, tzinfo=UTC)
    op.bulk_insert(
        companies,
        [
            {
                "id": PETR4,
                "ticker": "PETR4",
                "cnpj": "33.000.167/0001-01",
                "legal_name": "PETRÓLEO BRASILEIRO S.A. - PETROBRAS",
                "sector": "Petróleo, Gás e Biocombustíveis",
            },
            {
                "id": VALE3,
                "ticker": "VALE3",
                "cnpj": "33.592.510/0001-54",
                "legal_name": "VALE S.A.",
                "sector": "Mineração",
            },
        ],
    )
    rad = "https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx"
    op.bulk_insert(
        documents,
        [
            {
                "id": "11111111-1111-1111-1111-111111111201",
                "company_id": PETR4,
                "document_type": "DFP",
                "subject": "Demonstrações Financeiras Padronizadas",
                "reference_period": "Exercício 2025",
                "delivered_at": date(2026, 2, 26),
                "status": "active",
                "official_url": f"{rad}?CNPJ=33000167000101",
                "link_status": "unchecked",
                "synced_at": now,
            },
            {
                "id": "11111111-1111-1111-1111-111111111202",
                "company_id": PETR4,
                "document_type": "ITR",
                "subject": "Informações Trimestrais",
                "reference_period": "2º trimestre de 2026",
                "delivered_at": date(2026, 8, 7),
                "status": "active",
                "official_url": f"{rad}?CNPJ=33000167000101",
                "link_status": "unchecked",
                "synced_at": now,
            },
            {
                "id": "11111111-1111-1111-1111-111111111203",
                "company_id": PETR4,
                "document_type": "FRE",
                "subject": "Formulário de Referência",
                "reference_period": "2026",
                "delivered_at": date(2026, 6, 30),
                "status": "active",
                "official_url": f"{rad}?CNPJ=33000167000101",
                "link_status": "unchecked",
                "synced_at": now,
            },
            {
                "id": "11111111-1111-1111-1111-111111111204",
                "company_id": PETR4,
                "document_type": "IPE",
                "subject": "Fato Relevante",
                "reference_period": "Outubro de 2026",
                "delivered_at": date(2026, 10, 20),
                "status": "active",
                "official_url": f"{rad}?CNPJ=33000167000101",
                "link_status": "unchecked",
                "synced_at": now,
            },
            {
                "id": "22222222-2222-2222-2222-222222222201",
                "company_id": VALE3,
                "document_type": "DFP",
                "subject": "Demonstrações Financeiras Padronizadas",
                "reference_period": "Exercício 2025",
                "delivered_at": date(2026, 2, 20),
                "status": "active",
                "official_url": f"{rad}?CNPJ=33592510000154",
                "link_status": "unchecked",
                "synced_at": now,
            },
            {
                "id": "22222222-2222-2222-2222-222222222202",
                "company_id": VALE3,
                "document_type": "ITR",
                "subject": "Informações Trimestrais",
                "reference_period": "2º trimestre de 2026",
                "delivered_at": date(2026, 8, 1),
                "status": "restated",
                "official_url": f"{rad}?CNPJ=33592510000154",
                "link_status": "unchecked",
                "synced_at": now,
            },
            {
                "id": "22222222-2222-2222-2222-222222222203",
                "company_id": VALE3,
                "document_type": "FRE",
                "subject": "Formulário de Referência",
                "reference_period": "2026",
                "delivered_at": date(2026, 6, 27),
                "status": "active",
                "official_url": f"{rad}?CNPJ=33592510000154",
                "link_status": "unchecked",
                "synced_at": now,
            },
            {
                "id": "22222222-2222-2222-2222-222222222204",
                "company_id": VALE3,
                "document_type": "IPE",
                "subject": "Comunicado ao Mercado",
                "reference_period": "Outubro de 2026",
                "delivered_at": date(2026, 10, 18),
                "status": "active",
                "official_url": f"{rad}?CNPJ=33592510000154",
                "link_status": "unchecked",
                "synced_at": now,
            },
        ],
    )


def downgrade():
    op.drop_index("ix_official_documents_company_id", table_name="official_documents")
    op.drop_table("official_documents")
    op.drop_index("ix_public_companies_legal_name", table_name="public_companies")
    op.drop_index("ix_public_companies_cnpj", table_name="public_companies")
    op.drop_index("ix_public_companies_ticker", table_name="public_companies")
    op.drop_table("public_companies")
