"""Casos de uso das SPEC-046 a SPEC-049 (aposentadoria, previdência, IR e resumo anual)."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app.application.auth import AuthError, AuthService
from app.domain.expansion import (
    TAX_RULE_VERSION,
    comparar_previdencia,
    estimar_ir,
    projetar_aposentadoria,
)
from app.infrastructure.models import SimulationRecord, TaxEstimateRecord

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
RETIREMENT_NOTICE = (
    "Projeção educativa: a renda estimada não é benefício garantido e varia com a "
    "rentabilidade real, a inflação e mudanças na legislação previdenciária."
)
PENSION_NOTICE = (
    "Simplificação educativa com tabela interna versionada; não é recomendação personalizada "
    "nem substitui a análise de um profissional."
)
PGBL_CONTEXT = (
    "O PGBL costuma ser mais vantajoso para quem faz a declaração completa do IR, pois os "
    "aportes podem ser deduzidos da base de cálculo (limite legal sobre a renda bruta "
    "tributável); para quem usa a declaração simplificada ou é isento, o VGBL tende a ser "
    "mais adequado. O benefício fiscal não é calculado nesta simulação."
)
TAX_NOTICE = (
    "Estimativa educativa: não substitui a apuração de um contador nem o e-CAC da Receita "
    "Federal. O FinNova não gera nem envia DARF."
)
ANNUAL_NOTICE = (
    "Resumo auxiliar gerado pelo FinNova a partir dos seus registros e simulações. "
    "Não é informe de rendimentos oficial de instituição financeira."
)


class PlanningTaxService:
    def __init__(self, db, auth: AuthService):
        self.db, self.auth = db, auth

    def _owner(self, user_id: uuid.UUID) -> None:
        self.auth.require_category_owner(user_id)

    # SPEC-046
    def retirement(self, user_id: uuid.UUID, data) -> dict[str, object]:
        self._owner(user_id)
        result = projetar_aposentadoria(
            idade_atual=data.current_age,
            idade_alvo=data.target_age,
            valor_inicial=data.initial_amount,
            aporte_mensal=data.monthly_contribution,
            taxa_anual=data.annual_rate,
            taxa_retirada_anual=data.withdrawal_rate,
        )
        try:
            suggestion = self.auth.indicator("selic")
            suggested = {
                "code": "selic",
                "value": suggestion["value"],
                "stale": suggestion["stale"],
            }
        except AuthError:
            suggested = None  # sem cache válido: nenhuma taxa é inventada (C-08)
        return {
            "months": result.meses,
            "invested": result.total_investido,
            "projected_wealth": result.patrimonio_projetado,
            "estimated_monthly_income": result.renda_mensal_estimada,
            "withdrawal_rate": result.taxa_retirada_anual,
            "suggested_rate": suggested,
            "assumptions": [
                "Valores nominais, sem descontar inflação.",
                "Aportes no fim de cada mês; taxa anual convertida por equivalência composta.",
                f"Renda = patrimônio × {result.taxa_retirada_anual}% ao ano ÷ 12.",
            ],
            "notice": RETIREMENT_NOTICE,
        }

    # SPEC-047
    def pension(self, user_id: uuid.UUID, data) -> dict[str, object]:
        self._owner(user_id)
        results = comparar_previdencia(
            valor_inicial=data.initial_amount,
            aporte_mensal=data.monthly_contribution,
            taxa_anual=data.annual_rate,
            prazo_meses=data.term_months,
            regime=data.regime,
            aliquota_progressiva=data.progressive_rate,
        )
        return {
            "regime": data.regime,
            "rule_version": TAX_RULE_VERSION,
            "results": [
                {
                    "modality": item.modalidade,
                    "invested": item.total_investido,
                    "gross_amount": item.montante_bruto,
                    "earnings": item.rendimento,
                    "tax": item.imposto,
                    "net_amount": item.montante_liquido,
                    "effective_tax_rate": item.aliquota_efetiva,
                }
                for item in results
            ],
            "pgbl_context": PGBL_CONTEXT,
            "notice": PENSION_NOTICE,
        }

    # SPEC-048
    def _estimate_output(self, record: TaxEstimateRecord, notes: tuple[str, ...] = ()):
        return {
            "id": record.id,
            "regime": record.regime,
            "competence": record.competence.strftime("%Y-%m"),
            "sales": record.sales,
            "result": record.result,
            "tax_rate": record.tax_rate,
            "tax": record.tax,
            "exempt": record.exempt,
            "darf_due_on": record.darf_due_on,
            "rule_version": record.rule_version,
            "notes": list(notes),
            "notice": TAX_NOTICE,
        }

    def create_tax_estimate(self, user_id: uuid.UUID, data) -> dict[str, object]:
        self._owner(user_id)
        competence = date.fromisoformat(f"{data.competence}-01")
        estimate = estimar_ir(
            regime=data.regime,
            competencia=competence,
            resultado=data.result,
            vendas_no_mes=data.sales,
            dias_aplicacao=data.holding_days,
        )
        record = TaxEstimateRecord(
            user_id=user_id,
            regime=data.regime,
            competence=competence,
            sales=data.sales,
            result=data.result,
            tax_rate=estimate.aliquota,
            tax=estimate.imposto,
            exempt=estimate.isento,
            darf_due_on=estimate.vencimento_darf,
            rule_version=TAX_RULE_VERSION,
            created_at=self.auth.clock(),
        )
        self.db.add(record)
        self.db.commit()
        return self._estimate_output(record, estimate.observacoes)

    def _estimates(self, user_id: uuid.UUID, year: int | None = None):
        query = select(TaxEstimateRecord).where(TaxEstimateRecord.user_id == user_id)
        if year is not None:
            query = query.where(
                TaxEstimateRecord.competence >= date(year, 1, 1),
                TaxEstimateRecord.competence < date(year + 1, 1, 1),
            )
        return self.db.scalars(
            query.order_by(TaxEstimateRecord.competence.desc(), TaxEstimateRecord.created_at)
        ).all()

    def list_tax_estimates(self, user_id: uuid.UUID) -> list[dict[str, object]]:
        self._owner(user_id)
        return [self._estimate_output(record) for record in self._estimates(user_id)]

    def delete_tax_estimate(self, user_id: uuid.UUID, estimate_id: uuid.UUID) -> None:
        self._owner(user_id)
        record = self.db.get(TaxEstimateRecord, estimate_id)
        if record is None or record.user_id != user_id:
            raise AuthError("tax_estimate_not_found", 404)
        self.db.delete(record)
        self.db.commit()

    # SPEC-049
    def annual_summary(self, user_id: uuid.UUID, year: int) -> dict[str, object]:
        self._owner(user_id)
        months = [self.auth.income_summary(user_id, date(year, month, 1)) for month in range(1, 13)]
        totals = {
            key: sum((Decimal(m[key]) for m in months), Decimal("0"))
            for key in ("recurring_income", "one_time_income", "bonus", "total")
        }
        estimates = self._estimates(user_id, year)
        start = datetime(year, 1, 1, tzinfo=SAO_PAULO).astimezone(UTC)
        end = datetime(year + 1, 1, 1, tzinfo=SAO_PAULO).astimezone(UTC)
        simulations = [
            self.auth.simulation_output(record)
            for record in self.db.scalars(
                select(SimulationRecord)
                .where(
                    SimulationRecord.user_id == user_id,
                    SimulationRecord.created_at >= start,
                    SimulationRecord.created_at < end,
                )
                .order_by(SimulationRecord.created_at)
            )
        ]
        # Ano sem dados não gera renda inexistente (R02).
        if totals["total"] == 0 and not estimates and not simulations:
            raise AuthError("no_data_for_year", 404)
        return {
            "year": year,
            "registered_income": {
                "monthly": [
                    {"competence": m["competence"], "total": Decimal(m["total"])} for m in months
                ],
                **totals,
            },
            "tax_estimates": [self._estimate_output(record) for record in estimates],
            "estimated_tax_total": sum((r.tax for r in estimates), Decimal("0")),
            "simulations": [
                {
                    "label": item["label"],
                    "kind": item["kind"],
                    "final_amount": item["final_amount"],
                    "estimated_tax": Decimal(str(item["payload"].get("estimated_tax", "0"))),
                    "origin": "simulated",
                }
                for item in simulations
            ],
            "notice": ANNUAL_NOTICE,
        }
