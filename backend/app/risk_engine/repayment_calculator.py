"""Repayment calculator — deterministic loan calculations.

All calculations use standard amortization formulas.
No LLM involvement. Pure Python math.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


TWO_PLACES = Decimal("0.01")


@dataclass
class MonthlyPaymentResult:
    monthly_payment: float
    total_interest: float
    total_repayment: float
    effective_rate: float | None


@dataclass
class AmortizationRow:
    month: int
    payment: float
    principal_portion: float
    interest_portion: float
    remaining_balance: float


def calculate_monthly_payment(
    principal: float,
    annual_rate: float,
    term_months: int,
    fees: float = 0.0,
) -> MonthlyPaymentResult:
    """
    Calculate monthly payment using standard amortization formula.

    M = P * [r(1+r)^n] / [(1+r)^n - 1]

    Where:
        P = principal
        r = monthly interest rate
        n = number of months
    """
    if principal <= 0:
        raise ValueError("Principal must be positive")
    if term_months <= 0:
        raise ValueError("Term must be positive")
    if annual_rate < 0:
        raise ValueError("Interest rate cannot be negative")

    total_principal = principal + fees

    if annual_rate == 0:
        monthly = total_principal / term_months
        return MonthlyPaymentResult(
            monthly_payment=round(monthly, 2),
            total_interest=0.0,
            total_repayment=round(total_principal, 2),
            effective_rate=0.0,
        )

    monthly_rate = annual_rate / 100 / 12
    factor = (1 + monthly_rate) ** term_months
    monthly = principal * (monthly_rate * factor) / (factor - 1)
    monthly = round(monthly, 2)

    total_repayment = monthly * term_months + fees
    total_interest = total_repayment - principal - fees

    # Effective annual rate (accounting for fees)
    effective_rate = None
    if fees > 0 and principal > fees:
        effective_monthly = monthly / (principal - fees)
        # Simplified effective rate
        effective_rate = round(annual_rate * (principal / (principal - fees)), 2)

    return MonthlyPaymentResult(
        monthly_payment=monthly,
        total_interest=round(total_interest, 2),
        total_repayment=round(total_repayment, 2),
        effective_rate=effective_rate,
    )


def calculate_amortization_schedule(
    principal: float,
    annual_rate: float,
    term_months: int,
) -> list[AmortizationRow]:
    """Generate a full amortization schedule."""
    if principal <= 0 or term_months <= 0:
        return []

    schedule = []
    balance = principal

    if annual_rate == 0:
        monthly = principal / term_months
        for month in range(1, term_months + 1):
            balance -= monthly
            schedule.append(AmortizationRow(
                month=month,
                payment=round(monthly, 2),
                principal_portion=round(monthly, 2),
                interest_portion=0.0,
                remaining_balance=round(max(balance, 0), 2),
            ))
        return schedule

    monthly_rate = annual_rate / 100 / 12
    factor = (1 + monthly_rate) ** term_months
    monthly = principal * (monthly_rate * factor) / (factor - 1)
    monthly = round(monthly, 2)

    for month in range(1, term_months + 1):
        interest_portion = round(balance * monthly_rate, 2)
        principal_portion = round(monthly - interest_portion, 2)

        # Last month adjustment
        if month == term_months:
            principal_portion = round(balance, 2)
            monthly_adjusted = principal_portion + interest_portion
            balance = 0.0
        else:
            balance -= principal_portion

        schedule.append(AmortizationRow(
            month=month,
            payment=round(monthly if month < term_months else monthly_adjusted, 2),
            principal_portion=principal_portion,
            interest_portion=interest_portion,
            remaining_balance=round(max(balance, 0), 2),
        ))

    return schedule


def calculate_total_repayment(
    principal: float,
    annual_rate: float,
    term_months: int,
    fees: float = 0.0,
) -> float:
    """Calculate total amount repaid over the loan term."""
    result = calculate_monthly_payment(principal, annual_rate, term_months, fees)
    return result.total_repayment


def calculate_early_repayment_cost(
    remaining_principal: float,
    early_repayment_fee_pct: float,
) -> float:
    """Calculate the cost of early repayment."""
    if remaining_principal < 0 or early_repayment_fee_pct < 0:
        raise ValueError("Values must be non-negative")
    fee = remaining_principal * (early_repayment_fee_pct / 100)
    return round(fee, 2)
