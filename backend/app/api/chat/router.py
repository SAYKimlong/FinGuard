"""Chat router: clause-specific Q&A endpoint."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.clause import Clause
from app.models.finding import Finding
from app.api.chat.schemas import ClauseQuestionRequest, ClauseAnswerResponse
from app.ai.llm_provider import get_llm_provider

router = APIRouter(tags=["Chat"])


@router.post("/clause", response_model=ClauseAnswerResponse)
async def ask_about_clause(
    body: ClauseQuestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ask a question about a specific clause in a document."""
    # Fetch the clause
    clause_result = await db.execute(
        select(Clause).where(Clause.id == body.clause_id)
    )
    clause = clause_result.scalar_one_or_none()
    if not clause:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clause not found.")

    # Verify document ownership
    doc_result = await db.execute(
        select(Document).where(
            Document.id == clause.document_id,
            Document.user_id == current_user.id,
        )
    )
    document = doc_result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # Fetch related findings for context
    findings_result = await db.execute(
        select(Finding).where(Finding.clause_id == clause.id)
    )
    findings = findings_result.scalars().all()

    # Build context for the LLM
    findings_context = ""
    if findings:
        findings_context = "\n\nExisting analysis findings for this clause:\n"
        for f in findings:
            sev = f.severity.value if hasattr(f.severity, 'value') else str(f.severity)
            findings_context += f"- [{sev}] {f.explanation}\n"

    clause_type_str = clause.clause_type.value if hasattr(clause.clause_type, 'value') else str(clause.clause_type)

    prompt = f"""You are a financial document analysis assistant. Answer the user's question about the following clause from a financial agreement.

CLAUSE (Page {clause.page_number}):
---
{clause.original_text}
---

Clause Type: {clause_type_str}
{findings_context}

USER QUESTION: {body.question}

INSTRUCTIONS:
- Answer based only on the information in the clause and any analysis findings.
- If the clause doesn't contain enough information to answer, say so clearly.
- Do not provide legal advice. Suggest the user consult a professional for definitive answers.
- Keep the answer clear and concise.
- If financial values are mentioned, preserve them exactly as stated.
- Respond in {body.language if body.language != 'auto' else 'English'}.
"""

    try:
        llm = get_llm_provider()
        answer = await llm.generate(
            prompt=prompt,
            system_prompt="You are FinGuard, a financial document analysis assistant. You help users understand financial agreements. You do not provide legal or financial advice.",
            temperature=0.3,
            max_tokens=500,
        )

        return ClauseAnswerResponse(
            clause_id=clause.id,
            question=body.question,
            answer=answer,
            confidence=0.7,
            sources=[],
        )
    except Exception:
        # Fallback if LLM is unavailable
        fallback_answer = (
            f'I found the clause on page {clause.page_number}: "{clause.original_text[:200]}..."\n\n'
        )
        if findings:
            fallback_answer += "Based on the analysis:\n"
            for f in findings:
                fallback_answer += f"• {f.explanation}\n"
        else:
            fallback_answer += "No detailed analysis is available for this clause yet."

        fallback_answer += "\n\n⚠️ Note: The AI assistant is currently unavailable. This is a summary based on extracted data."

        return ClauseAnswerResponse(
            clause_id=clause.id,
            question=body.question,
            answer=fallback_answer,
            confidence=0.3,
            sources=[],
        )
