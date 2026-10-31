"""Versioned local reference source used when the public CVM cache is rebuilt."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.models import FinancialIndicatorRecord, OfficialDocumentRecord

PETR4 = UUID("11111111-1111-1111-1111-111111111111")
VALE3 = UUID("22222222-2222-2222-2222-222222222222")
RAD = "https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx"
SOURCE = "Dados Abertos CVM — catálogo local de referência"
DFP = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/"
ITR = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/"


def _identifier(company_id: UUID, value: int) -> UUID:
    return UUID(f"{str(company_id)[:8]}-5353-4000-8000-{value:012d}")


def rebuild_documents_if_missing(db: Session, company_id: UUID, synced_at: datetime) -> None:
    """Recreate only missing metadata, never a PDF or any user-owned record."""
    if db.scalar(
        select(func.count())
        .select_from(OfficialDocumentRecord)
        .where(OfficialDocumentRecord.company_id == company_id)
    ):
        return
    cnpj = "33000167000101" if company_id == PETR4 else "33592510000154"
    delivered = (
        (
            "DFP",
            "Demonstrações Financeiras Padronizadas",
            "Exercício 2025",
            date(2026, 2, 26),
            "active",
        ),
        ("ITR", "Informações Trimestrais", "2º trimestre de 2026", date(2026, 8, 7), "active"),
        ("FRE", "Formulário de Referência", "2026", date(2026, 6, 30), "active"),
        ("IPE", "Fato Relevante", "Outubro de 2026", date(2026, 10, 20), "active"),
    )
    if company_id == VALE3:
        delivered = (
            (
                "DFP",
                "Demonstrações Financeiras Padronizadas",
                "Exercício 2025",
                date(2026, 2, 20),
                "active",
            ),
            (
                "ITR",
                "Informações Trimestrais",
                "2º trimestre de 2026",
                date(2026, 8, 1),
                "restated",
            ),
            ("FRE", "Formulário de Referência", "2026", date(2026, 6, 27), "active"),
            ("IPE", "Comunicado ao Mercado", "Outubro de 2026", date(2026, 10, 18), "active"),
        )
    for index, (document_type, subject, period, delivered_at, status) in enumerate(
        delivered, start=1
    ):
        db.add(
            OfficialDocumentRecord(
                id=_identifier(company_id, 10_000 + index),
                company_id=company_id,
                document_type=document_type,
                subject=subject,
                reference_period=period,
                delivered_at=delivered_at,
                status=status,
                official_url=f"{RAD}?CNPJ={cnpj}",
                link_status="unchecked",
                last_checked_at=None,
                synced_at=synced_at,
            )
        )


def rebuild_indicators_if_missing(db: Session, company_id: UUID, synced_at: datetime) -> None:
    """Recreate structured reference values while retaining the explicit restatement rule."""
    if db.scalar(
        select(func.count())
        .select_from(FinancialIndicatorRecord)
        .where(FinancialIndicatorRecord.company_id == company_id)
    ):
        return
    values = {
        PETR4: ((315_692_000, 1_746_000, 397_921_000), (153_043_000, 21_074_000, 408_173_000)),
        VALE3: ((206_005_000, 31_961_000, 207_687_000), (98_628_000, 9_746_000, 215_120_000)),
    }[company_id]
    metrics = ("net_revenue", "net_income", "equity")
    periods = (
        ("Exercício 2025", date(2025, 12, 31), "annual", DFP, date(2026, 2, 26)),
        ("2º trimestre de 2026", date(2026, 6, 30), "quarterly", ITR, date(2026, 8, 7)),
    )
    for period_index, (label, reference_date, kind, source_url, published_at) in enumerate(periods):
        for metric_index, metric in enumerate(metrics):
            db.add(
                FinancialIndicatorRecord(
                    id=_identifier(company_id, 100 + (period_index + 1) * 10 + metric_index + 1),
                    company_id=company_id,
                    metric=metric,
                    period_kind=kind,
                    reference_period=label,
                    reference_date=reference_date,
                    value=Decimal(values[period_index][metric_index]),
                    unit="BRL_THOUSANDS",
                    source_name=SOURCE,
                    source_url=source_url,
                    status="active",
                    published_at=published_at,
                    synced_at=synced_at,
                )
            )
    if company_id == VALE3:
        db.add(
            FinancialIndicatorRecord(
                id=_identifier(company_id, 199),
                company_id=company_id,
                metric="net_income",
                period_kind="quarterly",
                reference_period="2º trimestre de 2026",
                reference_date=date(2026, 6, 30),
                value=Decimal(9_200_000),
                unit="BRL_THOUSANDS",
                source_name=SOURCE,
                source_url=ITR,
                status="restated",
                published_at=date(2026, 7, 30),
                synced_at=synced_at,
            )
        )
