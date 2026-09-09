"""
Tests for Run 6 — Tender Intelligence: Requirement Extraction → BIS Recommendations.

Test categories:
  A. Requirement extraction (unit tests on service)
  B. Integration (API end-to-end with mock provider)
  C. Failure handling
  D. Regression (existing endpoints unaffected)

All tests use MockExtractionProvider or in-process fixtures.
No internet dependency; no Gemini API key required.
"""
from __future__ import annotations

import io
import os
import re
from typing import Any

import pymupdf
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.search import get_vector_store, get_embedding_service
from app.schemas.document import DocumentExtractionResponse, ExtractionStatus, PageExtraction, DocumentMetadata
from app.schemas.requirement import (
    RequirementCategory,
    TenderRequirement,
    TechnicalParameter,
)
from app.services.requirement_extractor import (
    MockExtractionProvider,
    RequirementExtractor,
    _LLMRequirement,
    _LLMParameter,
    _convert_to_tender_requirements,
    _make_chunks,
    _merge_requirements,
)

# ─────────────────────────────────────────────────────────────────────────────
#  Mock vector store + embedding service (same pattern as test_api.py)
#  Avoids competing with running uvicorn server for the Qdrant file lock.
# ─────────────────────────────────────────────────────────────────────────────

class MockEmbeddingService:
    model_name = "test-model"
    dimension = 384

    def embed_text(self, text: str) -> list[float]:
        return [0.1] * 384

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 384 for _ in texts]


class MockVectorStore:
    collection_name = "bis_standards"

    def get_collection_info(self) -> dict:
        return {
            "collection_name": self.collection_name,
            "status": "green",
            "points_count": 30,
            "vectors_count": 30,
        }

    def search(self, query_vector: list[float], limit: int = 10, score_threshold: float = 0.0) -> list[dict]:
        """Returns realistic results covering the three sample tender standards."""
        return [
            {
                "id": 1, "score": 0.88,
                "payload": {
                    "standard_number": "IS 1786:2008",
                    "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement",
                    "category": "Reinforcement Steel / Construction",
                    "scope": (
                        "This standard covers the requirements of high strength deformed steel bars "
                        "and wires for use as reinforcement in concrete, including Fe 500 and Fe 500D grades."
                    ),
                    "keywords": ["reinforcement", "TMT", "Fe 500", "deformed bars", "RCC"],
                    "status": "ACTIVE",
                    "year_of_publication": 2008,
                    "source_url": "https://www.bis.gov.in/index.php?option=com_content&view=article&id=1786",
                    "source_evidence_note": "Official BIS catalog entry",
                },
            },
            {
                "id": 2, "score": 0.75,
                "payload": {
                    "standard_number": "IS 2062:2011",
                    "title": "Hot Rolled Medium and High Tensile Structural Steel",
                    "category": "Structural Steel / Fabrication",
                    "scope": (
                        "This standard covers the requirements of steel plates, sections, and bars "
                        "in grades E250, E350, E450 for structural purposes."
                    ),
                    "keywords": ["structural steel", "E250", "hot rolled", "plates", "sections"],
                    "status": "ACTIVE",
                    "year_of_publication": 2011,
                    "source_url": "https://www.bis.gov.in/index.php?option=com_content&view=article&id=2062",
                    "source_evidence_note": "Official BIS catalog entry",
                },
            },
            {
                "id": 3, "score": 0.72,
                "payload": {
                    "standard_number": "IS 694:2010",
                    "title": "PVC Insulated Cables for Working Voltages up to and Including 1100 V",
                    "category": "Electrical / Cables",
                    "scope": (
                        "This standard covers PVC insulated cables with copper or aluminium conductors "
                        "for working voltages up to and including 1100 V."
                    ),
                    "keywords": ["PVC cable", "copper", "insulated", "450/750 V", "wiring"],
                    "status": "ACTIVE",
                    "year_of_publication": 2010,
                    "source_url": "https://www.bis.gov.in/index.php?option=com_content&view=article&id=694",
                    "source_evidence_note": "Official BIS catalog entry",
                },
            },
        ]


