"""SPEC-040: resumo mensal automático optativo, enviado pelo canal de e-mail (SPEC-061)."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.application.auth import AuthError, AuthService
from app.infrastructure.models import (
    HealthScoreRecord,
    MonthlySummaryRecord,
    NetWorthSnapshotRecord,
    ReportSettingsRecord,
    UserRecord,
)
from app.infrastructure.pdf import pdf_document

SAO_PAULO = ZoneInfo("America/Sao_Paulo")


def previous_month(instant: datetime) -> date:
    """Competência anterior, fechada no fuso de São Paulo (ADR-006)."""
    local = instant.astimezone(SAO_PAULO).date().replace(day=1)
    return date(local.year - 1, 12, 1) if local.month == 1 else local.replace(month=local.month - 1)


class MonthlySummaryService:
    def __init__(self, db, auth: AuthService):
        self.db, self.auth = db, auth

    def settings(self, user_id: uuid.UUID) -> dict[str, bool]:
        record = self.db.get(ReportSettingsRecord, user_id)
        return {"monthly_summary_enabled": bool(record and record.monthly_summary_enabled)}

    def set_settings(self, user_id: uuid.UUID, enabled: bool) -> dict[str, bool]:
        self.auth.require_category_owner(user_id)
        record = self.db.get(ReportSettingsRecord, user_id)
        if record is None:
            record = ReportSettingsRecord(user_id=user_id)
            self.db.add(record)
        record.monthly_summary_enabled, record.updated_at = enabled, self.auth.clock()
        self.db.commit()
        return self.settings(user_id)

    def content(self, user_id: uuid.UUID, competence: date) -> dict[str, object]:
        """Somente dados do titular e da competência anterior (INV-001)."""
        summary = self.auth.balance_summary(user_id, competence)
        snapshot = self.db.scalar(
            select(NetWorthSnapshotRecord).where(
                NetWorthSnapshotRecord.user_id == user_id,
                NetWorthSnapshotRecord.competence == competence,
            )
        )
        score = self.db.scalar(
            select(HealthScoreRecord).where(
                HealthScoreRecord.user_id == user_id, HealthScoreRecord.competence == competence
            )
        )
        return {
            "competence": competence.strftime("%Y-%m"),
            "income": Decimal(summary["total"]),
            "expenses": Decimal(summary["expenses"]),
            "balance_variation": Decimal(summary["balance_variation"]),
            "net_worth": snapshot.net_worth if snapshot else None,
            "health_score": score.score if score else None,
        }

    def pdf(self, data: dict[str, object]) -> bytes:
        def show(value):
            return "não registrado no mês" if value is None else f"R$ {value}"

        return pdf_document(
            [
                f"FinNova - Resumo mensal {data['competence']}",
                "",
                f"Renda do mês: R$ {data['income']}",
                f"Gastos do mês: R$ {data['expenses']}",
                f"Variação do saldo: R$ {data['balance_variation']}",
                f"Patrimônio líquido (posição registrada): {show(data['net_worth'])}",
                "Score de saúde financeira: "
                + (
                    "não calculado no mês"
                    if data["health_score"] is None
                    else str(data["health_score"])
                ),
                "",
                "Relatório automático optativo; desative em Minha conta > Relatórios.",
            ]
        )

    def history(self, user_id: uuid.UUID) -> list[dict[str, object]]:
        self.auth.require_category_owner(user_id)
        return [
            {
                "competence": record.competence.strftime("%Y-%m"),
                "status": record.status,
                "generated_at": record.generated_at,
            }
            for record in self.db.scalars(
                select(MonthlySummaryRecord)
                .where(MonthlySummaryRecord.user_id == user_id)
                .order_by(MonthlySummaryRecord.competence.desc())
            )
        ]

    def download(self, user_id: uuid.UUID, competence: date) -> bytes:
        self.auth.require_category_owner(user_id)
        if competence.replace(day=1) > previous_month(self.auth.clock()):
            raise AuthError("competence_not_closed", 422)  # INV-001: nunca o mês corrente
        return self.pdf(self.content(user_id, competence))

    def run(self) -> dict[str, int]:
        """Gera e envia o resumo do mês anterior para quem optou; um envio por mês."""
        competence = previous_month(self.auth.clock())
        recipients = self.db.scalars(
            select(ReportSettingsRecord.user_id)
            .join(UserRecord, UserRecord.id == ReportSettingsRecord.user_id)
            .where(
                ReportSettingsRecord.monthly_summary_enabled.is_(True),
                UserRecord.email_verified_at.is_not(None),
            )
        ).all()
        counts = {"generated": 0, "skipped": 0}
        for user_id in recipients:
            exists = self.db.scalar(
                select(MonthlySummaryRecord.id).where(
                    MonthlySummaryRecord.user_id == user_id,
                    MonthlySummaryRecord.competence == competence,
                )
            )
            if exists is not None:
                counts["skipped"] += 1
                continue
            record = MonthlySummaryRecord(
                user_id=user_id,
                competence=competence,
                status="provider_unavailable",
                generated_at=self.auth.clock(),
            )
            self.db.add(record)
            try:
                self.db.commit()  # reserva a competência antes de enviar (sem envio duplicado)
            except IntegrityError:
                self.db.rollback()
                counts["skipped"] += 1
                continue
            data = self.content(user_id, competence)
            result = self.auth.dispatch_external(
                user_id,
                f"Resumo mensal FinNova {data['competence']}",
                "Seu resumo do mês anterior está em anexo (PDF).",
                None,
                "monthly_summary",
                channels=("email",),
                attachment=(f"resumo-{data['competence']}.pdf", self.pdf(data)),
            )
            # Sem preferência de e-mail habilitada, o envio não acontece (no_destination).
            record.status = result.get("email", "no_destination")
            self.db.commit()
            counts["generated"] += 1
        return counts
