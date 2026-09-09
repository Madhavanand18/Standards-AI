"""
Requirement Extraction Service — Run 6B.

Architecture:
  BaseExtractionProvider     abstract interface
  GeminiExtractionProvider   Google Gemini with Pydantic structured output
  MockExtractionProvider     deterministic, testable, no network dependency

  RequirementExtractor       orchestrates chunking, provider calls, and merging

Design principles:
- The LLM identifies and normalizes procurement requirements.
- The LLM NEVER decides which BIS standard is applicable.
- original_text is verbatim evidence from the PDF — never paraphrased.
- normalized_text is the cleaned query sent to the BIS search engine.
- explicitly_referenced_standards contains only IS numbers present in the source text.
- Duplicate requirements (same subject across chunks) are merged deterministically.
- One chunk failure does not abort the entire extraction.
"""
from __future__ import annotations

import hashlib
import logging
import re
import uuid
from abc import ABC, abstractmethod
from typing import Any

from app.core.config import settings
from app.schemas.document import DocumentExtractionResponse, PageExtraction
from app.schemas.requirement import (
    RequirementCategory,
    TechnicalParameter,
    TenderRequirement,
)

logger = logging.getLogger(__name__)

# ── IS standard number detection regex ──────────────────────────────────────
# Matches: IS 1786:2008, IS 2062:2011, IS 15298 (Part 2):2016, IS 694:2010
_IS_NUMBER_RE = re.compile(
    r"\bIS\s+\d[\d\s]*(?:\(Part\s+\d+\))?(?::\s*\d{4})?\b",
    re.IGNORECASE,
)

# ── Pages whose headings signal technical content ────────────────────────────
_TECHNICAL_SECTION_KEYWORDS = {
    "technical specifications",
    "technical requirements",
    "quality assurance",
    "schedule of requirements",
    "scope of work",
}


def _is_technical_section(page: PageExtraction) -> bool:
    """Returns True if this page belongs to a known technical/specification section."""
    for h in page.detected_headings:
        if any(kw in h.lower() for kw in _TECHNICAL_SECTION_KEYWORDS):
            return True
    return False


def _has_is_reference(text: str) -> bool:
    """Returns True if the text contains an explicit IS standard reference."""
    return bool(_IS_NUMBER_RE.search(text))


def _word_count(text: str) -> int:
    return len(text.split())


# ─────────────────────────────────────────────────────────────────────────────
#  Pydantic model used as the Gemini structured output schema
# ─────────────────────────────────────────────────────────────────────────────
from pydantic import BaseModel, Field as PydanticField


class _LLMParameter(BaseModel):
    name: str
    value: str
    unit: str | None = None


class _LLMRequirement(BaseModel):
    """
    Schema for a single requirement as returned by the LLM.
    Kept separate from TenderRequirement so the LLM sees a minimal, focused schema.
    """
    title: str = PydanticField(description="Short descriptive title")
    category: str = PydanticField(
        description=(
            "One of: MATERIAL, DIMENSIONAL, GRADE, PERFORMANCE, ELECTRICAL, MECHANICAL, "
            "CHEMICAL, SAFETY, TESTING, INSPECTION, QUALITY, INSTALLATION, PACKING_MARKING, "
            "ENVIRONMENTAL, OTHER"
        )
    )
    original_text: str = PydanticField(
        description="Verbatim text from the tender. Must not be paraphrased or invented."
    )
    normalized_text: str = PydanticField(
        description="Clean normalized version suitable as a BIS search query"
    )
    source_page: int = PydanticField(description="1-indexed page number in the PDF")
    source_section: str | None = PydanticField(None, description="Section name if detectable")
    mandatory_language: bool = PydanticField(
        default=False,
        description="True if source contains 'shall', 'must', 'required'"
    )
    explicitly_referenced_standards: list[str] = PydanticField(
        default_factory=list,
        description=(
            "IS numbers literally stated in the source text (e.g. ['IS 1786:2008']). "
            "MUST be empty if no IS number appears."
        )
    )
    technical_parameters: list[_LLMParameter] = PydanticField(
        default_factory=list,
        description="Technical parameters supported by source text"
    )
    extraction_confidence: float = PydanticField(
        default=1.0,
        description="Confidence 0.0–1.0"
    )
    notes: str | None = PydanticField(None)


