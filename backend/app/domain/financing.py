"""SPEC-036: pure educational Price amortization, without financial writes."""

from dataclasses import dataclass
from decimal import Decimal, localcontext

from app.domain.juros_compostos import ErroCalculo, arredondar_moeda, converter_taxa


@dataclass(frozen=True, slots=True)
class Installment:
    number: int
    payment: Decimal
    interest: Decimal
    principal: Decimal
    remaining_balance: Decimal


@dataclass(frozen=True, slots=True)
class FinancingPlan:
    asset_value: Decimal
    down_payment: Decimal
    financed_amount: Decimal
    installments: int
    annual_rate: Decimal
    monthly_rate: Decimal
    installment_amount: Decimal
    total_installments: Decimal
    total_paid: Decimal
    total_interest: Decimal
    schedule: tuple[Installment, ...]


def simulate_financing(
    asset_value: Decimal,
    down_payment: Decimal,
    installments: int,
    annual_rate: Decimal,
) -> FinancingPlan:
    """Price annuity with end-of-month payments and annual effective rate.

    Monetary rounding only occurs at the output boundary. Internal balances
    use Decimal precision and the last installment clears residual principal.
    Fees, insurance, IOF, CET, indexation and early repayment are excluded.
    """
    if not all(
        isinstance(value, Decimal) and value.is_finite()
        for value in (asset_value, down_payment, annual_rate)
    ):
        raise ErroCalculo("financing", "decimal_invalido")
    if asset_value <= 0 or down_payment < 0 or down_payment > asset_value:
        raise ErroCalculo("asset_value", "entrada_invalida")
    if type(installments) is not int or not 1 <= installments <= 600:
        raise ErroCalculo("installments", "prazo_invalido")
    if annual_rate < 0 or annual_rate > 100:
        raise ErroCalculo("annual_rate", "taxa_nao_suportada")
    principal = asset_value - down_payment
    monthly_percent = converter_taxa(annual_rate, "anual", "mensal")
    rate = monthly_percent / Decimal("100")
    with localcontext() as ctx:
        ctx.prec = 42
        if principal == 0:
            payment = Decimal("0")
        elif rate == 0:
            payment = principal / installments
        else:
            compound = (Decimal("1") + rate) ** installments
            payment = principal * rate * compound / (compound - Decimal("1"))
        rows = []
        balance = principal
        total_interest = Decimal("0")
        total_installments = Decimal("0")
        for number in range(1, installments + 1):
            interest = balance * rate
            principal_payment = balance if number == installments else payment - interest
            current_payment = principal_payment + interest
            balance = max(Decimal("0"), balance - principal_payment)
            total_interest += interest
            total_installments += current_payment
            rows.append(
                Installment(
                    number=number,
                    payment=arredondar_moeda(current_payment),
                    interest=arredondar_moeda(interest),
                    principal=arredondar_moeda(principal_payment),
                    remaining_balance=arredondar_moeda(balance),
                )
            )
        return FinancingPlan(
            asset_value=arredondar_moeda(asset_value),
            down_payment=arredondar_moeda(down_payment),
            financed_amount=arredondar_moeda(principal),
            installments=installments,
            annual_rate=annual_rate,
            monthly_rate=monthly_percent,
            installment_amount=arredondar_moeda(payment),
            total_installments=arredondar_moeda(total_installments),
            total_paid=arredondar_moeda(down_payment + total_installments),
            total_interest=arredondar_moeda(total_interest),
            schedule=tuple(rows),
        )
