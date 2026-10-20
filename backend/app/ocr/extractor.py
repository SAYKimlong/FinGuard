"""Document text extraction using PyMuPDF."""

import logging
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PageExtraction:
    page_number: int
    text: str
    width: float
    height: float
    has_text: bool
    word_count: int


@dataclass
class DocumentExtraction:
    pages: list[PageExtraction] = field(default_factory=list)
    total_pages: int = 0
    total_text_length: int = 0
    needs_ocr: bool = False
    language_hint: str | None = None


def extract_pdf_text(file_path: str) -> DocumentExtraction:
    """Extract text and page geometry from a PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.error("PyMuPDF not installed. Install with: pip install pymupdf")
        return DocumentExtraction()

    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return DocumentExtraction()

    result = DocumentExtraction()

    try:
        doc = fitz.open(str(path))
        result.total_pages = len(doc)

        pages_needing_ocr = 0

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            rect = page.rect

            word_count = len(text.split()) if text.strip() else 0
            has_text = word_count > 5  # Minimum threshold for meaningful text

            page_data = PageExtraction(
                page_number=page_num + 1,
                text=text.strip(),
                width=rect.width,
                height=rect.height,
                has_text=has_text,
                word_count=word_count,
            )
            result.pages.append(page_data)
            result.total_text_length += len(text)

            if not has_text:
                pages_needing_ocr += 1

        result.needs_ocr = pages_needing_ocr > 0

        doc.close()
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return DocumentExtraction()

    return result


def extract_docx_text(file_path: str) -> DocumentExtraction:
    """Extract text from a DOCX file."""
    try:
        from docx import Document as DocxDocument
    except ImportError:
        logger.error("python-docx not installed")
        return DocumentExtraction()

    try:
        doc = DocxDocument(file_path)
        full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

        page = PageExtraction(
            page_number=1,
            text=full_text,
            width=612,  # Standard letter width in points
            height=792,
            has_text=bool(full_text.strip()),
            word_count=len(full_text.split()),
        )

        return DocumentExtraction(
            pages=[page],
            total_pages=1,
            total_text_length=len(full_text),
            needs_ocr=False,
        )
    except Exception as e:
        logger.error(f"Error extracting DOCX text: {e}")
        return DocumentExtraction()


def detect_language(text: str) -> str:
    """Detect the language of a text sample."""
    try:
        from langdetect import detect
        if len(text.strip()) < 20:
            return "unknown"
        return detect(text)
    except Exception:
        return "unknown"