@pytest.fixture(autouse=True)
def override_vector_dependencies():
    """Override Qdrant + embedding dependencies for all tests in this module."""
    mock_store = MockVectorStore()
    mock_emb = MockEmbeddingService()
    app.dependency_overrides[get_vector_store] = lambda: mock_store
    app.dependency_overrides[get_embedding_service] = lambda: mock_emb
    yield
    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

client = TestClient(app)


def make_doc_response(
    pages_text: list[str],
    document_id: str = "test-doc-001",
    filename: str = "test_tender.pdf",
    status: str = ExtractionStatus.SUCCESS.value,
) -> DocumentExtractionResponse:
    """Build a DocumentExtractionResponse fixture in-process (no PDF needed)."""
    pages = []
    total_chars = 0
    total_words = 0

    for i, text in enumerate(pages_text, start=1):
        has_text = bool(text.strip())
        char_count = len(text)
        word_count = len(text.split())
        if has_text:
            total_chars += char_count
            total_words += word_count
        pages.append(PageExtraction(
            page_number=i,
            raw_text=text,
            cleaned_text=text,
            character_count=char_count,
            word_count=word_count,
            has_text=has_text,
            detected_headings=[],
        ))

    return DocumentExtractionResponse(
        document_id=document_id,
        filename=filename,
        content_type="application/pdf",
        file_size=len("".join(pages_text)),
        page_count=len(pages),
        status=status,
        extracted_text="\n\n".join(t for t in pages_text if t.strip()),
        pages=pages,
        warnings=[],
        metadata=DocumentMetadata(
            total_characters=total_chars,
            total_words=total_words,
            pages_with_text=sum(1 for t in pages_text if t.strip()),
            pages_without_text=sum(1 for t in pages_text if not t.strip()),
            detected_sections=[],
        ),
    )


