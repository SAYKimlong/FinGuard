"""Financial risk indicators — deterministic calculations.

These are analytical indicators, NOT legal or lending thresholds.
"""

from dataclasses import dataclass


@dataclass
class AffordabilityResult:
    dti_ratio: float | None
    payment_to_income: float | None
    remaining_cashflow: float
    emergency_fund_months: float | None
    total_monthly_obligations: float
    assessment: str
    warnings: list[str]


def calculate_dti_ratio(
    total_monthly_debt: float,
    monthly_income: float,
) -> float | None:
    """
    Calculate Debt-to-Income ratio.

    DTI = (Total Monthly Debt Payments / Monthly Income) × 100

    This is an analytical indicator. Different jurisdictions and
    institutions use different thresholds. FinGuard does not define
    universal limits.
    """
    if monthly_income <= 0:
        return None
    return round((total_monthly_debt / monthly_income) * 100, 2)


def calculate_remaining_cashflow(
    monthly_income: float,
    essential_expenses: float,
    existing_debt: float,
    proposed_payment: float = 0.0,
) -> float:
    """Calculate remaining monthly cash flow after all obligations."""
    return round(monthly_income - essential_expenses - existing_debt - proposed_payment, 2)


def calculate_emergency_fund_coverage(
    savings: float,
    monthly_expenses: float,
) -> float | None:
    """
    Calculate how many months of expenses the emergency fund covers.

    Coverage = Savings / Monthly Essential Expenses
    """
    if monthly_expenses <= 0:
        return None
    return round(savings / monthly_expenses, 1)


def calculate_affordability(
    monthly_income: float,
    essential_expenses: float,
    existing_debt: float,
    proposed_payment: float,
    savings: float = 0.0,
) -> AffordabilityResult:
    """
    Comprehensive affordability assessment.

    Returns calculated indicators and contextual warnings.
    These are not definitive judgments.
    """
    warnings = []

    total_debt = existing_debt + proposed_payment
    dti = calculate_dti_ratio(total_debt, monthly_income)
    payment_to_income = None
    if monthly_income > 0:
        payment_to_income = round((proposed_payment / monthly_income) * 100, 2)

    cashflow = calculate_remaining_cashflow(
        monthly_income, essential_expenses, existing_debt, proposed_payment
    )
    emergency_months = calculate_emergency_fund_coverage(savings, essential_expenses)

    # Generate contextual warnings (analytical, not prescriptive)
    if dti is not None and dti > 40:
        warnings.append(
            f"Total debt payments represent {dti}% of income. "
            "Many financial guidelines suggest keeping this below 36-43%."
        )
    elif dti is not None and dti > 36:
        warnings.append(
            f"Total debt payments represent {dti}% of income. "
            "This is approaching levels that some guidelines flag for review."
        )

    if cashflow < 0:
        warnings.append(
            f"Projected monthly cash flow is negative (${cashflow:,.2f}). "
            "Expenses and obligations exceed income."
        )
    elif cashflow < monthly_income * 0.1:
        warnings.append(
            f"Remaining cash flow (${cashflow:,.2f}) is less than 10% of income. "
            "Limited buffer for unexpected expenses."
        )

    if emergency_months is not None and emergency_months < 3:
        warnings.append(
            f"Emergency fund covers approximately {emergency_months} months of expenses. "
            "Financial guidelines often recommend 3-6 months."
        )

    if payment_to_income is not None and payment_to_income > 28:
        warnings.append(
            f"Proposed payment is {payment_to_income}% of income. "
            "This is a significant portion of monthly income."
        )

    # Assessment summary
    if cashflow < 0:
        assessment = "The proposed payment may not be affordable based on the provided financial information."
    elif len(warnings) >= 3:
        assessment = "Multiple financial indicators suggest careful review before committing to this obligation."
    elif len(warnings) >= 1:
        assessment = "Some indicators warrant attention. Review the specific warnings for details."
    else:
        assessment = "Based on the provided information, the financial indicators are within commonly referenced ranges."

    return AffordabilityResult(
        dti_ratio=dti,
        payment_to_income=payment_to_income,
        remaining_cashflow=cashflow,
        emergency_fund_months=emergency_months,
        total_monthly_obligations=round(total_debt, 2),
        assessment=assessment,
        warnings=warnings,
    )
