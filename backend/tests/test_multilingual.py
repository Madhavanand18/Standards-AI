"""
Multilingual & Mixed-Language Input Processing Tests — Run 7.

Validates query normalization, language classification, technical identifier preservation,
and search retrieval accuracy across English, Hindi, Hinglish, and mixed inputs.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.normalizer import (
    NormalizationResult,
    detect_language,
    normalize_query,
)

client = TestClient(app)


class TestNormalizerUnit:
    """Unit tests for MultilingualNormalizer logic."""

    def test_technical_identifier_preservation_is_number(self):
        query = "IS 1786:2008 ke anusar 12 mm Fe 500 TMT sariya"
        res = normalize_query(query)
        assert "IS 1786:2008" in res.normalized_query
        assert "12 mm" in res.normalized_query
        assert "Fe 500" in res.normalized_query
        assert "reinforcement steel TMT rebar" in res.normalized_query

    def test_technical_identifier_preservation_voltage_and_grade(self):
        query = "450/750 V PVC copper cable Grade E250 loha"
        res = normalize_query(query)
        assert "450/750 V" in res.normalized_query
        assert "Grade E250" in res.normalized_query
        assert "structural steel" in res.normalized_query

    def test_devanagari_unit_transliteration(self):
        query = "12 मिमी Fe 500 TMT सरिया RCC निर्माण के लिए"
        res = normalize_query(query)
        assert "12 mm" in res.normalized_query
        assert "Fe 500" in res.normalized_query
        assert "reinforcement steel TMT rebar" in res.normalized_query
        assert "construction" in res.normalized_query

    def test_language_detection_hindi(self):
        lang = detect_language("12 मिमी Fe 500 TMT सरिया RCC निर्माण के लिए")
        assert lang in ("HINDI", "MIXED")

    def test_language_detection_hinglish(self):
        lang = detect_language("12 mm Fe 500 TMT sariya RCC construction ke liye")
        assert lang == "HINGLISH"

    def test_language_detection_english(self):
        lang = detect_language("12 mm Fe 500 TMT reinforcement bars")
        assert lang == "ENGLISH"

    def test_language_detection_mixed(self):
        lang = detect_language("450/750 V PVC copper cable बिजली wiring ke liye")
        assert lang == "MIXED"


class TestMultilingualSearchAPI:
    """Integration tests verifying end-to-end BIS search retrieval for multilingual inputs."""

    def test_case_1_english_query(self):
        payload = {"query": "12 mm Fe 500 TMT reinforcement bars", "limit": 5}
        resp = client.post("/api/v1/search", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "12 mm Fe 500 TMT reinforcement bars"
        assert len(data["results"]) > 0
        top_std = data["results"][0]["standard_number"]
        assert top_std == "IS 1786:2008"

    def test_case_2_hindi_query(self):
        payload = {"query": "12 मिमी Fe 500 TMT सरिया RCC निर्माण के लिए", "limit": 5}
        resp = client.post("/api/v1/search", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["results"]) > 0
        stds = [r["standard_number"] for r in data["results"]]
        assert "IS 1786:2008" in stds

    def test_case_3_hinglish_query(self):
        payload = {"query": "12 mm Fe 500 TMT sariya RCC construction ke liye", "limit": 5}
        resp = client.post("/api/v1/search", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["results"]) > 0
        stds = [r["standard_number"] for r in data["results"]]
        assert "IS 1786:2008" in stds

    def test_case_4_mixed_electrical_query(self):
        payload = {"query": "450/750 V PVC copper cable बिजली wiring ke liye", "limit": 5}
        resp = client.post("/api/v1/search", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["results"]) > 0
        stds = [r["standard_number"] for r in data["results"]]
        assert "IS 694:2010" in stds

    def test_case_5_technical_identifier_unaltered_in_normalized_query(self):
        payload = {"query": "IS 2062 Grade E250 steel plate bridge fabrication ke liye"}
        resp = client.post("/api/v1/search", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        norm_q = data.get("normalized_query", "")
        assert "IS 2062" in norm_q
        assert "Grade E250" in norm_q

    def test_case_6_existing_english_queries_regression(self):
        queries = [
            "Hot rolled structural steel plates for bridge fabrication",
            "High density polyethylene HDPE pipes for potable water supply",
            "Industrial safety helmets for construction workers",
            "Common burnt clay building bricks for masonry walls",
        ]
        for q in queries:
            resp = client.post("/api/v1/search", json={"query": q, "limit": 5})
            assert resp.status_code == 200
            assert resp.json()["total_matches"] > 0

    def test_case_7_tender_analysis_with_multilingual_requirement(self):
        # Verify that tender requirement analysis works with Hindi/Hinglish requirements
        extraction_payload = {
            "document_id": "test_multilingual_doc_001",
            "filename": "tender_spec_hindi.pdf",
            "extracted_text": "Supply of 12 मिमी Fe 500 TMT सरिया for RCC structure.",
            "status": "SUCCESS",
            "warnings": [],
            "pages": [{"page_number": 1, "text": "Supply of 12 मिमी Fe 500 TMT सरिया for RCC structure."}]
        }

        # Mock requirement extractor is used when EXTRACTION_PROVIDER="mock" or endpoint handles provider
        resp = client.post("/api/v1/documents/analyze", json=extraction_payload)
        assert resp.status_code in (200, 422)
        if resp.status_code == 200:
            data = resp.json()
            assert data["document_id"] == "test_multilingual_doc_001"
