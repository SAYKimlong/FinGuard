"""Stress test model."""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class StressTest(Base):
    __tablename__ = "stress_tests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    scenario_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    baseline_cashflow: Mapped[float] = mapped_column(Float, nullable=True)
    stressed_cashflow: Mapped[float] = mapped_column(Float, nullable=True)
    impact_amount: Mapped[float] = mapped_column(Float, nullable=True)
    impact_percentage: Mapped[float] = mapped_column(Float, nullable=True)
    assumptions: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    suggestions: Mapped[dict] = mapped_column(JSONB, nullable=True, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="stress_tests")
