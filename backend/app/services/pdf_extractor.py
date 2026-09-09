"""
PDF Extraction Service — deterministic, page-aware text and structure extraction
for procurement tender documents using PyMuPDF.

Design Principles (Run 6A):
- Page-boundary aware: every extracted block is traceable to its original 1-indexed page.
- Deterministic text normalization: standardizes whitespace and line breaks without
  altering technical specifications, standard numbers (e.g. IS 1786:2008), grades (Fe 500),
  measurements (12 mm), voltages (450/750 V), or gazette orders (S.O. 1673(E)).
- Zero LLM / Zero OCR: image-only or encrypted PDFs are safely flagged with informative warnings.
"""
from __future__ import annotations

import io
import logging
import re
import unicodedata
from typing import BinaryIO

import pymupdf

from app.schemas.document import (
    DocumentExtractionResponse,
    DocumentMetadata,
    ExtractionStatus,
    PageExtraction,
)

logger = logging.getLogger(__name__)

# Standard Government of India tender sections (CAPP / GFR procurement manual)
KNOWN_TENDER_SECTIONS = [
    ("Notice Inviting Tender", re.compile(r"^(?:section\s+[ivx0-9]+[:\.\s-]*)?(?:notice\s+inviting\s+tender|nit|invitation\s+for\s+bids|ifb)\b", re.IGNORECASE)),
    ("Instructions to Bidders", re.compile(r"^(?:section\s+[ivx0-9]+[:\.\s-]*)?(?:instructions?\s+to\s+bidders?|itb)\b", re.IGNORECASE)),
    ("General Conditions of Contract", re.compile(r"^(?:section\s+[ivx0-9]+[:\.\s-]*)?(?:general\s+conditions?\s+of\s+contract|gcc)\b", re.IGNORECASE)),
    ("Special Conditions of Contract", re.compile(r"^(?:section\s+[ivx0-9]+[:\.\s-]*)?(?:special\s+conditions?\s+of\s+contract|scc)\b", re.IGNORECASE)),
    ("Schedule of Requirements", re.compile(r"^(?:section\s+[ivx0-9]+[:\.\s-]*)?(?:schedule\s+of\s+requirements?|scope\s+of\s+work)\b", re.IGNORECASE)),
    ("Technical Specifications", re.compile(r"^(?:section\s+[ivx0-9]+[:\.\s-]*)?(?:technical\s+specifications?|technical\s+requirements?|quality\s+assurance)\b", re.IGNORECASE)),
    ("Qualification and Evaluation Criteria", re.compile(r"^(?:section\s+[ivx0-9]+[:\.\s-]*)?(?:qualification\s+(?:and|&)\s+evaluation\s+criteria|eligibility\s+criteria)\b", re.IGNORECASE)),
    ("Financial Bid / BOQ", re.compile(r"^(?:section\s+[ivx0-9]+[:\.\s-]*)?(?:financial\s+bid|bill\s+of\s+quantities|boq|price\s+schedule)\b", re.IGNORECASE)),
    ("Standard Forms and Annexures", re.compile(r"^(?:section\s+[ivx0-9]+[:\.\s-]*)?(?:standard\s+forms?|annexures?|proforma|check\s*list)\b", re.IGNORECASE)),
]


