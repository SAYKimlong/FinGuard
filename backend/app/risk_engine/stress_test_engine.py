"""Stress test engine — deterministic scenario calculations.

All scenarios are hypothetical. Results are not predictions.
"""

from dataclasses import dataclass, field


@dataclass
class StressResult:
    scenario_type: str
    baseline_cashflow: float
    stressed_cashflow: float
    impact_amount: float
    impact_percentage: float | None
    assumptions: dict
    suggestions: list[str] = field(default_factory=list)


def _base_cashflow(
    income: float,
    expenses: float,
    debt: float,
    proposed: float = 0.0,
) -> float:
    return round(income - expenses - debt - proposed, 2)


def run_income_reduction(
    monthly_income: float,
    essential_expenses: float,
    existing_debt: float,
    proposed_payment: float = 0.0,
    reduction_pct: float = 20.0,
) -> StressResult:
    """Simulate income falling by a given percentage."""
    baseline = _base_cashflow(monthly_income, essential_expenses, existing_debt, proposed_payment)
    reduced_income = monthly_income * (1 - reduction_pct / 100)
    stressed = _base_cashflow(reduced_income, essential_expenses, existing_debt, proposed_payment)
    impact = round(baseline - stressed, 2)
    impact_pct = round((impact / abs(baseline)) * 100, 2) if baseline != 0 else None

    suggestions = []
    if stressed < 0:
        suggestions.append("Under this scenario, monthly obligations would exceed income.")
        suggestions.append("Consider whether savings could cover the shortfall and for how long.")
        suggestions.append("Review which expenses could be reduced if income decreases.")
    elif stressed < monthly_income * 0.05:
        suggestions.append("Cash flow would be very tight under this scenario.")
        suggestions.append("Building an emergency fund could provide a buffer.")

    return StressResult(
        scenario_type="income_reduction",
        baseline_cashflow=baseline,
        stressed_cashflow=stressed,
        impact_amount=impact,
        impact_percentage=impact_pct,
        assumptions={
            "scenario": f"Income reduced by {reduction_pct}%",
            "original_income": monthly_income,
            "reduced_income": round(reduced_income, 2),
            "note": "This is a hypothetical scenario, not a prediction.",
        },
        suggestions=suggestions,
    )


def run_unexpected_expense(
    monthly_income: float,
    essential_expenses: float,
    existing_debt: float,
    proposed_payment: float = 0.0,
    expense_amount: float = 1000.0,
    spread_months: int = 1,
) -> StressResult:
    """Simulate an unexpected one-time expense."""
    baseline = _base_cashflow(monthly_income, essential_expenses, existing_debt, proposed_payment)
    monthly_impact = expense_amount / max(spread_months, 1)
    stressed = round(baseline - monthly_impact, 2)
    impact = round(monthly_impact, 2)
    impact_pct = round((impact / abs(baseline)) * 100, 2) if baseline != 0 else None

    suggestions = []
    if stressed < 0:
        suggestions.append(f"A ${expense_amount:,.0f} unexpected expense would push cash flow negative.")
        suggestions.append("Consider whether emergency savings could absorb this cost.")
    else:
        suggestions.append(f"Cash flow would remain positive but reduced by ${impact:,.2f}/month.")

    return StressResult(
        scenario_type="unexpected_expense",
        baseline_cashflow=baseline,
        stressed_cashflow=stressed,
        impact_amount=impact,
        impact_percentage=impact_pct,
        assumptions={
            "scenario": f"Unexpected expense of ${expense_amount:,.0f}",
            "spread_over_months": spread_months,
            "monthly_impact": round(monthly_impact, 2),
            "note": "This is a hypothetical scenario, not a prediction.",
        },
        suggestions=suggestions,
    )


def run_expense_increase(
    monthly_income: float,
    essential_expenses: float,
    existing_debt: float,
    proposed_payment: float = 0.0,
    increase_pct: float = 15.0,
) -> StressResult:
    """Simulate essential expenses increasing by a percentage."""
    baseline = _base_cashflow(monthly_income, essential_expenses, existing_debt, proposed_payment)
    increased_expenses = essential_expenses * (1 + increase_pct / 100)
    stressed = _base_cashflow(monthly_income, increased_expenses, existing_debt, proposed_payment)
    impact = round(baseline - stressed, 2)
    impact_pct = round((impact / abs(baseline)) * 100, 2) if baseline != 0 else None

    suggestions = []
    if stressed < 0:
        suggestions.append("If essential expenses increase significantly, cash flow could become negative.")
        suggestions.append("Review which expense categories have the most variability.")
    else:
        suggestions.append(f"Cash flow would decrease by ${impact:,.2f} under this scenario.")

    return StressResult(
        scenario_type="expense_increase",
        baseline_cashflow=baseline,
        stressed_cashflow=stressed,
        impact_amount=impact,
        impact_percentage=impact_pct,
        assumptions={
            "scenario": f"Essential expenses increased by {increase_pct}%",
            "original_expenses": essential_expenses,
            "increased_expenses": round(increased_expenses, 2),
            "note": "This is a hypothetical scenario, not a prediction.",
        },
        suggestions=suggestions,
    )


def run_late_payment(
    monthly_income: float,
    essential_expenses: float,
    existing_debt: float,
    proposed_payment: float = 0.0,
    late_fee: float = 50.0,
    penalty_rate_increase: float = 0.0,
) -> StressResult:
    """Simulate a late payment penalty being incurred."""
    baseline = _base_cashflow(monthly_income, essential_expenses, existing_debt, proposed_payment)
    total_penalty = late_fee + (proposed_payment * penalty_rate_increase / 100)
    stressed = round(baseline - total_penalty, 2)
    impact = round(total_penalty, 2)
    impact_pct = round((impact / abs(baseline)) * 100, 2) if baseline != 0 else None

    suggestions = []
    suggestions.append(f"A late payment could cost an additional ${total_penalty:,.2f}.")
    if penalty_rate_increase > 0:
        suggestions.append("Some agreements increase interest rates after late payments — verify the terms.")
    suggestions.append("Setting up automatic payments can help avoid late fees.")

    return StressResult(
        scenario_type="late_payment",
        baseline_cashflow=baseline,
        stressed_cashflow=stressed,
        impact_amount=impact,
        impact_percentage=impact_pct,
        assumptions={
            "scenario": "Late payment penalty incurred",
            "late_fee": late_fee,
            "penalty_rate_increase_pct": penalty_rate_increase,
            "total_additional_cost": round(total_penalty, 2),
            "note": "Actual penalties depend on the specific contract terms.",
        },
        suggestions=suggestions,
    )
