"""Financial profile model."""

import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class IncomeBasis(str, enum.Enum):
    GROSS = "gross"
    NET = "net"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"


class IncomeStability(str, enum.Enum):
    STABLE = "stable"
    VARIABLE = "variable"
    SEASONAL = "seasonal"


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    monthly_income: Mapped[float] = mapped_column(Float, nullable=True)
    income_basis: Mapped[str] = mapped_column(String(10), nullable=True, default="net")
    employment_type: Mapped[str] = mapped_column(String(50), nullable=True)
    income_stability: Mapped[str] = mapped_column(String(20), nullable=True)
    essential_expenses: Mapped[float] = mapped_column(Float, nullable=True)
    existing_debt_payments: Mapped[float] = mapped_column(Float, nullable=True)
    savings: Mapped[float] = mapped_column(Float, nullable=True)
    dependents: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="financial_profile")