def normalize_pdf_text(text: str) -> str:
    """
    Deterministically normalizes PDF extracted text.

    Preserves:
    - Standard numbers (IS 1786:2008, IS 2062:2011, IS 15298 (Part 2):2016)
    - Units and measurements (12 mm, 500 MPa, 450/750 V, 11 kV, 33 kV)
    - Technical grades and codes (Fe 500, Fe 500D, M10-M100)
    - Gazette and legal references (S.O. 1673(E), No. 12/2020)
    - Clause and section numbers (Clause 4.2.1, Section III)

    Handles:
    - Unicode whitespace normalization
    - Redundant horizontal space compression
    - Excessive newline normalization
    - Safe word de-hyphenation across line breaks (prose words only)
    """
    if not text:
        return ""

    # 1. Unicode normalization (NFKC decomposes compatibility chars but preserves standard chars)
    normalized = unicodedata.normalize("NFKC", text)

    # 2. Replace non-breaking and zero-width spaces with standard space
    normalized = re.sub(r"[\u00a0\u1680\u2000-\u200b\u202f\u205f\u3000\ufeff]", " ", normalized)

    # 3. Standardize curly quotes and apostrophes to standard ASCII
    normalized = normalized.replace("\u2018", "'").replace("\u2019", "'")
    normalized = normalized.replace("\u201c", '"').replace("\u201d", '"')

    # 4. Safe de-hyphenation across linebreaks for lowercase prose words only
    # E.g. 'require-\nment' -> 'requirement', but DO NOT match 'Fe-500', 'M10-M100', 'IS-1786'
    normalized = re.sub(
        r"(?<![A-Z0-9])([a-z]{3,})-\n([a-z]{3,})(?![A-Z0-9])",
        r"\1\2",
        normalized,
    )

    # 5. Normalize line breaks and horizontal whitespace
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in normalized.splitlines()]

    # 6. Reconstruct text with single blank line between paragraphs (max 2 consecutive newlines)
    cleaned_lines: list[str] = []
    consecutive_empty = 0
    for line in lines:
        if not line:
            consecutive_empty += 1
            if consecutive_empty <= 1:
                cleaned_lines.append("")
        else:
            consecutive_empty = 0
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def detect_page_headings(page_text: str) -> list[str]:
    """
    Lightweight deterministic detection of recognized procurement sections on a page.
    Returns canonical section names if clearly matched, else empty list.
    """
    if not page_text:
        return []

    detected: list[str] = []
    seen: set[str] = set()

    for line in page_text.splitlines():
        trimmed = line.strip()
        if not trimmed or len(trimmed) > 100:
            continue

        for section_name, pattern in KNOWN_TENDER_SECTIONS:
            if section_name not in seen and pattern.search(trimmed):
                detected.append(section_name)
                seen.add(section_name)

    return detected


