"""Knowledge base models for RAG."""

import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, DateTime, Date, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.database import Base


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    country: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    organization: Mapped[str] = mapped_column(String(500), nullable=True)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    url: Mapped[str] = mapped_column(String(2000), nullable=True)
    publication_date: Mapped[date] = mapped_column(Date, nullable=True)
    last_verified: Mapped[date] = mapped_column(Date, nullable=True)
    source_type: Mapped[str] = mapped_column(String(100), nullable=True)  # regulation, guideline, consumer_protection
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    passages = relationship("KnowledgePassage", back_populates="source", cascade="all, delete-orphan")


class KnowledgePassage(Base):
    __tablename__ = "knowledge_passages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    section_reference: Mapped[str] = mapped_column(String(500), nullable=True)
    embedding = mapped_column(Vector(768), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    source = relationship("KnowledgeSource", back_populates="passages")