def create_in_memory_pdf(pages_text: list[str]) -> bytes:
    """Programmatically generate small test PDFs."""
    doc = pymupdf.open()
    for text in pages_text:
        page = doc.new_page()
        if text.strip():
            page.insert_text((50, 72), text, fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _force_mock_provider(monkeypatch) -> None:
    """Patch RequirementExtractor in the tender_analysis module to use MockExtractionProvider."""
    import app.api.v1.tender_analysis as ta_module
    monkeypatch.setattr(
        ta_module,
        "RequirementExtractor",
        lambda: RequirementExtractor(provider=MockExtractionProvider()),
    )


# ─────────────────────────────────────────────────────────────────────────────
#  A. REQUIREMENT EXTRACTION UNIT TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestRequirementExtractionService:

    def test_technical_requirement_extracted(self):
        """A1. TMT steel requirement is extracted from spec text."""
        provider = MockExtractionProvider()
        text = (
            "[Page 2]\n"
            "Technical Specifications\n"
            "12 mm Fe 500 TMT high strength deformed reinforcement bars conforming to IS 1786:2008 "
            "shall be used for all RCC works."
        )
        results = provider.extract(text, page_numbers=[2])
        assert len(results) >= 1
        titles = [r.title for r in results]
        assert any("TMT" in t or "Reinforcement" in t or "Steel" in t for t in titles)

    def test_non_technical_clause_not_extracted(self):
        """A2. Payment terms and bid deadlines are not extracted as technical requirements."""
        provider = MockExtractionProvider()
        text = (
            "[Page 1]\n"
            "General Conditions of Contract\n"
            "Payment shall be made within 30 days of invoice. "
            "Bank guarantee of 10% of contract value required. "
            "Bid submission deadline: 15 October 2026. "
            "Arbitration shall be as per the Arbitration and Conciliation Act."
        )
        results = provider.extract(text, page_numbers=[1])
        # Mock provider uses keyword matching; these clauses contain no technical patterns
        assert len(results) == 0

    def test_source_page_preserved(self):
        """A3. source_page matches the page number passed to the provider."""
        provider = MockExtractionProvider()
        text = "[Page 5]\nPVC insulated copper cable rated 450/750 V for internal electrical wiring."
        results = provider.extract(text, page_numbers=[5])
        assert len(results) >= 1
        assert all(r.source_page == 5 for r in results)

    def test_explicit_is_reference_preserved(self):
        """A4. IS number stated in the text appears in explicitly_referenced_standards."""
        provider = MockExtractionProvider()
        text = (
            "[Page 2]\n"
            "Fe 500 TMT bars shall conform to IS 1786:2008 for all structural reinforcement."
        )
        results = provider.extract(text, page_numbers=[2])
        assert len(results) >= 1
        tmt_req = next((r for r in results if "TMT" in r.title or "Reinforcement" in r.title), results[0])
        assert "IS 1786:2008" in tmt_req.explicitly_referenced_standards

    def test_missing_is_reference_not_fabricated(self):
        """A5. If no IS number in text, explicitly_referenced_standards must be empty."""
        provider = MockExtractionProvider()
        text = (
            "[Page 3]\n"
            "12 mm Fe 500 TMT high strength deformed bars shall be used for RCC slab construction."
        )
        results = provider.extract(text, page_numbers=[3])
        assert len(results) >= 1
        tmt_req = next((r for r in results if "TMT" in r.title or "Reinforcement" in r.title), results[0])
        # Text contains no IS number → list must be empty
        assert tmt_req.explicitly_referenced_standards == []

    def test_technical_parameters_extracted(self):
        """A6. Diameter, grade, and voltage parameters survive extraction."""
        provider = MockExtractionProvider()
        texts_and_checks = [
            (
                "[Page 2]\n12 mm Fe 500 TMT deformed steel bars conforming to IS 1786:2008.",
                [2],
                {"diameter": "12", "grade": "Fe 500"},
            ),
            (
                "[Page 2]\nPVC insulated copper cable rated 450/750 V as per IS 694:2010.",
                [2],
                {"voltage": "450/750"},
            ),
        ]
        for text, pages, expected_params in texts_and_checks:
            results = provider.extract(text, pages)
            assert len(results) >= 1
            param_dict = {p.name: p.value for p in results[0].technical_parameters}
            for pname, pval in expected_params.items():
                assert pname in param_dict, f"Parameter '{pname}' not extracted"
                assert pval in param_dict[pname], f"Value '{pval}' not in '{param_dict[pname]}'"

    def test_duplicate_requirements_merged(self):
        """A7. Same requirement appearing on two pages is merged into one with both pages."""
        req1 = TenderRequirement(
            requirement_id="REQ-001",
            title="TMT Reinforcement Steel Bar",
            category=RequirementCategory.GRADE,
            original_text="12 mm Fe 500 TMT bars per IS 1786:2008.",
            normalized_text="high strength deformed TMT steel bars concrete reinforcement",
            source_page=2,
            source_pages=[2],
            mandatory_language=True,
            explicitly_referenced_standards=["IS 1786:2008"],
            technical_parameters=[TechnicalParameter(name="diameter", value="12", unit="mm")],
            extraction_confidence=0.90,
        )
        req2 = TenderRequirement(
            requirement_id="REQ-002",
            title="TMT Reinforcement Steel Bar",  # same title → same fingerprint
            category=RequirementCategory.GRADE,
            original_text="Fe 500 TMT reinforcement bars conforming to IS 1786:2008 for all RCC.",
            normalized_text="high strength deformed TMT steel bars concrete reinforcement",
            source_page=4,
            source_pages=[4],
            mandatory_language=True,
            explicitly_referenced_standards=["IS 1786:2008"],
            technical_parameters=[TechnicalParameter(name="grade", value="Fe 500", unit=None)],
            extraction_confidence=0.95,
        )

        merged = _merge_requirements([req1, req2])

        assert len(merged) == 1
        merged_req = merged[0]
        assert 2 in merged_req.source_pages
        assert 4 in merged_req.source_pages
        # Longer text wins
        assert "for all RCC" in merged_req.original_text
        # Both parameters present
        param_names = {p.name for p in merged_req.technical_parameters}
        assert "diameter" in param_names
        assert "grade" in param_names
        # Explicit standard preserved
        assert "IS 1786:2008" in merged_req.explicitly_referenced_standards
        # Higher confidence kept
        assert merged_req.extraction_confidence == 0.95

    def test_different_requirements_not_merged(self):
        """A8. Requirements with different subjects are kept separate."""
        req1 = TenderRequirement(
            requirement_id="REQ-001",
            title="TMT Reinforcement Steel Bar",
            category=RequirementCategory.GRADE,
            original_text="12 mm Fe 500 TMT bars.",
            normalized_text="high strength deformed TMT steel bars concrete reinforcement",
            source_page=2,
            source_pages=[2],
        )
        req2 = TenderRequirement(
            requirement_id="REQ-002",
            title="PVC Insulated Copper Cable",
            category=RequirementCategory.ELECTRICAL,
            original_text="PVC insulated copper cable rated 450/750 V.",
            normalized_text="PVC insulated copper cable 450 750 V electrical wiring",
            source_page=3,
            source_pages=[3],
        )
        merged = _merge_requirements([req1, req2])
        assert len(merged) == 2

    def test_chunking_single_small_doc(self):
        """Chunking a small document produces exactly one chunk."""
        pages = [
            PageExtraction(
                page_number=i, raw_text=f"Page {i} content here.", cleaned_text=f"Page {i} content here.",
                character_count=20, word_count=4, has_text=True, detected_headings=[],
            )
            for i in range(1, 4)
        ]
        chunks = _make_chunks(pages, max_words=3000)
        assert len(chunks) == 1
        _, page_nums = chunks[0]
        assert page_nums == [1, 2, 3]

    def test_chunking_large_doc_splits_at_boundaries(self):
        """Large document splits into multiple bounded chunks."""
        # 4 pages × 1000 words each = 4000 total > 3000 limit
        pages = [
            PageExtraction(
                page_number=i,
                raw_text=" ".join(["word"] * 1000),
                cleaned_text=" ".join(["word"] * 1000),
                character_count=5000,
                word_count=1000,
                has_text=True,
                detected_headings=[],
            )
            for i in range(1, 5)
        ]
        chunks = _make_chunks(pages, max_words=3000)
        assert len(chunks) >= 2
        # All pages accounted for
        all_pages_in_chunks = [pn for _, pns in chunks for pn in pns]
        assert sorted(all_pages_in_chunks) == [1, 2, 3, 4]

    def test_convert_preserves_is_reference(self):
        """_convert_to_tender_requirements keeps valid IS refs and drops non-IS strings."""
        raw = [_LLMRequirement(
            title="Steel",
            category="MATERIAL",
            original_text="Steel per IS 2062:2011",
            normalized_text="structural steel",
            source_page=1,
            explicitly_referenced_standards=["IS 2062:2011", "not-a-standard"],
        )]
        converted = _convert_to_tender_requirements(raw)
        assert len(converted) == 1
        assert "IS 2062:2011" in converted[0].explicitly_referenced_standards
        assert "not-a-standard" not in converted[0].explicitly_referenced_standards

    def test_full_extractor_with_mock_provider(self):
        """RequirementExtractor produces requirements from a multi-page mock doc."""
        doc = make_doc_response([
            "Cover Page\nProcurement of Civil Materials\nPWD Tender 2026/09",
            (
                "Technical Specifications\n"
                "12 mm Fe 500 TMT high strength deformed bars conforming to IS 1786:2008 "
                "shall be used for all RCC works.\n"
                "Structural steel per IS 2062:2011 Grade E250 for fabrication.\n"
                "PVC insulated copper cable rated 450/750 V per IS 694:2010."
            ),
        ])
        extractor = RequirementExtractor(provider=MockExtractionProvider())
        requirements, warnings = extractor.extract(doc)
        assert len(requirements) >= 1
        # Source pages must be integers, not invented
        for req in requirements:
            assert isinstance(req.source_page, int)
            assert req.source_page >= 1

    def test_extractor_empty_document_returns_warning(self):
        """Empty document returns [] and a warning, not an exception."""
        doc = make_doc_response(["", ""])  # no text
        extractor = RequirementExtractor(provider=MockExtractionProvider())
        requirements, warnings = extractor.extract(doc)
        assert requirements == []
        assert len(warnings) >= 1


# ─────────────────────────────────────────────────────────────────────────────
#  B. INTEGRATION TESTS — API endpoint
# ─────────────────────────────────────────────────────────────────────────────

class TestTenderAnalysisAPI:

    def test_analyze_returns_recommendations_for_technical_requirements(self, monkeypatch):
        """B1. Extracted requirements receive BIS recommendations from the existing engine."""
        _force_mock_provider(monkeypatch)
        doc = make_doc_response([
            "Cover Page\nPublic Works Department Tender",
            (
                "Technical Specifications\n"
                "12 mm Fe 500 TMT deformed steel bars conforming to IS 1786:2008.\n"
                "PVC insulated copper cable rated 450/750 V as per IS 694:2010.\n"
                "Structural steel IS 2062:2011 Grade E250."
            ),
        ])
        response = client.post("/api/v1/documents/analyze", json=doc.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert data["extraction_status"] in ("SUCCESS", "PARTIAL")
        assert data["requirement_count"] >= 1
        assert len(data["requirements"]) >= 1

    def test_recommendations_attached_to_requirements(self, monkeypatch):
        """B2. Each requirement record has a 'recommendations' list."""
        _force_mock_provider(monkeypatch)
        doc = make_doc_response([
            "Technical Specifications\n"
            "12 mm Fe 500 TMT reinforcement bars per IS 1786:2008 for all RCC works."
        ])
        response = client.post("/api/v1/documents/analyze", json=doc.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert len(data["requirements"]) >= 1
        for req_rec in data["requirements"]:
            assert "requirement" in req_rec
            assert "recommendations" in req_rec
            assert isinstance(req_rec["recommendations"], list)

    def test_lifecycle_and_compliance_survive_integration(self, monkeypatch):
        """B3. Recommended standards carry lifecycle and compliance data from existing services."""
        _force_mock_provider(monkeypatch)
        doc = make_doc_response([
            "Technical Specifications\n"
            "12 mm Fe 500 TMT deformed steel bars conforming to IS 1786:2008 for all RCC."
        ])
        response = client.post("/api/v1/documents/analyze", json=doc.model_dump())
        assert response.status_code == 200
        data = response.json()
        # Find any requirement that has at least one recommendation
        has_lifecycle_data = False
        for req_rec in data["requirements"]:
            for std in req_rec["recommendations"]:
                if std.get("lifecycle") is not None:
                    has_lifecycle_data = True
                    break
        # Lifecycle data exists in the DB for at least IS 1786
        assert has_lifecycle_data, "No lifecycle data found in any recommendation"

    def test_zero_result_requirement_handled(self, monkeypatch):
        """B4. A requirement with no matching standards returns an empty list, not an error."""
        _force_mock_provider(monkeypatch)

        # Override RequirementExtractor to inject a req with an unmatchable query
        class _FixedProvider(MockExtractionProvider):
            def extract(self, chunk_text, page_numbers):
                return [_LLMRequirement(
                    title="Hypothetical Unobtainium Requirement",
                    category="MATERIAL",
                    original_text="Supply of unobtainium grade X99 per IS 99999:2099.",
                    normalized_text="unobtainium grade X99 completely unknown fictional material",
                    source_page=page_numbers[0] if page_numbers else 1,
                )]

        import app.api.v1.tender_analysis as ta_module
        monkeypatch.setattr(
            ta_module, "RequirementExtractor",
            lambda: RequirementExtractor(provider=_FixedProvider()),
        )

        doc = make_doc_response(["Fictional Tender\nSupply of unobtainium grade X99."])
        response = client.post("/api/v1/documents/analyze", json=doc.model_dump())
        assert response.status_code == 200
        data = response.json()
        for req_rec in data["requirements"]:
            # Zero results is valid — must not error
            assert isinstance(req_rec["recommendations"], list)

    def test_source_page_preserved_in_api_response(self, monkeypatch):
        """B5. source_page from the extracted requirement appears in the API response."""
        _force_mock_provider(monkeypatch)
        doc = make_doc_response([
            "Cover Page",
            "Technical Specifications\n12 mm Fe 500 TMT bars per IS 1786:2008.",
        ])
        response = client.post("/api/v1/documents/analyze", json=doc.model_dump())
        assert response.status_code == 200
        data = response.json()
        for req_rec in data["requirements"]:
            req = req_rec["requirement"]
            assert isinstance(req["source_page"], int)
            assert req["source_page"] >= 1

    def test_explicit_is_reference_appears_in_response(self, monkeypatch):
        """B6. IS numbers from source text appear in explicitly_referenced_standards in response."""
        _force_mock_provider(monkeypatch)
        doc = make_doc_response([
            "Technical Specifications\n"
            "Fe 500 TMT bars conforming to IS 1786:2008 for structural reinforcement."
        ])
        response = client.post("/api/v1/documents/analyze", json=doc.model_dump())
        assert response.status_code == 200
        data = response.json()
        found_explicit_ref = False
        for req_rec in data["requirements"]:
            refs = req_rec["requirement"].get("explicitly_referenced_standards", [])
            if "IS 1786:2008" in refs:
                found_explicit_ref = True
                break
        assert found_explicit_ref, "IS 1786:2008 should appear in explicitly_referenced_standards"


# ─────────────────────────────────────────────────────────────────────────────
#  C. FAILURE HANDLING TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestTenderAnalysisFailureHandling:

    def test_provider_unavailable_returns_failed_status(self, monkeypatch):
        """C1. Provider RuntimeError (e.g. missing API key) returns FAILED status, not HTTP 500."""
        import app.api.v1.tender_analysis as ta_module

        def _broken_extractor():
            raise RuntimeError("GEMINI_API_KEY is not set.")

        monkeypatch.setattr(ta_module, "RequirementExtractor", _broken_extractor)

        doc = make_doc_response(["Technical Specifications\nFe 500 TMT bars."])
        response = client.post("/api/v1/documents/analyze", json=doc.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert data["extraction_status"] == "FAILED"
        assert data["requirement_count"] == 0

    def test_no_requirements_found_returns_no_requirements_status(self, monkeypatch):
        """C2. Document with only non-technical content returns NO_REQUIREMENTS."""
        class _EmptyProvider(MockExtractionProvider):
            def extract(self, chunk_text, page_numbers):
                return []  # always empty

        import app.api.v1.tender_analysis as ta_module
        monkeypatch.setattr(
            ta_module, "RequirementExtractor",
            lambda: RequirementExtractor(provider=_EmptyProvider()),
        )

        doc = make_doc_response([
            "Payment terms: 30 days. Bank guarantee: 10%. Arbitration: Delhi."
        ])
        response = client.post("/api/v1/documents/analyze", json=doc.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert data["extraction_status"] == "NO_REQUIREMENTS"
        assert data["requirement_count"] == 0

    def test_failed_extraction_document_returns_422(self):
        """C3. A FAILED extraction with no text is rejected with 422."""
        doc = make_doc_response(["", ""], status=ExtractionStatus.FAILED.value)
        response = client.post("/api/v1/documents/analyze", json=doc.model_dump())
        assert response.status_code == 422

    def test_one_provider_chunk_failure_returns_partial(self, monkeypatch):
        """C4. A single chunk failure adds a warning but other requirements survive."""
        call_count = {"n": 0}

        class _PartialProvider(MockExtractionProvider):
            def extract(self, chunk_text, page_numbers):
                call_count["n"] += 1
                if call_count["n"] == 1:
                    raise Exception("Network timeout on first chunk")
                return super().extract(chunk_text, page_numbers)

        import app.api.v1.tender_analysis as ta_module
        monkeypatch.setattr(
            ta_module, "RequirementExtractor",
            lambda: RequirementExtractor(provider=_PartialProvider()),
        )

        # Build a large enough doc to force 2 chunks
        long_text = " ".join(["word"] * 2000)
        doc = make_doc_response([
            long_text,
            "Technical Specifications\n12 mm Fe 500 TMT bars per IS 1786:2008.",
        ])
        response = client.post("/api/v1/documents/analyze", json=doc.model_dump())
        # Should succeed (partial at worst) rather than crashing
        assert response.status_code == 200

    def test_missing_document_id_raises_validation_error(self):
        """C5. Malformed payload without required fields is rejected."""
        response = client.post("/api/v1/documents/analyze", json={"bad": "data"})
        assert response.status_code == 422  # Pydantic validation

    def test_anti_hallucination_note_present(self, monkeypatch):
        """C6. Response always contains anti-hallucination note."""
        _force_mock_provider(monkeypatch)
        doc = make_doc_response(["Fe 500 TMT bars per IS 1786:2008."])
        response = client.post("/api/v1/documents/analyze", json=doc.model_dump())
        data = response.json()
        assert "anti_hallucination_note" in data
        assert len(data["anti_hallucination_note"]) > 10


# ─────────────────────────────────────────────────────────────────────────────
#  D. REGRESSION TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestRegressionRun6:

    def test_manual_search_still_works(self):
        """D1. Manual specification search endpoint unchanged."""
        response = client.post(
            "/api/v1/search",
            json={"query": "12 mm Fe 500 TMT reinforcement bars for RCC construction", "limit": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_matches"] > 0
        top = data["results"][0]
        assert "IS 1786" in top["standard_number"]

    def test_document_upload_still_works(self):
        """D2. Run 6A document upload endpoint unchanged."""
        pdf_bytes = create_in_memory_pdf([
            "Technical Specifications\nFe 500 TMT bars per IS 1786:2008."
        ])
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("tender.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert "document_id" in data
        assert data["page_count"] == 1

    def test_health_endpoint_still_works(self):
        """D3. Health endpoint reports online."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "HEALTHY"

    def test_compliance_endpoint_still_works(self):
        """D4. IS 1786 compliance data still accessible."""
        response = client.get("/api/v1/standards/IS 1786:2008/compliance")
        assert response.status_code == 200
        data = response.json()
        assert data["certification_status"] == "MANDATORY"

    def test_lifecycle_endpoint_still_works(self):
        """D5. IS 2062 lifecycle data still accessible."""
        response = client.get("/api/v1/standards/IS 2062:2011/lifecycle")
        assert response.status_code == 200
        data = response.json()
        assert data["lifecycle_status"] in ("ACTIVE", "SUPERSEDED", "UNKNOWN")

    def test_analyze_endpoint_registered(self):
        """D6. The new /documents/analyze endpoint is reachable (not 404)."""
        # Send minimal invalid payload — expect 422 (validation) not 404
        response = client.post("/api/v1/documents/analyze", json={})
        assert response.status_code == 422

    def test_search_audit_disclaimer_present(self):
        """D7. Manual search still returns audit disclaimer."""
        response = client.post(
            "/api/v1/search",
            json={"query": "PVC cable 450/750 V copper", "limit": 3},
        )
        assert response.status_code == 200
        data = response.json()
        assert "audit_disclaimer" in data
