"""Document schemas - fixed imports."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    name: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: uuid.UUID
    name: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    page_count: int | None = None
    language: str | None = None
    country: str | None = None
    document_type: str | None = None
    purpose: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int


class StatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    error_message: str | None = None
    page_count: int | None = None

    model_config = {"from_attributes": True}


class ClauseResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    page_number: int | None = None
    clause_index: int | None = None
    original_text: str
    normalized_text: str | None = None
    language: str | None = None
    clause_heading: str | None = None
    clause_type: str | None = None
    extracted_values: dict[str, Any] | None = None
    bounding_box: dict[str, Any] | None = None
    extraction_confidence: float | None = None

    model_config = {"from_attributes": True}


class FindingResponse(BaseModel):
    id: uuid.UUID
    clause_id: uuid.UUID | None = None
    document_id: uuid.UUID
    severity: str
    classification: str | None = None
    explanation: str | None = None
    why_it_matters: str | None = None
    confidence: float | None = None
    risk_contribution: float | None = None
    evidence: str | None = None
    source_reference: str | None = None
    recommended_action: str | None = None

    model_config = {"from_attributes": True}


class RiskAssessmentResponse(BaseModel):
    overall_score: float | None = None
    document_risk_score: float | None = None
    financial_risk_score: float | None = None
    fairness_score: float | None = None
    risk_summary: str | None = None
    risk_factors: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class AnalysisResponse(BaseModel):
    document: DocumentResponse
    clauses: list[ClauseResponse] = []
    findings: list[FindingResponse] = []
    risk_assessment: RiskAssessmentResponse | None = None
