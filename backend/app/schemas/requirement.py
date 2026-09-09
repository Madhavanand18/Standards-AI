"""
Requirement extraction schemas for Run 6 Tender Intelligence.

Design principles:
- TenderRequirement is the ground-truth record for a single procurement requirement.
  original_text is immutable evidence; normalized_text is the cleaned retrieval query.
- Every requirement carries source_page / source_pages so the UI can show
  "this requirement came from page N of the tender".
- explicitly_referenced_standards ONLY contains IS numbers stated in the tender text.
  The BIS engine independently produces 'recommendations'; these two are kept separate.
- TenderAnalysisResponse is the complete document-level response.
"""
from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from app.schemas.search import StandardResult


class RequirementCategory(str, Enum):
    MATERIAL = "MATERIAL"
    DIMENSIONAL = "DIMENSIONAL"
    GRADE = "GRADE"
    PERFORMANCE = "PERFORMANCE"
    ELECTRICAL = "ELECTRICAL"
    MECHANICAL = "MECHANICAL"
    CHEMICAL = "CHEMICAL"
    SAFETY = "SAFETY"
    TESTING = "TESTING"
    INSPECTION = "INSPECTION"
    QUALITY = "QUALITY"
    INSTALLATION = "INSTALLATION"
    PACKING_MARKING = "PACKING_MARKING"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    OTHER = "OTHER"


class TechnicalParameter(BaseModel):
    """A single extracted technical parameter with its value and unit."""
    name: str = Field(..., description="Parameter name (e.g. 'diameter', 'voltage', 'grade')")
    value: str = Field(..., description="Extracted value from source text (e.g. '12', 'Fe 500', '450/750')")
    unit: str | None = Field(None, description="Unit of measurement if applicable (e.g. 'mm', 'V', 'MPa')")


class TenderRequirement(BaseModel):
    """
    A single procurement/technical requirement extracted from a tender document.

    Traceability guarantee:
    - original_text: verbatim text from the PDF (never paraphrased or invented).
    - source_page: primary page; source_pages: all contributing pages.
    - explicitly_referenced_standards: ONLY IS numbers literally present in the source text.
    """
    requirement_id: str = Field(..., description="Unique identifier for this requirement (e.g. 'REQ-001')")
    title: str = Field(..., description="Short descriptive title for the requirement")
    category: RequirementCategory = Field(
        default=RequirementCategory.OTHER,
        description="Technical category of the requirement"
    )
    original_text: str = Field(
        ...,
        description="Verbatim text from the tender document — evidence, never paraphrased"
    )
    normalized_text: str = Field(
        ...,
        description="Cleaned, normalized version of the requirement for BIS engine retrieval"
    )
    source_page: int = Field(..., description="Primary 1-indexed page number in the source PDF")
    source_pages: list[int] = Field(
        default_factory=list,
        description="All page numbers contributing to this requirement"
    )
    source_section: str | None = Field(
        None,
        description="Detected tender section name if reliably identified (e.g. 'Technical Specifications')"
    )
    mandatory_language: bool = Field(
        default=False,
        description="True if the source text contains mandatory language (shall, must, required)"
    )
    explicitly_referenced_standards: list[str] = Field(
        default_factory=list,
        description=(
            "IS/BIS standard numbers explicitly stated in the tender text (e.g. ['IS 1786:2008']). "
            "MUST remain empty if the tender does NOT mention a standard number."
        )
    )
    technical_parameters: list[TechnicalParameter] = Field(
        default_factory=list,
        description="Extracted technical parameters supported by source text"
    )
    extraction_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Provider confidence in this extraction (1.0 = high, <0.5 = uncertain)"
    )
    notes: str | None = Field(
        None,
        description="Optional extraction notes (e.g. ambiguity reason, merge notes)"
    )


class RequirementRecommendation(BaseModel):
    """
    Pairs a single extracted tender requirement with BIS standard recommendations
    from the existing search engine.

    Traceability: requirement.source_page → requirement text → BIS recommendations.
    The distinction between 'explicitly_referenced' and 'semantically recommended'
    is preserved at the requirement level (explicitly_referenced_standards field).
    """
    requirement: TenderRequirement
    recommendations: list[StandardResult] = Field(
        default_factory=list,
        description="BIS standards recommended by the existing search engine for this requirement"
    )
    search_query_used: str = Field(
        ...,
        description="The normalized_text actually sent to the BIS search engine"
    )
    recommendation_warnings: list[str] = Field(
        default_factory=list,
        description="Warnings specific to this requirement's search (e.g. 'zero results')"
    )


class TenderAnalysisResponse(BaseModel):
    """
    Complete tender analysis result for a document.

    Contains:
    - Extraction status and metadata
    - All extracted requirements with source-page traceability
    - BIS recommendations per requirement from the existing search engine
    """
    document_id: str = Field(..., description="Document ID from the Run 6A extraction")
    filename: str = Field(..., description="Original filename from the Run 6A extraction")
    extraction_status: str = Field(
        ...,
        description="Overall requirement extraction status: SUCCESS, PARTIAL, FAILED, NO_REQUIREMENTS"
    )
    extraction_warnings: list[str] = Field(
        default_factory=list,
        description="Warnings from the requirement extraction phase"
    )
    requirement_count: int = Field(..., description="Total number of extracted requirements")
    requirements: list[RequirementRecommendation] = Field(
        default_factory=list,
        description="Extracted requirements with BIS recommendations"
    )
    analysis_warnings: list[str] = Field(
        default_factory=list,
        description="Document-level analysis warnings"
    )
    anti_hallucination_note: str = Field(
        default=(
            "Requirement extraction uses LLM to identify technical requirements from tender text. "
            "BIS standard recommendations are produced exclusively by the deterministic semantic "
            "search engine using official BIS data. The LLM does not decide which standard is applicable."
        )
    )
