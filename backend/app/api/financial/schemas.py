"""Financial profile and calculation schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class FinancialProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    monthly_income: float | None = None
    income_basis: str | None = None
    employment_type: str | None = None
    income_stability: str | None = None
    essential_expenses: float | None = None
    existing_debt_payments: float | None = None
    savings: float | None = None
    dependents: int | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    monthly_income: float | None = None
    income_basis: str | None = None
    employment_type: str | None = None
    income_stability: str | None = None
    essential_expenses: float | None = None
    existing_debt_payments: float | None = None
    savings: float | None = None
    dependents: int | None = None


class RepaymentRequest(BaseModel):
    principal: float = Field(..., gt=0)
    annual_rate: float = Field(..., ge=0)
    term_months: int = Field(..., gt=0)
    fees: float = Field(default=0, ge=0)


class MonthlyPaymentDetail(BaseModel):
    monthly_payment: float
    total_interest: float
    total_repayment: float
    effective_rate: float | None = None


class AmortizationRow(BaseModel):
    month: int
    payment: float
    principal_portion: float
    interest_portion: float
    remaining_balance: float


class RepaymentResponse(BaseModel):
    monthly_payment: float
    total_interest: float
    total_repayment: float
    effective_rate: float | None = None
    amortization_schedule: list[AmortizationRow] = []


class AffordabilityResponse(BaseModel):
    dti_ratio: float | None = None
    payment_to_income: float | None = None
    remaining_cashflow: float | None = None
    emergency_fund_months: float | None = None
    total_monthly_obligations: float | None = None
    assessment: str = ""
    warnings: list[str] = []


class StressTestRequest(BaseModel):
    scenario_type: str = Field(
        ...,
        pattern=r"^(income_reduction|unexpected_expense|expense_increase|late_payment|debt_increase)$",
    )
    parameters: dict = Field(default_factory=dict)
    document_id: uuid.UUID | None = None


class StressTestResponse(BaseModel):
    id: uuid.UUID
    scenario_type: str
    parameters: dict
    baseline_cashflow: float | None = None
    stressed_cashflow: float | None = None
    impact_amount: float | None = None
    impact_percentage: float | None = None
    assumptions: dict | None = None
    suggestions: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
