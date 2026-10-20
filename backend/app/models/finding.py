"""Finding model for analysis results."""

import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Float, Text, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Severity(str, enum.Enum):
    INFO = "info"
    ATTENTION = "attention"
    CONCERNING = "concerning"
    HIGH_RISK = "high_risk"
    SUSPICIOUS = "suspicious"
    MISSING = "missing"


class Classification(str, enum.Enum):
    NO_CONCERN = "no_concern"
    NEEDS_ATTENTION = "needs_attention"
    POTENTIALLY_UNFAIR = "potentially_unfair"
    POTENTIALLY_NON_COMPLIANT = "potentially_non_compliant"
    HIGH_FINANCIAL_EXPOSURE = "high_financial_exposure"
    SUSPICIOUS_INDICATOR = "suspicious_indicator"
    MISSING_INFORMATION = "missing_information"
    UNABLE_TO_DETERMINE = "unable_to_determine"


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    clause_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clauses.id", ondelete="CASCADE"), nullable=True, index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity), default=Severity.INFO, nullable=False
    )
    classification: Mapped[Classification] = mapped_column(
        Enum(Classification), default=Classification.NO_CONCERN, nullable=False
    )
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    why_it_matters: Mapped[str] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    risk_contribution: Mapped[float] = mapped_column(Float, nullable=True)
    evidence: Mapped[str] = mapped_column(Text, nullable=True)
    source_reference: Mapped[str] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    clause = relationship("Clause", back_populates="findings")
    document = relationship("Document", back_populates="findings")
