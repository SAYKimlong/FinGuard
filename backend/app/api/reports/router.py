"""Reports router: generate full analysis reports."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.clause import Clause
from app.models.finding import Finding
from app.models.risk_assessment import RiskAssessment
from app.api.documents.schemas import (
    DocumentResponse, ClauseResponse, FindingResponse, RiskAssessmentResponse,
)
from app.api.reports.schemas import FullReportResponse

router = APIRouter(tags=["Reports"])


@router.get("/{document_id}", response_model=FullReportResponse)
async def get_report(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a full analysis report for a document."""
    # Verify ownership
    doc_result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    document = doc_result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # Clauses
    clauses_result = await db.execute(
        select(Clause).where(Clause.document_id == document_id).order_by(Clause.page_number, Clause.clause_index)
    )
    clauses = clauses_result.scalars().all()

    # Findings
    findings_result = await db.execute(
        select(Finding).where(Finding.document_id == document_id)
    )
    findings = findings_result.scalars().all()

    # Risk
    risk_result = await db.execute(
        select(RiskAssessment).where(RiskAssessment.document_id == document_id)
    )
    risk = risk_result.scalar_one_or_none()

    # Summary stats
    severity_counts = {}
    for f in findings:
        sev = f.severity.value if hasattr(f.severity, 'value') else str(f.severity)
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    return FullReportResponse(
        document=DocumentResponse.model_validate(document),
        clauses=[ClauseResponse.model_validate(c) for c in clauses],
        findings=[FindingResponse.model_validate(f) for f in findings],
        risk_assessment=RiskAssessmentResponse.model_validate(risk) if risk else None,
        total_clauses=len(clauses),
        total_findings=len(findings),
        severity_distribution=severity_counts,
    )
