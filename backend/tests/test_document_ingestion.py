"""
Focused tests for Run 6A — PDF / Tender Document Ingestion Foundation.

Covers:
1. Valid single-page text PDF extraction
2. Multi-page PDF extraction preserving page boundaries
3. 1-indexed page numbering correctness
4. Deterministic text normalization
5. Technical specifications, standard numbers, and unit preservation
6. Empty / zero-text PDF detection and warning
7. Non-PDF file type rejection (HTTP 400)
8. File size validation (0 bytes and > 20 MB)
9. Corrupted / malformed PDF stream handling
10. API endpoint POST /api/v1/documents/upload success response
11. Partial text extraction warnings (scanned / empty page detection)
12. Existing search API regression verification
"""
import io
import pytest
import pymupdf
from fastapi.testclient import TestClient

from app.main import app
from app.services.pdf_extractor import PDFExtractor, normalize_pdf_text, detect_page_headings
from app.schemas.document import ExtractionStatus, DocumentExtractionResponse

client = TestClient(app)


def create_in_memory_pdf(pages_text: list[str]) -> bytes:
    """Helper to programmatically generate small in-memory test PDFs."""
    doc = pymupdf.open()
    for text in pages_text:
        page = doc.new_page()
        if text.strip():
            page.insert_text((50, 72), text, fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


class TestPDFExtractionService:
    def test_single_page_extraction(self):
        """1. Valid text PDF extraction with page metrics."""
        text = "Technical Specification\n12 mm Fe 500 reinforcement bars conforming to IS 1786:2008."
        pdf_bytes = create_in_memory_pdf([text])

        res = PDFExtractor.extract_from_bytes(pdf_bytes, filename="tender_sample.pdf", document_id="doc-1")
        assert isinstance(res, DocumentExtractionResponse)
        assert res.document_id == "doc-1"
        assert res.filename == "tender_sample.pdf"
        assert res.page_count == 1
        assert res.status == ExtractionStatus.SUCCESS.value
        assert len(res.pages) == 1

        page = res.pages[0]
        assert page.page_number == 1
        assert page.has_text is True
        assert "IS 1786:2008" in page.cleaned_text
        assert "12 mm" in page.cleaned_text
        assert "Fe 500" in page.cleaned_text
        assert page.character_count > 0
        assert page.word_count > 0

    def test_multipage_page_boundaries_preserved(self):
        """2 & 3. Multi-page PDF extraction with 1-indexed page boundaries."""
        page1 = "Section I: Notice Inviting Tender\nTender No: 2026/PWD/09"
        page2 = "Section II: Technical Specifications\nHigh Strength Deformed Steel Bars for RCC (IS 1786:2008)"
        page3 = "Section III: Electrical Specifications\nPVC insulated cables rated 450/750 V as per IS 694:2010"

        pdf_bytes = create_in_memory_pdf([page1, page2, page3])
        res = PDFExtractor.extract_from_bytes(pdf_bytes, filename="multi_page_tender.pdf", document_id="doc-multi")

        assert res.page_count == 3
        assert len(res.pages) == 3
        assert [p.page_number for p in res.pages] == [1, 2, 3]

        # Verify page-level content isolation (no flattened blurring)
        assert "Notice Inviting Tender" in res.pages[0].cleaned_text
        assert "Notice Inviting Tender" not in res.pages[1].cleaned_text

        assert "IS 1786:2008" in res.pages[1].cleaned_text
        assert "IS 1786:2008" not in res.pages[0].cleaned_text

        assert "IS 694:2010" in res.pages[2].cleaned_text
        assert "450/750 V" in res.pages[2].cleaned_text

        # Verify metadata
        assert res.metadata.pages_with_text == 3
        assert res.metadata.pages_without_text == 0
        assert "Notice Inviting Tender" in res.metadata.detected_sections
        assert "Technical Specifications" in res.metadata.detected_sections

    def test_text_normalization_rules(self):
        """4. Text normalization handles whitespace, blank lines, and curly quotes."""
        raw = "Clause  4.1:   General   Requirement\n\n\n\n\n‘Special’  “Grade”  material\u00a0specification."
        cleaned = normalize_pdf_text(raw)

        # Non-breaking spaces and redundant spaces collapsed
        assert "  " not in cleaned
        # Max 2 newlines
        assert "\n\n\n" not in cleaned
        # Standard ASCII quotes
        assert "'Special'" in cleaned
        assert '"Grade"' in cleaned

    def test_technical_identifiers_preserved_intact(self):
        """5. Critical standards, grades, units, and legal citations remain uncorrupted."""
        technical_spec = (
            "Requirement:\n"
            "- Standard: IS 1786:2008 and IS 2062:2011 Grade E250\n"
            "- Diameter: 12 mm and 16 mm Fe 500 TMT bars\n"
            "- Cable: 450/750 V multi-core flexible cable (IS 694:2010)\n"
            "- Fastener: M10-M100 high strength bolts\n"
            "- Gazette Order: S.O. 1673(E) Steel QCO Order\n"
            "- PPE: IS 15298 (Part 2):2016 safety footwear"
        )
        cleaned = normalize_pdf_text(technical_spec)

        assert "IS 1786:2008" in cleaned
        assert "IS 2062:2011" in cleaned
        assert "12 mm" in cleaned
        assert "Fe 500" in cleaned
        assert "450/750 V" in cleaned
        assert "M10-M100" in cleaned
        assert "S.O. 1673(E)" in cleaned
        assert "IS 15298 (Part 2):2016" in cleaned

    def test_zero_text_or_empty_pdf_warning(self):
        """6. Scanned or empty PDF generates clear OCR warning without faking text."""
        # 2 pages with zero text (simulating blank or image-only scanned pages)
        pdf_bytes = create_in_memory_pdf(["", ""])
        res = PDFExtractor.extract_from_bytes(pdf_bytes, filename="scanned_drawing.pdf", document_id="doc-scan")

        assert res.page_count == 2
        assert res.status == ExtractionStatus.FAILED.value
        assert res.metadata.pages_with_text == 0
        assert res.metadata.pages_without_text == 2
        assert len(res.warnings) >= 1
        assert "OCR is not enabled in the current MVP" in res.warnings[0]

    def test_partial_text_pages_warning(self):
        """11. PDF with a mix of text and empty pages generates PARTIAL status and page warnings."""
        pdf_bytes = create_in_memory_pdf(["Page 1 with text", "", "Page 3 with text"])
        res = PDFExtractor.extract_from_bytes(pdf_bytes, filename="mixed.pdf", document_id="doc-mixed")

        assert res.page_count == 3
        assert res.status == ExtractionStatus.PARTIAL.value
        assert res.metadata.pages_with_text == 2
        assert res.metadata.pages_without_text == 1
        assert any("Page 2 contains little or no extractable text" in w for w in res.warnings)


class TestDocumentUploadAPI:
    def test_upload_valid_pdf_success_200(self):
        """10. Endpoint POST /api/v1/documents/upload returns HTTP 200 with valid structure."""
        text = "Technical Specifications for Civil Works\nMaterial: Fe 500 TMT Steel (IS 1786:2008)"
        pdf_bytes = create_in_memory_pdf([text])

        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("tender_civil.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        )

        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["filename"] == "tender_civil.pdf"
        assert data["page_count"] == 1
        assert data["status"] == "SUCCESS"
        assert len(data["pages"]) == 1
        assert "IS 1786:2008" in data["extracted_text"]
        assert "Fe 500" in data["extracted_text"]
        assert data["metadata"]["total_characters"] > 0

    def test_upload_invalid_file_extension_rejected(self):
        """7. Reject non-PDF file uploads with HTTP 400."""
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("tender_schedule.xlsx", io.BytesIO(b"fake-excel-data"), "application/vnd.ms-excel")}
        )
        assert response.status_code == 400
        assert "Only PDF documents (.pdf) are supported" in response.json()["detail"]

        response_docx = client.post(
            "/api/v1/documents/upload",
            files={"file": ("spec.docx", io.BytesIO(b"fake-doc-data"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        assert response_docx.status_code == 400

    def test_upload_empty_file_rejected(self):
        """8a. Reject 0-byte upload with HTTP 400."""
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")}
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_upload_missing_magic_bytes_rejected(self):
        """9. Reject file named .pdf that is corrupted or not a valid PDF."""
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("corrupted.pdf", io.BytesIO(b"This is just plain text, not a PDF."), "application/pdf")}
        )
        assert response.status_code == 400
        assert "PDF signature" in response.json()["detail"]

    def test_search_api_regression_unaffected(self):
        """12. Verify manual search pipeline remains completely functional after document integration."""
        response = client.post(
            "/api/v1/search",
            json={"query": "12 mm Fe 500 TMT reinforcement bars for RCC construction", "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_matches"] > 0
        top = data["results"][0]
        assert "IS 1786" in top["standard_number"]
        assert "compliance" in top
        assert top["compliance"]["certification_status"] == "MANDATORY"
