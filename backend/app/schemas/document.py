from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class ExtractionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class PageExtraction(BaseModel):
    """
    Extracted text and structural metadata for an individual PDF page.
    Preserves page boundaries and reading order.
    """
    page_number: int = Field(..., description="1-indexed page number from the original PDF")
    raw_text: str = Field(..., description="Unmodified extracted text from the page")
    cleaned_text: str = Field(..., description="Normalized text preserving technical identifiers and specs")
    character_count: int = Field(..., description="Number of characters in cleaned text")
    word_count: int = Field(..., description="Number of words in cleaned text")
    has_text: bool = Field(..., description="True if extractable text exists on this page")
    detected_headings: list[str] = Field(
        default_factory=list,
        description="Lightweight deterministic section or heading titles detected on this page"
    )


class DocumentMetadata(BaseModel):
    """
    Deterministic extraction quality and content statistics.
    """
    total_characters: int = 0
    total_words: int = 0
    pages_with_text: int = 0
    pages_without_text: int = 0
    detected_sections: list[str] = Field(default_factory=list)


class DocumentExtractionResponse(BaseModel):
    """
    Complete response model for document ingestion and text extraction.
    Traceable to page-level content for downstream requirement analysis.
    """
    document_id: str = Field(..., description="Collision-resistant unique identifier (UUID)")
    filename: str = Field(..., description="Sanitized original document filename")
    content_type: str = Field(default="application/pdf", description="MIME content type")
    file_size: int = Field(..., description="File size in bytes")
    page_count: int = Field(..., description="Total number of pages in the PDF")
    status: str = Field(default=ExtractionStatus.SUCCESS.value, description="Extraction status (SUCCESS, PARTIAL, FAILED)")
    extracted_text: str = Field(..., description="Combined cleaned text across all pages")
    pages: list[PageExtraction] = Field(default_factory=list, description="Page-by-page extractions")
    warnings: list[str] = Field(default_factory=list, description="Extraction warnings, e.g. image-only pages or parsing issues")
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata, description="Extraction statistics and quality metrics")
