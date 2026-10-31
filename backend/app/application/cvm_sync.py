"""Sincronização semanal dos Dados Abertos CVM (OPEN-27, ADR-009; SPEC-012, 027, 053, 054).

- Cadastro: atualiza razão social e setor das companhias já catalogadas (o cadastro CVM não
  traz ticker, então nenhuma companhia nova é criada).
- Índices DFP/ITR/IPE: identidade = CNPJ + tipo + data de referência + versão. Versão nova de
  um documento já conhecido é reapresentação: passa a ser a efetiva (`restated`), a anterior
  vira `replaced` e não há novo alerta. Só o documento inédito (`active`) gera aviso da
  watchlist (SPEC-027-R05).
- Apenas metadados e link oficial; nunca PDF (C-09). Só entram documentos entregues nos
  últimos 12 meses de calendário (SPEC-054).
"""

import logging
import uuid
from collections.abc import Callable
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.application.companies import CompanyService
from app.application.cvm_cache import twelve_calendar_months_before
from app.infrastructure.cvm_catalogue import RAD
from app.infrastructure.models import OfficialDocumentRecord, PublicCompanyRecord
from app.infrastructure.official_sources import CvmDocument, CvmSources, SourceError, digits

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
CVM_ITEMS = ("register", "DFP", "ITR", "IPE")
EFFECTIVE = ("active", "restated")

logger = logging.getLogger("finnova.cvm_sync")


def reference_label(document: CvmDocument) -> str:
    year = document.reference_date.year
    if document.document_type == "DFP":
        return f"Exercício {year}"
    if document.document_type == "ITR":
        return f"{(document.reference_date.month + 2) // 3}º trimestre de {year}"
    return document.reference_date.strftime("%d/%m/%Y")


class CvmSyncService:
    def __init__(
        self,
        db: Session,
        clock: Callable[[], datetime],
        sources: CvmSources,
        notify: Callable[[uuid.UUID], int] | None = None,
    ):
        self.db = db
        self.clock = clock
        self.sources = sources
        self.notify = notify or (lambda _document_id: 0)

    def catalogue(self) -> dict[str, PublicCompanyRecord]:
        return {
            digits(company.cnpj): company
            for company in self.db.scalars(select(PublicCompanyRecord))
        }

    def sync_register(self) -> str:
        companies = self.catalogue()
        changed = 0
        for entry in self.sources.company_register():
            company = companies.get(entry.cnpj)
            if company is None or not entry.active:
                continue
            sector = entry.sector or company.sector
            if (company.legal_name, company.sector) != (entry.legal_name, sector):
                company.legal_name, company.sector = entry.legal_name, sector
                changed += 1
        self.db.commit()
        return "updated" if changed else "kept"

    def sync_documents(self, document_type: str) -> str:
        now = self.clock()
        local_today = now.astimezone(SAO_PAULO).date()
        cutoff = twelve_calendar_months_before(now).astimezone(SAO_PAULO).date()
        companies = self.catalogue()
        documents = [
            document
            for year in (local_today.year - 1, local_today.year)
            for document in self.sources.document_index(document_type, year)
            if document.cnpj in companies and document.delivered_on >= cutoff
        ]
        created: list[uuid.UUID] = []
        for document in sorted(documents, key=lambda item: item.version):
            company = companies[document.cnpj]
            new_id = self.upsert(company, document, now)
            if new_id is not None:
                created.append(new_id)
        self.db.commit()
        for document_id in created:
            self.notify(document_id)
        return "updated" if documents else "kept"

    def upsert(
        self, company: PublicCompanyRecord, document: CvmDocument, now: datetime
    ) -> uuid.UUID | None:
        """Grava a versão; devolve o id apenas de documento inédito (que gera aviso)."""
        same_reference = list(
            self.db.scalars(
                select(OfficialDocumentRecord).where(
                    OfficialDocumentRecord.company_id == company.id,
                    OfficialDocumentRecord.document_type == document.document_type,
                    OfficialDocumentRecord.cvm_reference_date == document.reference_date,
                )
            )
        )
        link = (
            document.link
            if CompanyService.is_official_cvm_url(document.link)
            else f"{RAD}?CNPJ={document.cnpj}"
        )
        existing = next((r for r in same_reference if r.cvm_version == document.version), None)
        if existing is not None:
            existing.synced_at, existing.official_url = now, link
            return None
        latest = max((r.cvm_version or 0 for r in same_reference), default=0)
        if not same_reference:
            status = "active"
        elif document.version > latest:
            status = "restated"
            for record in same_reference:
                if record.status in EFFECTIVE:
                    record.status = "replaced"
        else:
            status = "replaced"  # versão antiga recebida depois da reapresentação
        record = OfficialDocumentRecord(
            id=uuid.uuid4(),
            company_id=company.id,
            document_type=document.document_type,
            subject=document.subject[:180],
            reference_period=reference_label(document),
            delivered_at=document.delivered_on,
            status=status,
            official_url=link,
            link_status="unchecked",
            last_checked_at=None,
            synced_at=now,
            cvm_reference_date=document.reference_date,
            cvm_version=document.version,
        )
        self.db.add(record)
        self.db.flush()
        return record.id if status == "active" else None

    def sync_item(self, item: str) -> str:
        try:
            return self.sync_register() if item == "register" else self.sync_documents(item)
        except (SourceError, SQLAlchemyError) as exc:
            self.db.rollback()
            logger.warning("cvm_sync_failed item=%s reason=%s", item, exc)
            return "failed"

    def run(self, items: tuple[str, ...] = CVM_ITEMS) -> dict[str, str]:
        result = {item: self.sync_item(item) for item in items}
        logger.info("cvm_sync_run %s", result)
        return result