class _LLMExtractionResult(BaseModel):
    requirements: list[_LLMRequirement] = PydanticField(
        default_factory=list,
        description="List of extracted technical procurement requirements"
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Provider abstraction
# ─────────────────────────────────────────────────────────────────────────────

class BaseExtractionProvider(ABC):
    """Abstract interface for requirement extraction providers."""

    @abstractmethod
    def extract(self, chunk_text: str, page_numbers: list[int]) -> list[_LLMRequirement]:
        """
        Extract technical requirements from the given text chunk.

        Args:
            chunk_text: Text from one or more PDF pages.
            page_numbers: Page numbers that produced this text (for attribution).

        Returns:
            List of _LLMRequirement objects; empty list if none found.
            Must never raise on malformed output — return empty list or partial results.
        """
        ...


class GeminiExtractionProvider(BaseExtractionProvider):
    """
    Extracts requirements using Google Gemini with Pydantic structured output.
    Reads API key from settings.GEMINI_API_KEY (environment variable GEMINI_API_KEY).
    """

    _SYSTEM_PROMPT = (
        "You are a procurement document analysis assistant for the Government of India. "
        "Your task is to identify TECHNICAL procurement requirements from tender text. "
        "\n\n"
        "EXTRACT requirements that specify:\n"
        "- Product/material, dimensions, grades, capacity, performance\n"
        "- Electrical, mechanical, or chemical characteristics\n"
        "- Safety, testing, inspection, quality requirements\n"
        "- Installation, packing, marking, or environmental requirements\n"
        "\n"
        "DO NOT extract:\n"
        "- Bid submission deadlines, payment terms, arbitration clauses\n"
        "- Bank guarantee requirements, bidder financial eligibility\n"
        "- General commercial or legal clauses\n"
        "\n"
        "CRITICAL RULES:\n"
        "1. original_text must be verbatim from the tender. Never paraphrase or invent.\n"
        "2. explicitly_referenced_standards must list ONLY IS numbers literally in the text.\n"
        "   If no IS number appears in the text, leave the list empty.\n"
        "3. Do NOT invent standard numbers, values, grades, or quantities.\n"
        "4. If uncertain, lower extraction_confidence; do not guess.\n"
        "5. source_page must match the page number indicated in the text header."
    )

    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Set the GEMINI_API_KEY environment variable to use the Gemini provider. "
                "Alternatively, set EXTRACTION_PROVIDER=mock for offline/test use."
            )
        try:
            from google import genai
            from google.genai import types as genai_types
            self._genai = genai
            self._genai_types = genai_types
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        except ImportError as e:
            raise ImportError(
                "google-genai is not installed. Run: pip install google-genai"
            ) from e

        self._model = settings.GEMINI_REQUIREMENT_MODEL

    def extract(self, chunk_text: str, page_numbers: list[int]) -> list[_LLMRequirement]:
        pages_label = ", ".join(str(p) for p in page_numbers)
        prompt = (
            f"The following text is from pages {pages_label} of a procurement tender document. "
            "Extract all technical procurement requirements as structured JSON.\n\n"
            f"--- TENDER TEXT ---\n{chunk_text}\n--- END TENDER TEXT ---"
        )

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=self._genai_types.GenerateContentConfig(
                    system_instruction=self._SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=_LLMExtractionResult,
                    temperature=0.1,  # low temperature for factual extraction
                ),
            )
            result: _LLMExtractionResult = response.parsed
            return result.requirements if result and result.requirements else []
        except Exception as exc:
            logger.error("Gemini extraction failed for pages %s: %s", pages_label, exc)
            return []


