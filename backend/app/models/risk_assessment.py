"""Risk assessment model."""

import uuid
from datetime import datetime
from sqlalchemy import Float, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=True)
    document_risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    financial_risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    fairness_score: Mapped[float] = mapped_column(Float, nullable=True)
    risk_summary: Mapped[str] = mapped_column(Text, nullable=True)
    risk_factors: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    document = relationship("Document", back_populates="risk_assessment")
