"""Financial API router: profile, repayment calculator, stress tests."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.financial_profile import FinancialProfile
from app.models.stress_test import StressTest as StressTestModel
from app.api.financial.schemas import (
    FinancialProfileResponse, UpdateProfileRequest,
    RepaymentRequest, RepaymentResponse,
    AffordabilityResponse,
    StressTestRequest, StressTestResponse,
)
from app.risk_engine.repayment_calculator import (
    calculate_monthly_payment, calculate_amortization_schedule,
)
from app.risk_engine.financial_risk import calculate_affordability
from app.risk_engine.stress_test_engine import (
    run_income_reduction, run_unexpected_expense,
    run_expense_increase, run_late_payment,
)

router = APIRouter(tags=["Financial"])


@router.get("/profile", response_model=FinancialProfileResponse | None)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current user's financial profile."""
    result = await db.execute(
        select(FinancialProfile).where(FinancialProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        return None
    return profile


@router.put("/profile", response_model=FinancialProfileResponse)
async def update_profile(
    body: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update the user's financial profile."""
    result = await db.execute(
        select(FinancialProfile).where(FinancialProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if profile:
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
    else:
        profile = FinancialProfile(
            user_id=current_user.id,
            **body.model_dump(exclude_unset=True),
        )
        db.add(profile)

    await db.commit()
    await db.refresh(profile)
    return profile


@router.post("/repayment/calculate", response_model=RepaymentResponse)
async def calculate_repayment(
    body: RepaymentRequest,
    current_user: User = Depends(get_current_user),
):
    """Calculate loan repayment details using deterministic formulas."""
    try:
        result = calculate_monthly_payment(
            principal=body.principal,
            annual_rate=body.annual_rate,
            term_months=body.term_months,
            fees=body.fees,
        )
        schedule = calculate_amortization_schedule(
            principal=body.principal,
            annual_rate=body.annual_rate,
            term_months=body.term_months,
        )
        return RepaymentResponse(
            monthly_payment=result.monthly_payment,
            total_interest=result.total_interest,
            total_repayment=result.total_repayment,
            effective_rate=result.effective_rate,
            amortization_schedule=[
                {
                    "month": row.month,
                    "payment": row.payment,
                    "principal_portion": row.principal_portion,
                    "interest_portion": row.interest_portion,
                    "remaining_balance": row.remaining_balance,
                }
                for row in schedule
            ],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/affordability", response_model=AffordabilityResponse)
async def get_affordability(
    proposed_payment: float = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate affordability based on user's financial profile."""
    result = await db.execute(
        select(FinancialProfile).where(FinancialProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Financial profile required. Please set up your profile first.",
        )
    if not profile.monthly_income:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Monthly income is required for affordability calculation.",
        )

    affordability = calculate_affordability(
        monthly_income=profile.monthly_income,
        essential_expenses=profile.essential_expenses or 0,
        existing_debt=profile.existing_debt_payments or 0,
        proposed_payment=proposed_payment,
        savings=profile.savings or 0,
    )

    return AffordabilityResponse(
        dti_ratio=affordability.dti_ratio,
        payment_to_income=affordability.payment_to_income,
        remaining_cashflow=affordability.remaining_cashflow,
        emergency_fund_months=affordability.emergency_fund_months,
        total_monthly_obligations=affordability.total_monthly_obligations,
        assessment=affordability.assessment,
        warnings=affordability.warnings,
    )


@router.post("/stress-tests", response_model=StressTestResponse, status_code=status.HTTP_201_CREATED)
async def create_stress_test(
    body: StressTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run a financial stress test scenario."""
    profile_result = await db.execute(
        select(FinancialProfile).where(FinancialProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile or not profile.monthly_income:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Financial profile with income is required for stress testing.",
        )

    params = body.parameters
    proposed = params.get("proposed_payment", 0)

    if body.scenario_type == "income_reduction":
        result = run_income_reduction(
            monthly_income=profile.monthly_income,
            essential_expenses=profile.essential_expenses or 0,
            existing_debt=profile.existing_debt_payments or 0,
            proposed_payment=proposed,
            reduction_pct=params.get("reduction_pct", 20),
        )
    elif body.scenario_type == "unexpected_expense":
        result = run_unexpected_expense(
            monthly_income=profile.monthly_income,
            essential_expenses=profile.essential_expenses or 0,
            existing_debt=profile.existing_debt_payments or 0,
            proposed_payment=proposed,
            expense_amount=params.get("expense_amount", 1000),
        )
    elif body.scenario_type == "expense_increase":
        result = run_expense_increase(
            monthly_income=profile.monthly_income,
            essential_expenses=profile.essential_expenses or 0,
            existing_debt=profile.existing_debt_payments or 0,
            proposed_payment=proposed,
            increase_pct=params.get("increase_pct", 15),
        )
    elif body.scenario_type == "late_payment":
        result = run_late_payment(
            monthly_income=profile.monthly_income,
            essential_expenses=profile.essential_expenses or 0,
            existing_debt=profile.existing_debt_payments or 0,
            proposed_payment=proposed,
            late_fee=params.get("late_fee", 50),
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown scenario type.")

    stress_test = StressTestModel(
        user_id=current_user.id,
        document_id=body.document_id,
        scenario_type=result.scenario_type,
        parameters=body.parameters,
        baseline_cashflow=result.baseline_cashflow,
        stressed_cashflow=result.stressed_cashflow,
        impact_amount=result.impact_amount,
        impact_percentage=result.impact_percentage,
        assumptions=result.assumptions,
        suggestions=result.suggestions,
    )
    db.add(stress_test)
    await db.commit()
    await db.refresh(stress_test)
    return stress_test


@router.get("/stress-tests", response_model=list[StressTestResponse])
async def list_stress_tests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's stress test results."""
    result = await db.execute(
        select(StressTestModel)
        .where(StressTestModel.user_id == current_user.id)
        .order_by(StressTestModel.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()
