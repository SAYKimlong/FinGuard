"""Report schemas."""

from typing import Any
from pydantic import BaseModel
from app.api.documents.schemas import (
    DocumentResponse, ClauseResponse, FindingResponse, RiskAssessmentResponse,
)


class FullReportResponse(BaseModel):
    document: DocumentResponse
    clauses: list[ClauseResponse] = []
    findings: list[FindingResponse] = []
    risk_assessment: RiskAssessmentResponse | None = None
    total_clauses: int = 0
    total_findings: int = 0
    severity_distribution: dict[str, int] = {}