class MockExtractionProvider(BaseExtractionProvider):
    """
    Deterministic mock provider for automated tests and offline use.

    Scans the text for known technical patterns and produces realistic
    TenderRequirement records without any network call.
    """

    # Each entry: (regex pattern, title, category, normalized_text template)
    _RULES: list[tuple[re.Pattern, str, str, str]] = [
        (
            re.compile(r"(?:Fe\s*500|TMT|deformed\s+(?:steel\s+)?bar)", re.IGNORECASE),
            "TMT Reinforcement Steel Bar",
            "GRADE",
            "high strength deformed TMT steel bars concrete reinforcement",
        ),
        (
            re.compile(r"structural\s+steel|hot\s+rolled\s+steel|Grade\s+E250|IS\s+2062", re.IGNORECASE),
            "Structural Steel Sections",
            "MATERIAL",
            "structural steel plates sections hot rolled medium high tensile",
        ),
        (
            re.compile(r"PVC\s+insulated|copper\s+cable|450/750\s*V", re.IGNORECASE),
            "PVC Insulated Copper Cable",
            "ELECTRICAL",
            "PVC insulated copper cable 450 750 V electrical wiring",
        ),
        (
            re.compile(r"cement|OPC|Portland", re.IGNORECASE),
            "Portland Cement",
            "MATERIAL",
            "ordinary Portland cement OPC construction concrete",
        ),
        (
            re.compile(r"pipe|plumbing|GI\s+pipe|HDPE", re.IGNORECASE),
            "Pipes and Plumbing Material",
            "MATERIAL",
            "pipes plumbing galvanized iron HDPE water supply",
        ),
    ]

    def extract(self, chunk_text: str, page_numbers: list[int]) -> list[_LLMRequirement]:
        results: list[_LLMRequirement] = []
        primary_page = page_numbers[0] if page_numbers else 1
        seen_titles: set[str] = set()

        # Extract IS references from chunk
        is_refs = [m.group().strip() for m in _IS_NUMBER_RE.finditer(chunk_text)]
        # Normalize IS refs (remove extra spaces)
        is_refs = [re.sub(r"\s+", " ", r) for r in is_refs]
        is_refs_deduped = list(dict.fromkeys(is_refs))

        for pattern, title, category, normalized in self._RULES:
            match = pattern.search(chunk_text)
            if not match or title in seen_titles:
                continue
            seen_titles.add(title)

            # Extract the sentence/clause containing the match (up to 300 chars)
            start = max(0, match.start() - 50)
            end = min(len(chunk_text), match.end() + 250)
            snippet = chunk_text[start:end].strip()
            # Clip at sentence boundary if possible
            for delim in ["\n\n", "\n", ". "]:
                parts = snippet.split(delim)
                if len(parts) > 1:
                    snippet = parts[0].strip()
                    break

            # Only include IS refs that appear near this match
            relevant_refs = [r for r in is_refs_deduped if r.upper() in chunk_text[start:end].upper()]

            # Extract simple parameters
            params: list[_LLMParameter] = []
            # diameter
            dm = re.search(r"(\d+(?:\.\d+)?)\s*mm", chunk_text[start:end])
            if dm:
                params.append(_LLMParameter(name="diameter", value=dm.group(1), unit="mm"))
            # grade
            gm = re.search(r"Fe\s*(\d+[A-Z]*)", chunk_text[start:end])
            if gm:
                params.append(_LLMParameter(name="grade", value=f"Fe {gm.group(1)}", unit=None))
            # voltage
            vm = re.search(r"(\d+/\d+)\s*V", chunk_text[start:end])
            if vm:
                params.append(_LLMParameter(name="voltage", value=vm.group(1), unit="V"))
            # Grade E250
            em = re.search(r"Grade\s+(E\d+)", chunk_text[start:end])
            if em:
                params.append(_LLMParameter(name="grade", value=em.group(1), unit=None))

            mandatory = bool(re.search(r"\b(?:shall|must|required|conform)\b", chunk_text[start:end], re.IGNORECASE))

            results.append(_LLMRequirement(
                title=title,
                category=category,
                original_text=snippet or match.group(),
                normalized_text=normalized,
                source_page=primary_page,
                source_section=None,
                mandatory_language=mandatory,
                explicitly_referenced_standards=relevant_refs,
                technical_parameters=params,
                extraction_confidence=0.90,
                notes="Extracted by MockExtractionProvider",
            ))

        return results


