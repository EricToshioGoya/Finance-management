"""Store local structured CVM indicator fixtures for SPEC-053, never report PDFs."""

from datetime import UTC, date, datetime

import sqlalchemy as sa
from alembic import op

revision = "017_cvm_financial_indicators"
down_revision = "016_public_cvm_catalogue"
branch_labels = None
depends_on = None

PETR4 = "11111111-1111-1111-1111-111111111111"
VALE3 = "22222222-2222-2222-2222-222222222222"
SOURCE = "Dados Abertos CVM — catálogo local de referência"
DFP = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/"
ITR = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/"


def upgrade():
    op.create_table(
        "financial_indicators",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Uuid(),
            sa.ForeignKey("public_companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("metric", sa.String(30), nullable=False),
        sa.Column("period_kind", sa.String(12), nullable=False),
        sa.Column("reference_period", sa.String(80), nullable=False),
        sa.Column("reference_date", sa.Date(), nullable=False),
        sa.Column("value", sa.Numeric(18, 2), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("source_name", sa.String(180), nullable=False),
        sa.Column("source_url", sa.String(1000), nullable=False),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column("published_at", sa.Date(), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "metric IN ('net_revenue', 'net_income', 'equity')", name="valid_financial_metric"
        ),
        sa.CheckConstraint(
            "period_kind IN ('annual', 'quarterly')", name="valid_financial_period_kind"
        ),
        sa.CheckConstraint("unit = 'BRL_THOUSANDS'", name="valid_financial_indicator_unit"),
        sa.CheckConstraint(
            "status IN ('active', 'restated')", name="valid_financial_indicator_status"
        ),
    )
    op.create_index("ix_financial_indicators_company_id", "financial_indicators", ["company_id"])
    op.create_index("ix_financial_indicators_metric", "financial_indicators", ["metric"])
    indicators = sa.table(
        "financial_indicators",
        sa.column("id", sa.Uuid()),
        sa.column("company_id", sa.Uuid()),
        sa.column("metric", sa.String()),
        sa.column("period_kind", sa.String()),
        sa.column("reference_period", sa.String()),
        sa.column("reference_date", sa.Date()),
        sa.column("value", sa.Numeric()),
        sa.column("unit", sa.String()),
        sa.column("source_name", sa.String()),
        sa.column("source_url", sa.String()),
        sa.column("status", sa.String()),
        sa.column("published_at", sa.Date()),
        sa.column("synced_at", sa.DateTime(timezone=True)),
    )
    now = datetime(2026, 10, 28, tzinfo=UTC)
    rows = []
    fixture_values = {
        PETR4: (
            ("315_692_000", "1_746_000", "397_921_000"),
            ("153_043_000", "21_074_000", "408_173_000"),
        ),
        VALE3: (
            ("206_005_000", "31_961_000", "207_687_000"),
            ("98_628_000", "9_746_000", "215_120_000"),
        ),
    }
    metrics = ("net_revenue", "net_income", "equity")
    periods = (
        ("Exercício 2025", date(2025, 12, 31), "annual", DFP, date(2026, 2, 26)),
        ("2º trimestre de 2026", date(2026, 6, 30), "quarterly", ITR, date(2026, 8, 7)),
    )
    for company_id, values_by_period in fixture_values.items():
        for period_index, (
            label,
            reference_date,
            kind,
            source_url,
            published_at,
        ) in enumerate(periods):
            for metric_index, metric in enumerate(metrics):
                rows.append(
                    {
                        "id": (
                            f"{company_id[:8]}-5353-4000-8000-"
                            f"{period_index + 1}{metric_index + 1:011d}"
                        ),
                        "company_id": company_id,
                        "metric": metric,
                        "period_kind": kind,
                        "reference_period": label,
                        "reference_date": reference_date,
                        "value": values_by_period[period_index][metric_index].replace("_", ""),
                        "unit": "BRL_THOUSANDS",
                        "source_name": SOURCE,
                        "source_url": source_url,
                        "status": "active",
                        "published_at": published_at,
                        "synced_at": now,
                    }
                )
    # A superseded snapshot is retained as an auditable restatement; it is never summed.
    rows.append(
        {
            "id": "22222222-5353-4000-8000-000000000099",
            "company_id": VALE3,
            "metric": "net_income",
            "period_kind": "quarterly",
            "reference_period": "2º trimestre de 2026",
            "reference_date": date(2026, 6, 30),
            "value": "9200000",
            "unit": "BRL_THOUSANDS",
            "source_name": SOURCE,
            "source_url": ITR,
            "status": "restated",
            "published_at": date(2026, 7, 30),
            "synced_at": now,
        }
    )
    op.bulk_insert(indicators, rows)


def downgrade():
    op.drop_index("ix_financial_indicators_metric", table_name="financial_indicators")
    op.drop_index("ix_financial_indicators_company_id", table_name="financial_indicators")
    op.drop_table("financial_indicators")
