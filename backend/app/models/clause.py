"""Clause model for extracted document clauses."""

import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ClauseType(str, enum.Enum):
    PRINCIPAL = "principal"
    INTEREST_RATE = "interest_rate"
    FEES = "fees"
    REPAYMENT = "repayment"
    LATE_PENALTY = "late_penalty"
    EARLY_REPAYMENT = "early_repayment"
    COLLATERAL = "collateral"
    DEFAULT_CONDITIONS = "default_conditions"
    COLLECTIONS = "collections"
    TERM_CHANGES = "term_changes"
    INSURANCE = "insurance"
    GUARANTOR = "guarantor"
    TERMINATION = "termination"
    DISPUTE = "dispute"
    OTHER = "other"


class Clause(Base):
    __tablename__ = "clauses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    clause_index: Mapped[int] = mapped_column(Integer, nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(10), nullable=True, default="en")
    clause_heading: Mapped[str] = mapped_column(String(500), nullable=True)
    clause_type: Mapped[ClauseType] = mapped_column(
        Enum(ClauseType), default=ClauseType.OTHER, nullable=False
    )
    extracted_values: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    bounding_box: Mapped[dict] = mapped_column(JSONB, nullable=True)
    extraction_confidence: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    document = relationship("Document", back_populates="clauses")
    findings = relationship("Finding", back_populates="clause", cascade="all, delete-orphan")
