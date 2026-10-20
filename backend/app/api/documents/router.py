"""Documents API router: upload, list, get, delete, status, analysis, clauses."""

import os
import uuid
import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.models.clause import Clause
from app.models.finding import Finding
from app.models.risk_assessment import RiskAssessment
from app.config import settings
from app.api.documents.schemas import (
    DocumentUploadResponse, DocumentResponse, DocumentListResponse,
    StatusResponse, ClauseResponse, FindingResponse,
    RiskAssessmentResponse, AnalysisResponse,
)

router = APIRouter(tags=["Documents"])

# Allowed file types and their magic bytes
ALLOWED_EXTENSIONS = {
    ".pdf": "pdf", ".docx": "docx", ".jpg": "jpg", ".jpeg": "jpg", ".png": "png",
}

MAGIC_BYTES = {
    "pdf": b"%PDF",
    "png": b"\x89PNG",
    "jpg": b"\xff\xd8\xff",
    "docx": b"PK\x03\x04",
}


def sanitize_filename(filename: str) -> str:
    """Remove potentially dangerous characters from filename."""
    name = os.path.basename(filename)
    name = re.sub(r'[^\w\s\-.]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name[:255] if name else "unnamed_document"


def validate_file_extension(filename: str) -> str:
    """Validate and return the file type string from extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS.keys())}",
        )
    return ALLOWED_EXTENSIONS[ext]


def validate_magic_bytes(content: bytes, expected_type: str) -> bool:
    """Validate file content against expected magic bytes."""
    expected = MAGIC_BYTES.get(expected_type)
    if expected:
        return content[:len(expected)] == expected
    return True


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    name: str = Form(...),
    document_type: str = Form(default="loan_agreement"),
    language: str = Form(default="auto"),
    country: str = Form(default=""),
    purpose: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a financial document for analysis."""
    # Validate extension
    file_type = validate_file_extension(file.filename or "unknown")

    # Read and validate size
    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded.",
        )

    # Validate magic bytes
    if not validate_magic_bytes(content, file_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content does not match the expected file type.",
        )

    # Create storage path
    doc_id = uuid.uuid4()
    safe_name = sanitize_filename(file.filename or "document")
    storage_dir = Path(settings.UPLOAD_DIR) / str(current_user.id) / str(doc_id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    file_path = storage_dir / safe_name

    # Write file
    with open(file_path, "wb") as f:
        f.write(content)

    # Create database record
    document = Document(
        id=doc_id,
        user_id=current_user.id,
        name=name.strip(),
        original_filename=safe_name,
        file_path=str(file_path),
        file_type=file_type,
        file_size=len(content),
        language=language,
        country=country if country else None,
        document_type=document_type,
        purpose=purpose if purpose else None,
        status=DocumentStatus.UPLOADED,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Queue async processing task
    try:
        from app.workers.document_tasks import process_document_task
        process_document_task.delay(str(doc_id))
        document.status = DocumentStatus.QUEUED
        await db.commit()
    except Exception:
        # If Celery is unavailable, mark as uploaded (can process manually)
        pass

    return document


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the current user's documents with pagination."""
    count_query = select(func.count()).select_from(Document).where(
        Document.user_id == current_user.id
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    query = (
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    documents = result.scalars().all()

    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific document (must be owned by the current user)."""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return document


@router.get("/{document_id}/status", response_model=StatusResponse)
async def get_document_status(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check document processing status."""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return document


@router.get("/{document_id}/clauses", response_model=list[ClauseResponse])
async def get_document_clauses(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all extracted clauses for a document."""
    doc_result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    if not doc_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    result = await db.execute(
        select(Clause).where(Clause.document_id == document_id).order_by(Clause.page_number, Clause.clause_index)
    )
    return result.scalars().all()


@router.get("/{document_id}/analysis", response_model=AnalysisResponse)
async def get_document_analysis(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full analysis results for a document."""
    doc_result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    document = doc_result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    clauses_result = await db.execute(
        select(Clause).where(Clause.document_id == document_id).order_by(Clause.page_number, Clause.clause_index)
    )
    clauses = clauses_result.scalars().all()

    findings_result = await db.execute(
        select(Finding).where(Finding.document_id == document_id)
    )
    findings = findings_result.scalars().all()

    risk_result = await db.execute(
        select(RiskAssessment).where(RiskAssessment.document_id == document_id)
    )
    risk = risk_result.scalar_one_or_none()

    return AnalysisResponse(
        document=DocumentResponse.model_validate(document),
        clauses=[ClauseResponse.model_validate(c) for c in clauses],
        findings=[FindingResponse.model_validate(f) for f in findings],
        risk_assessment=RiskAssessmentResponse.model_validate(risk) if risk else None,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a document and its associated data."""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # Delete file from storage
    try:
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()
            parent = file_path.parent
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
    except Exception:
        pass

    await db.delete(document)
    await db.commit()