# ─────────────────────────────────────────────────────────────────────────────
#  Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class RequirementExtractor:
    """
    Orchestrates requirement extraction from a DocumentExtractionResponse.

    Steps:
    1. Select relevant pages (technical sections first; fallback to all pages with text).
    2. For small docs (≤ REQUIREMENT_MAX_CHUNK_WORDS): one provider call.
       For larger docs: split into bounded chunks.
    3. Call provider per chunk; collect _LLMRequirement lists.
    4. Convert to TenderRequirement, assign IDs.
    5. Deterministically merge near-duplicate requirements.
    """

    def __init__(self, provider: BaseExtractionProvider | None = None) -> None:
        self._provider = provider or _build_provider()

    def extract(
        self,
        doc: DocumentExtractionResponse,
    ) -> tuple[list[TenderRequirement], list[str]]:
        """
        Returns (requirements, warnings).
        Never raises — returns ([], [warning]) on total failure.
        """
        warnings: list[str] = []

        pages_with_text = [p for p in doc.pages if p.has_text]
        if not pages_with_text:
            return [], ["No extractable text found. Cannot extract requirements."]

        # ── Step 1: select pages ──────────────────────────────────────────────
        technical_pages = [p for p in pages_with_text if _is_technical_section(p)]
        candidate_pages = technical_pages if technical_pages else pages_with_text

        # ── Step 2: chunk ─────────────────────────────────────────────────────
        chunks = _make_chunks(candidate_pages, settings.REQUIREMENT_MAX_CHUNK_WORDS)

        # ── Step 3: extract per chunk ─────────────────────────────────────────
        raw_requirements: list[_LLMRequirement] = []
        for chunk_text, page_nums in chunks:
            try:
                found = self._provider.extract(chunk_text, page_nums)
                raw_requirements.extend(found)
            except Exception as exc:
                logger.error("Provider failed for pages %s: %s", page_nums, exc)
                warnings.append(f"Extraction failed for pages {page_nums}: {exc}")

        if not raw_requirements:
            return [], warnings + ["No technical requirements could be identified in this document."]

        # ── Step 4: convert to TenderRequirement ─────────────────────────────
        converted = _convert_to_tender_requirements(raw_requirements)

        # ── Step 5: merge duplicates ──────────────────────────────────────────
        merged = _merge_requirements(converted)

        logger.info(
            "Extracted %d requirements from document '%s' (%d raw → %d merged)",
            len(merged), doc.filename, len(raw_requirements), len(merged),
        )
        return merged, warnings


# ─────────────────────────────────────────────────────────────────────────────
#  Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _build_provider() -> BaseExtractionProvider:
    """Instantiate the provider specified in settings."""
    if settings.EXTRACTION_PROVIDER.lower() == "mock":
        return MockExtractionProvider()
    if settings.EXTRACTION_PROVIDER.lower() == "gemini":
        return GeminiExtractionProvider()
    raise ValueError(
        f"Unknown EXTRACTION_PROVIDER: '{settings.EXTRACTION_PROVIDER}'. "
        "Supported values: 'gemini', 'mock'."
    )


def _make_chunks(
    pages: list[PageExtraction],
    max_words: int,
) -> list[tuple[str, list[int]]]:
    """
    Produces (chunk_text, [page_numbers]) pairs.
    For small total content: one chunk with all pages.
    For larger content: splits at page boundaries without exceeding max_words.
    """
    # Build page header + text pairs
    page_entries: list[tuple[int, str]] = []
    for p in pages:
        header = f"[Page {p.page_number}]"
        page_entries.append((p.page_number, f"{header}\n{p.cleaned_text}"))

    # Total words across all candidate pages
    total_words = sum(_word_count(text) for _, text in page_entries)

    if total_words <= max_words:
        combined = "\n\n".join(text for _, text in page_entries)
        page_nums = [pn for pn, _ in page_entries]
        return [(combined, page_nums)]

    # Split into bounded chunks
    chunks: list[tuple[str, list[int]]] = []
    current_texts: list[str] = []
    current_pages: list[int] = []
    current_words = 0

    for page_num, text in page_entries:
        pw = _word_count(text)
        if current_words + pw > max_words and current_texts:
            chunks.append(("\n\n".join(current_texts), current_pages))
            current_texts = []
            current_pages = []
            current_words = 0
        current_texts.append(text)
        current_pages.append(page_num)
        current_words += pw

    if current_texts:
        chunks.append(("\n\n".join(current_texts), current_pages))

    return chunks