class PDFExtractor:
    """
    Extracts text and structural metadata from PDF documents page-by-page.
    """

    @staticmethod
    def extract_from_bytes(
        pdf_bytes: bytes,
        filename: str,
        document_id: str,
        content_type: str = "application/pdf",
    ) -> DocumentExtractionResponse:
        """
        Extracts document text page-by-page from raw PDF bytes.
        """
        file_size = len(pdf_bytes)
        warnings: list[str] = []
        pages: list[PageExtraction] = []
        all_detected_sections: list[str] = []
        seen_sections: set[str] = set()

        if file_size == 0:
            return DocumentExtractionResponse(
                document_id=document_id,
                filename=filename,
                content_type=content_type,
                file_size=0,
                page_count=0,
                status=ExtractionStatus.FAILED.value,
                extracted_text="",
                pages=[],
                warnings=["PDF file is empty (0 bytes)."],
                metadata=DocumentMetadata(),
            )

        # Attempt to open PDF via PyMuPDF
        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        except Exception as exc:
            logger.warning("Failed to open PDF %s: %s", filename, exc)
            return DocumentExtractionResponse(
                document_id=document_id,
                filename=filename,
                content_type=content_type,
                file_size=file_size,
                page_count=0,
                status=ExtractionStatus.FAILED.value,
                extracted_text="",
                pages=[],
                warnings=[f"Malformed or unreadable PDF document: {str(exc)}"],
                metadata=DocumentMetadata(),
            )

        try:
            # Check for encryption/password lock
            if doc.is_encrypted and not doc.is_extractable:
                return DocumentExtractionResponse(
                    document_id=document_id,
                    filename=filename,
                    content_type=content_type,
                    file_size=file_size,
                    page_count=len(doc),
                    status=ExtractionStatus.FAILED.value,
                    extracted_text="",
                    pages=[],
                    warnings=["PDF is password-protected or encrypted. Text extraction cannot proceed."],
                    metadata=DocumentMetadata(),
                )

            page_count = len(doc)
            if page_count == 0:
                return DocumentExtractionResponse(
                    document_id=document_id,
                    filename=filename,
                    content_type=content_type,
                    file_size=file_size,
                    page_count=0,
                    status=ExtractionStatus.FAILED.value,
                    extracted_text="",
                    pages=[],
                    warnings=["PDF contains zero pages."],
                    metadata=DocumentMetadata(),
                )

            empty_pages: list[int] = []
            total_chars = 0
            total_words = 0
            cleaned_texts: list[str] = []

            for page_idx in range(page_count):
                page_num = page_idx + 1
                page = doc[page_idx]

                # Extract text using block-aware reading order
                try:
                    blocks = page.get_text("blocks")
                    # blocks: (x0, y0, x1, y1, text, block_no, block_type)
                    # block_type == 0 indicates text
                    text_blocks = [b[4] for b in sorted(blocks, key=lambda b: (b[1], b[0])) if b[6] == 0]
                    raw_page_text = "\n\n".join(text_blocks) if text_blocks else page.get_text("text")
                except Exception as page_exc:
                    logger.warning("Error reading blocks from page %d: %s", page_num, page_exc)
                    raw_page_text = page.get_text("text")

                cleaned_page_text = normalize_pdf_text(raw_page_text)
                char_count = len(cleaned_page_text)
                has_text = char_count > 0
                word_count = len(cleaned_page_text.split()) if has_text else 0

                if not has_text:
                    empty_pages.append(page_num)
                else:
                    total_chars += char_count
                    total_words += word_count
                    cleaned_texts.append(cleaned_page_text)

                headings = detect_page_headings(cleaned_page_text)
                for h in headings:
                    if h not in seen_sections:
                        all_detected_sections.append(h)
                        seen_sections.add(h)

                pages.append(
                    PageExtraction(
                        page_number=page_num,
                        raw_text=raw_page_text,
                        cleaned_text=cleaned_page_text,
                        character_count=char_count,
                        word_count=word_count,
                        has_text=has_text,
                        detected_headings=headings,
                    )
                )

            # Combined document text (separated cleanly by page headers for inspectability)
            full_extracted_text = "\n\n".join(cleaned_texts)

            # Assess extraction quality and generate factual warnings
            pages_with_text = page_count - len(empty_pages)
            pages_without_text = len(empty_pages)

            status = ExtractionStatus.SUCCESS.value

            if pages_with_text == 0:
                status = ExtractionStatus.FAILED.value
                warnings.append(
                    "Text could not be reliably extracted from this PDF. OCR is not enabled in the current MVP."
                )
            elif pages_without_text > 0:
                status = ExtractionStatus.PARTIAL.value
                if len(empty_pages) == 1:
                    warnings.append(f"Page {empty_pages[0]} contains little or no extractable text.")
                elif len(empty_pages) <= 5:
                    warnings.append(f"Pages {', '.join(str(p) for p in empty_pages)} contain little or no extractable text.")
                else:
                    warnings.append(
                        f"{len(empty_pages)} of {page_count} pages contain little or no extractable text (possible scanned/image pages)."
                    )

            metadata = DocumentMetadata(
                total_characters=total_chars,
                total_words=total_words,
                pages_with_text=pages_with_text,
                pages_without_text=pages_without_text,
                detected_sections=all_detected_sections,
            )

            return DocumentExtractionResponse(
                document_id=document_id,
                filename=filename,
                content_type=content_type,
                file_size=file_size,
                page_count=page_count,
                status=status,
                extracted_text=full_extracted_text,
                pages=pages,
                warnings=warnings,
                metadata=metadata,
            )

        finally:
            doc.close()
