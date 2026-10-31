"""SPEC-012 catalogue queries and explicit, safe official-link verification."""

from collections.abc import Callable
from datetime import UTC, date, datetime
from unicodedata import combining, normalize
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.auth import AuthError
from app.infrastructure.cvm_catalogue import (
    rebuild_documents_if_missing,
    rebuild_indicators_if_missing,
)
from app.infrastructure.models import (
    FinancialIndicatorRecord,
    OfficialDocumentRecord,
    PublicCompanyRecord,
)

OFFICIAL_CVM_HOSTS = {"rad.cvm.gov.br", "www.rad.cvm.gov.br"}


class CompanyService:
    def __init__(self, db: Session, clock: Callable[[], datetime] | None = None):
        self.db = db
        self.clock = clock or (lambda: datetime.now(UTC))

    @staticmethod
    def search_text(value: str) -> str:
        return "".join(
            character
            for character in normalize("NFD", value).casefold()
            if not combining(character)
        )

    @staticmethod
    def company_values(record: PublicCompanyRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "ticker": record.ticker,
            "cnpj": record.cnpj,
            "legal_name": record.legal_name,
            "sector": record.sector,
        }

    @staticmethod
    def document_values(record: OfficialDocumentRecord) -> dict[str, object]:
        return {
            "id": record.id,
            "company_id": record.company_id,
            "document_type": record.document_type,
            "subject": record.subject,
            "reference_period": record.reference_period,
            "delivered_at": record.delivered_at,
            "status": record.status,
            "official_url": record.official_url,
            "link_status": record.link_status,
            "last_checked_at": record.last_checked_at,
        }

    @staticmethod
    def indicator_values(
        record: FinancialIndicatorRecord, effective_ids: set[UUID]
    ) -> dict[str, object]:
        return {
            "id": record.id,
            "company_id": record.company_id,
            "metric": record.metric,
            "period_kind": record.period_kind,
            "reference_period": record.reference_period,
            "reference_date": record.reference_date,
            "value": record.value,
            "unit": record.unit,
            "source_name": record.source_name,
            "source_url": record.source_url,
            "status": record.status,
            "published_at": record.published_at,
            "synced_at": record.synced_at,
            "effective": record.id in effective_ids,
        }

    def search(self, query: str | None, limit: int) -> list[dict[str, object]]:
        records = self.db.scalars(select(PublicCompanyRecord).order_by(PublicCompanyRecord.ticker))
        if query and query.strip():
            needle = self.search_text(query.strip())
            records = (
                record
                for record in records
                if needle in self.search_text(record.ticker)
                or needle in self.search_text(record.cnpj)
                or needle in self.search_text(record.legal_name)
            )
        return [self.company_values(record) for record in list(records)[:limit]]

    def company(self, company_id: UUID) -> dict[str, object]:
        record = self.db.get(PublicCompanyRecord, company_id)
        if record is None:
            raise AuthError("company_not_found", 404)
        return self.company_values(record)

    def documents(
        self,
        company_id: UUID,
        document_type: str | None,
        starts_on: date | None,
        ends_on: date | None,
    ) -> list[dict[str, object]]:
        self.company(company_id)
        rebuild_documents_if_missing(self.db, company_id, self.clock())
        self.db.commit()
        statement = select(OfficialDocumentRecord).where(
            OfficialDocumentRecord.company_id == company_id
        )
        if document_type is not None:
            statement = statement.where(OfficialDocumentRecord.document_type == document_type)
        if starts_on is not None:
            statement = statement.where(OfficialDocumentRecord.delivered_at >= starts_on)
        if ends_on is not None:
            statement = statement.where(OfficialDocumentRecord.delivered_at <= ends_on)
        records = self.db.scalars(statement.order_by(OfficialDocumentRecord.delivered_at.desc()))
        return [self.document_values(record) for record in records]

    def financial_indicators(
        self, company_id: UUID, metric: str | None, period_kind: str | None
    ) -> list[dict[str, object]]:
        """Return all revisions and identify the latest one for each account/period.

        Keeping the historical row visible makes a restatement auditable while the
        ``effective`` flag prevents charts and totals from silently adding revisions.
        """
        self.company(company_id)
        rebuild_indicators_if_missing(self.db, company_id, self.clock())
        self.db.commit()
        statement = select(FinancialIndicatorRecord).where(
            FinancialIndicatorRecord.company_id == company_id
        )
        if metric is not None:
            statement = statement.where(FinancialIndicatorRecord.metric == metric)
        if period_kind is not None:
            statement = statement.where(FinancialIndicatorRecord.period_kind == period_kind)
        records = list(
            self.db.scalars(
                statement.order_by(
                    FinancialIndicatorRecord.reference_date,
                    FinancialIndicatorRecord.metric,
                    FinancialIndicatorRecord.published_at,
                )
            )
        )
        latest: dict[tuple[str, date], FinancialIndicatorRecord] = {}
        for record in records:
            key = (record.metric, record.reference_date)
            if key not in latest or record.published_at >= latest[key].published_at:
                latest[key] = record
        effective_ids = {record.id for record in latest.values()}
        return [self.indicator_values(record, effective_ids) for record in records]

    @staticmethod
    def is_official_cvm_url(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme == "https" and parsed.hostname in OFFICIAL_CVM_HOSTS

    def check_link(self, document_id: UUID) -> dict[str, object]:
        record = self.db.get(OfficialDocumentRecord, document_id)
        if record is None:
            raise AuthError("official_document_not_found", 404)
        if not self.is_official_cvm_url(record.official_url):
            record.link_status = "broken"
        else:
            request = Request(
                record.official_url, method="HEAD", headers={"User-Agent": "FinNova/1.0"}
            )
            try:
                with urlopen(request, timeout=5) as response:
                    record.link_status = "available" if response.status < 400 else "broken"
            except (HTTPError, URLError, TimeoutError, ValueError):
                record.link_status = "broken"
        record.last_checked_at = self.clock()
        self.db.commit()
        return self.document_values(record)
