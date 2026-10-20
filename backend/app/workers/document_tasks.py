"""Document processing Celery tasks.

Pipeline: validate -> extract -> detect_language -> segment -> analyze -> calculate -> report
"""

import logging
import json
import re
from uuid import UUID

from app.workers.celery_app import celery_app
from app.config import settings

logger = logging.getLogger(__name__)


def get_sync_session():
    """Create a synchronous database session for Celery tasks."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(settings.DATABASE_URL_SYNC)
    Session = sessionmaker(bind=engine)
    return Session()


def update_document_status(session, doc_id: str, status: str, error: str = None, **kwargs):
    """Update document status in the database."""
    from app.models.document import Document
    doc = session.query(Document).filter(Document.id == UUID(doc_id)).first()
    if doc:
        doc.status = status
        if error:
            doc.error_message = error
        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        session.commit()


@celery_app.task(bind=True, max_retries=2)
def process_document_task(self, document_id: str):
    """Main document processing pipeline."""
    session = get_sync_session()

    try:
        from app.models.document import Document, DocumentPage, DocumentStatus
        from app.models.clause import Clause, ClauseType
        from app.models.finding import Finding, Severity, Classification
        from app.models.risk_assessment import RiskAssessment

        doc = session.query(Document).filter(Document.id == UUID(document_id)).first()
        if not doc:
            logger.error(f"Document {document_id} not found")
            return

        # Step 1: Extract text
        update_document_status(session, document_id, DocumentStatus.EXTRACTING.value)

        file_type = str(doc.file_type)

        if file_type == "pdf":
            from app.ocr.extractor import extract_pdf_text
            extraction = extract_pdf_text(doc.file_path)
        elif file_type == "docx":
            from app.ocr.extractor import extract_docx_text
            extraction = extract_docx_text(doc.file_path)
        else:
            # Image files would need OCR
            update_document_status(
                session, document_id, DocumentStatus.COMPLETED.value,
                page_count=0,
            )
            return

        if not extraction.pages:
            update_document_status(
                session, document_id, DocumentStatus.FAILED.value,
                error="No text could be extracted from the document.",
            )
            return

        # Save page data
        doc.page_count = extraction.total_pages
        for page_data in extraction.pages:
            page = DocumentPage(
                document_id=doc.id,
                page_number=page_data.page_number,
                width=page_data.width,
                height=page_data.height,
                text_content=page_data.text,
            )
            session.add(page)
        session.commit()

        # Step 2: Detect language
        update_document_status(session, document_id, DocumentStatus.SEGMENTING.value)

        full_text = "\n".join(p.text for p in extraction.pages if p.text)

        from app.ocr.extractor import detect_language
        detected_lang = detect_language(full_text)
        doc.language = detected_lang if detected_lang != "unknown" else "en"
        session.commit()

        # Step 3: Segment clauses
        clauses_data = segment_clauses(full_text, extraction.pages)

        for i, clause_data in enumerate(clauses_data):
            clause = Clause(
                document_id=doc.id,
                page_number=clause_data.get("page_number", 1),
                clause_index=i + 1,
                original_text=clause_data["text"],
                normalized_text=clause_data["text"].lower().strip(),
                language=detected_lang,
                clause_heading=clause_data.get("heading"),
                clause_type=clause_data.get("type", ClauseType.OTHER),
                extracted_values=clause_data.get("values", {}),
                extraction_confidence=clause_data.get("confidence", 0.8),
            )
            session.add(clause)
        session.commit()

        # Step 4: Analyze and create findings
        update_document_status(session, document_id, DocumentStatus.ANALYZING.value)

        clauses = session.query(Clause).filter(Clause.document_id == doc.id).all()
        findings_data = analyze_clauses_deterministic(clauses)

        for finding_data in findings_data:
            finding = Finding(
                clause_id=finding_data.get("clause_id"),
                document_id=doc.id,
                severity=finding_data["severity"],
                classification=finding_data["classification"],
                explanation=finding_data["explanation"],
                why_it_matters=finding_data.get("why_it_matters"),
                confidence=finding_data.get("confidence", 0.7),
                risk_contribution=finding_data.get("risk_contribution"),
                evidence=finding_data.get("evidence"),
                recommended_action=finding_data.get("recommended_action"),
            )
            session.add(finding)
        session.commit()

        # Step 5: Calculate risk scores
        update_document_status(session, document_id, DocumentStatus.CALCULATING.value)

        findings = session.query(Finding).filter(Finding.document_id == doc.id).all()
        risk_score = calculate_document_risk(findings)

        risk_assessment = RiskAssessment(
            document_id=doc.id,
            overall_score=risk_score["overall"],
            document_risk_score=risk_score["document"],
            financial_risk_score=risk_score["financial"],
            fairness_score=risk_score["fairness"],
            risk_summary=risk_score["summary"],
            risk_factors=risk_score["factors"],
        )
        session.add(risk_assessment)
        session.commit()

        # Done
        update_document_status(session, document_id, DocumentStatus.COMPLETED.value)
        logger.info(f"Document {document_id} processing completed successfully")

    except Exception as e:
        logger.error(f"Document processing failed: {e}", exc_info=True)
        update_document_status(
            session, document_id, "failed",
            error=f"Processing failed: {str(e)[:500]}",
        )
        raise
    finally:
        session.close()


def segment_clauses(full_text: str, pages: list) -> list[dict]:
    """Segment document text into clauses using pattern matching."""
    from app.models.clause import ClauseType

    clauses = []
    # Common clause heading patterns
    patterns = [
        (r'(?i)(loan\s+amount|principal)', ClauseType.PRINCIPAL),
        (r'(?i)(interest\s+rate|annual\s+percentage|apr)', ClauseType.INTEREST_RATE),
        (r'(?i)(fee|charge|commission|cost|processing)', ClauseType.FEES),
        (r'(?i)(repayment|payment\s+schedule|installment|monthly\s+payment)', ClauseType.REPAYMENT),
        (r'(?i)(late\s+payment|overdue|penalty|default\s+interest)', ClauseType.LATE_PENALTY),
        (r'(?i)(early\s+repayment|prepayment|early\s+termination)', ClauseType.EARLY_REPAYMENT),
        (r'(?i)(collateral|security|pledge|guarantee)', ClauseType.COLLATERAL),
        (r'(?i)(default|acceleration|breach)', ClauseType.DEFAULT_CONDITIONS),
        (r'(?i)(insurance|coverage)', ClauseType.INSURANCE),
        (r'(?i)(guarantor|co-signer)', ClauseType.GUARANTOR),
        (r'(?i)(termination|cancellation)', ClauseType.TERMINATION),
        (r'(?i)(dispute|arbitration|jurisdiction|governing\s+law)', ClauseType.DISPUTE),
    ]

    # Split by numbered sections or line breaks
    sections = re.split(r'\n\s*(?=\d+[\.\)]\s|\b(?:Section|Article|Clause)\s+\d+)', full_text)

    if len(sections) <= 1:
        # Try splitting by double newlines
        sections = re.split(r'\n\s*\n', full_text)

    current_page = 1
    char_pos = 0

    for section in sections:
        section = section.strip()
        if len(section) < 10:
            continue

        # Determine clause type
        clause_type = ClauseType.OTHER
        for pattern, ctype in patterns:
            if re.search(pattern, section):
                clause_type = ctype
                break

        # Extract heading
        lines = section.split('\n')
        heading = lines[0][:100] if lines else None

        # Extract financial values
        values = extract_financial_values(section)

        # Determine page number (approximate)
        for page in pages:
            if section[:50] in (page.text or ""):
                current_page = page.page_number
                break

        clauses.append({
            "text": section,
            "heading": heading,
            "type": clause_type,
            "page_number": current_page,
            "values": values,
            "confidence": 0.75,
        })

    return clauses


def extract_financial_values(text: str) -> dict:
    """Extract financial values from clause text."""
    values = {}

    # Currency amounts
    amounts = re.findall(r'\$\s*([\d,]+(?:\.\d{2})?)', text)
    if amounts:
        values["amounts"] = [float(a.replace(",", "")) for a in amounts]

    # Percentages
    pcts = re.findall(r'([\d.]+)\s*%', text)
    if pcts:
        values["percentages"] = [float(p) for p in pcts]

    # Months/years duration
    months = re.findall(r'(\d+)\s*month', text, re.IGNORECASE)
    years = re.findall(r'(\d+)\s*year', text, re.IGNORECASE)
    if months:
        values["duration_months"] = int(months[0])
    if years:
        values["duration_years"] = int(years[0])

    return values


def analyze_clauses_deterministic(clauses) -> list[dict]:
    """Analyze clauses using deterministic rules to generate findings."""
    from app.models.finding import Severity, Classification
    from app.models.clause import ClauseType

    findings = []

    for clause in clauses:
        text_lower = clause.original_text.lower()
        values = clause.extracted_values or {}

        # High interest rate detection
        if clause.clause_type == ClauseType.INTEREST_RATE:
            pcts = values.get("percentages", [])
            for pct in pcts:
                if pct > 25:
                    findings.append({
                        "clause_id": clause.id,
                        "severity": Severity.HIGH_RISK,
                        "classification": Classification.HIGH_FINANCIAL_EXPOSURE,
                        "explanation": f"The stated interest rate of {pct}% is significantly above typical market rates for personal loans.",
                        "why_it_matters": "Higher interest rates increase the total cost of borrowing substantially over the loan term.",
                        "confidence": 0.85,
                        "risk_contribution": 0.3,
                        "evidence": clause.original_text[:300],
                        "recommended_action": "Compare this rate with current market rates for similar loan products.",
                    })
                elif pct > 15:
                    findings.append({
                        "clause_id": clause.id,
                        "severity": Severity.ATTENTION,
                        "classification": Classification.NEEDS_ATTENTION,
                        "explanation": f"Interest rate of {pct}% is above the median range for personal loans.",
                        "why_it_matters": "Consider comparing with other offers to ensure competitiveness.",
                        "confidence": 0.8,
                        "risk_contribution": 0.15,
                        "evidence": clause.original_text[:300],
                        "recommended_action": "Compare with other loan offers and check if you qualify for better rates.",
                    })

        # Late payment penalty analysis
        if clause.clause_type == ClauseType.LATE_PENALTY:
            pcts = values.get("percentages", [])
            for pct in pcts:
                if pct >= 5:
                    findings.append({
                        "clause_id": clause.id,
                        "severity": Severity.CONCERNING,
                        "classification": Classification.HIGH_FINANCIAL_EXPOSURE,
                        "explanation": f"Late payment penalty of {pct}% is significant and could compound quickly.",
                        "why_it_matters": "High late fees can create a debt spiral if payments are missed.",
                        "confidence": 0.85,
                        "risk_contribution": 0.25,
                        "evidence": clause.original_text[:300],
                        "recommended_action": "Understand exactly when late fees apply and how they're calculated.",
                    })

            if "compound" in text_lower:
                findings.append({
                    "clause_id": clause.id,
                    "severity": Severity.HIGH_RISK,
                    "classification": Classification.POTENTIALLY_UNFAIR,
                    "explanation": "Late payment fees appear to compound, which can rapidly increase the amount owed.",
                    "why_it_matters": "Compounding penalties can make it very difficult to recover from missed payments.",
                    "confidence": 0.8,
                    "risk_contribution": 0.3,
                    "evidence": clause.original_text[:300],
                    "recommended_action": "Ask the lender to clarify the compounding mechanism and consider negotiating a cap.",
                })

        # Acceleration clause
        if "acceleration" in text_lower or "full balance due" in text_lower:
            findings.append({
                "clause_id": clause.id,
                "severity": Severity.CONCERNING,
                "classification": Classification.HIGH_FINANCIAL_EXPOSURE,
                "explanation": "The agreement contains an acceleration clause that may require full repayment of the remaining balance upon default.",
                "why_it_matters": "If triggered, you may need to repay the entire remaining loan immediately.",
                "confidence": 0.8,
                "risk_contribution": 0.2,
                "evidence": clause.original_text[:300],
                "recommended_action": "Clarify exactly what conditions trigger the acceleration clause.",
            })

        # Mandatory arbitration
        if "arbitration" in text_lower and ("mandatory" in text_lower or "binding" in text_lower):
            findings.append({
                "clause_id": clause.id,
                "severity": Severity.ATTENTION,
                "classification": Classification.NEEDS_ATTENTION,
                "explanation": "The agreement requires mandatory binding arbitration for disputes.",
                "why_it_matters": "This may limit your ability to pursue disputes through courts.",
                "confidence": 0.85,
                "risk_contribution": 0.1,
                "evidence": clause.original_text[:300],
                "recommended_action": "Understand the arbitration process and any associated costs.",
            })

        # Ambiguous terms
        vague_phrases = ["at our discretion", "may be subject to change", "as determined by",
                        "reserves the right", "may adjust", "subject to terms"]
        for phrase in vague_phrases:
            if phrase in text_lower:
                findings.append({
                    "clause_id": clause.id,
                    "severity": Severity.ATTENTION,
                    "classification": Classification.MISSING_INFORMATION,
                    "explanation": f"This clause contains ambiguous language (\"{phrase}\") that could allow the lender to modify terms.",
                    "why_it_matters": "Vague terms can lead to unexpected changes in your loan conditions.",
                    "confidence": 0.7,
                    "risk_contribution": 0.1,
                    "evidence": clause.original_text[:300],
                    "recommended_action": "Ask for specific, measurable terms before signing.",
                })
                break

        # Variable rate without cap
        if clause.clause_type == ClauseType.INTEREST_RATE and "variable" in text_lower:
            if "cap" not in text_lower and "ceiling" not in text_lower and "maximum" not in text_lower:
                findings.append({
                    "clause_id": clause.id,
                    "severity": Severity.CONCERNING,
                    "classification": Classification.HIGH_FINANCIAL_EXPOSURE,
                    "explanation": "The interest rate is variable but no rate cap or ceiling is mentioned.",
                    "why_it_matters": "Without a cap, your interest rate could increase substantially over time.",
                    "confidence": 0.75,
                    "risk_contribution": 0.25,
                    "evidence": clause.original_text[:300],
                    "recommended_action": "Ask the lender to specify a maximum interest rate.",
                })

        # Wage assignment
        if "wage assignment" in text_lower or "salary deduction" in text_lower:
            findings.append({
                "clause_id": clause.id,
                "severity": Severity.HIGH_RISK,
                "classification": Classification.SUSPICIOUS_INDICATOR,
                "explanation": "The agreement includes a wage assignment clause.",
                "why_it_matters": "This allows the lender to take money directly from your salary if you default.",
                "confidence": 0.9,
                "risk_contribution": 0.3,
                "evidence": clause.original_text[:300],
                "recommended_action": "Check if wage assignments are permitted in your jurisdiction and understand the implications.",
            })

        # Auto-renewal
        if "auto-renew" in text_lower or "automatic renewal" in text_lower or "automatically renewed" in text_lower:
            findings.append({
                "clause_id": clause.id,
                "severity": Severity.ATTENTION,
                "classification": Classification.NEEDS_ATTENTION,
                "explanation": "The agreement contains an automatic renewal clause.",
                "why_it_matters": "The loan may automatically renew at the end of the term unless you actively cancel.",
                "confidence": 0.85,
                "risk_contribution": 0.15,
                "evidence": clause.original_text[:300],
                "recommended_action": "Note the renewal date and cancellation deadline.",
            })

    return findings


def calculate_document_risk(findings) -> dict:
    """Calculate overall risk score from findings."""
    if not findings:
        return {
            "overall": 0.0,
            "document": 0.0,
            "financial": 0.0,
            "fairness": 100.0,
            "summary": "No significant findings identified.",
            "factors": {},
        }

    severity_weights = {
        "info": 0,
        "attention": 5,
        "concerning": 15,
        "high_risk": 30,
        "suspicious": 40,
        "missing": 10,
    }

    total_risk = 0
    financial_risk = 0
    fairness_deductions = 0
    factors = {}

    for finding in findings:
        sev = finding.severity.value if hasattr(finding.severity, 'value') else str(finding.severity)
        weight = severity_weights.get(sev, 5)
        total_risk += weight

        contribution = finding.risk_contribution or 0
        financial_risk += contribution * 100

        cls = finding.classification.value if hasattr(finding.classification, 'value') else str(finding.classification)
        if cls in ("potentially_unfair", "suspicious_indicator"):
            fairness_deductions += 10

        factors[sev] = factors.get(sev, 0) + 1

    # Normalize scores (0-100)
    overall = min(total_risk, 100)
    doc_risk = min(overall * 0.6, 100)
    fin_risk = min(financial_risk, 100)
    fairness = max(100 - fairness_deductions, 0)

    # Summary
    if overall < 20:
        summary = "Low risk. The document appears straightforward with standard terms."
    elif overall < 50:
        summary = "Moderate risk. Some clauses need attention before committing."
    elif overall < 75:
        summary = "Elevated risk. Multiple concerning findings identified. Careful review recommended."
    else:
        summary = "High risk. Significant concerns found. Professional review strongly recommended before signing."

    return {
        "overall": round(overall, 1),
        "document": round(doc_risk, 1),
        "financial": round(fin_risk, 1),
        "fairness": round(fairness, 1),
        "summary": summary,
        "factors": factors,
    }