def _convert_to_tender_requirements(
    raw: list[_LLMRequirement],
) -> list[TenderRequirement]:
    """Convert _LLMRequirement → TenderRequirement, assigning sequential IDs."""
    result: list[TenderRequirement] = []
    for idx, r in enumerate(raw, start=1):
        try:
            category = RequirementCategory(r.category.upper())
        except ValueError:
            category = RequirementCategory.OTHER

        params = [
            TechnicalParameter(name=p.name, value=p.value, unit=p.unit)
            for p in (r.technical_parameters or [])
        ]

        # Clean explicitly_referenced_standards: keep only strings that look like IS numbers
        clean_refs = [
            s.strip()
            for s in (r.explicitly_referenced_standards or [])
            if s and _IS_NUMBER_RE.search(s)
        ]

        result.append(TenderRequirement(
            requirement_id=f"REQ-{idx:03d}",
            title=r.title or f"Requirement {idx}",
            category=category,
            original_text=r.original_text or "",
            normalized_text=r.normalized_text or r.title or "",
            source_page=r.source_page,
            source_pages=[r.source_page],
            source_section=r.source_section,
            mandatory_language=r.mandatory_language,
            explicitly_referenced_standards=clean_refs,
            technical_parameters=params,
            extraction_confidence=max(0.0, min(1.0, r.extraction_confidence)),
            notes=r.notes,
        ))
    return result


def _requirement_fingerprint(req: TenderRequirement) -> str:
    """
    Stable fingerprint used to detect likely duplicates.
    Based on normalized title (lowercased, punctuation-stripped).
    """
    clean = re.sub(r"[^a-z0-9\s]", "", req.title.lower())
    tokens = sorted(t for t in clean.split() if len(t) > 2)
    return hashlib.md5(" ".join(tokens).encode()).hexdigest()


def _merge_requirements(reqs: list[TenderRequirement]) -> list[TenderRequirement]:
    """
    Deterministically merges probable duplicate requirements.

    Merge rules:
    - Same fingerprint → merge.
    - Merged record keeps: longest original_text, union of source_pages,
      union of explicit standards, union of parameters (by name), minimum source_page.
    - If fingerprints differ → keep separate (never invent merges).
    """
    seen: dict[str, TenderRequirement] = {}
    order: list[str] = []

    for req in reqs:
        fp = _requirement_fingerprint(req)
        if fp not in seen:
            seen[fp] = req
            order.append(fp)
        else:
            existing = seen[fp]
            # Merge source pages
            merged_pages = sorted(set(existing.source_pages + req.source_pages))
            primary_page = merged_pages[0]
            # Keep the longer (more complete) original_text
            best_text = (
                req.original_text
                if len(req.original_text) > len(existing.original_text)
                else existing.original_text
            )
            # Union of explicit standards
            merged_refs = list(dict.fromkeys(
                existing.explicitly_referenced_standards + req.explicitly_referenced_standards
            ))
            # Union of parameters by name (first occurrence wins)
            param_by_name: dict[str, TechnicalParameter] = {
                p.name: p for p in existing.technical_parameters
            }
            for p in req.technical_parameters:
                if p.name not in param_by_name:
                    param_by_name[p.name] = p
            # Higher confidence wins
            conf = max(existing.extraction_confidence, req.extraction_confidence)
            seen[fp] = TenderRequirement(
                requirement_id=existing.requirement_id,
                title=existing.title,
                category=existing.category,
                original_text=best_text,
                normalized_text=existing.normalized_text,
                source_page=primary_page,
                source_pages=merged_pages,
                source_section=existing.source_section or req.source_section,
                mandatory_language=existing.mandatory_language or req.mandatory_language,
                explicitly_referenced_standards=merged_refs,
                technical_parameters=list(param_by_name.values()),
                extraction_confidence=conf,
                notes=(
                    f"Merged from pages {merged_pages}. "
                    + (existing.notes or "")
                ).strip(),
            )

    # Re-assign sequential IDs after merge
    merged_list = [seen[fp] for fp in order]
    for idx, req in enumerate(merged_list, start=1):
        object.__setattr__(req, "requirement_id", f"REQ-{idx:03d}") if False else None
        merged_list[idx - 1] = req.model_copy(update={"requirement_id": f"REQ-{idx:03d}"})

    return merged_list
