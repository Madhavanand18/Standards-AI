"""
Tender Analysis API — Run 6B+6C.

Endpoint: POST /documents/analyze

Accepts the DocumentExtractionResponse produced by Run 6A's /documents/upload
and returns TenderAnalysisResponse containing:
  - Structured technical requirements with source-page traceability
  - BIS standard recommendations per requirement (from the existing search engine)
  - Lifecycle, relationship, and compliance intelligence on each recommended standard

Design:
- Stateless: receives the full extraction payload; no server-side document storage needed.
- The LLM (via RequirementExtractor) extracts and normalizes requirements.
- The existing deterministic BIS search engine (embedding + Qdrant + ranker) produces recommendations.
- The LLM NEVER directly decides which standard is applicable.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.schemas.document import DocumentExtractionResponse, ExtractionStatus
from app.schemas.requirement import (
    RequirementRecommendation,
    TenderAnalysisResponse,
    TenderRequirement,
)
from app.schemas.search import StandardResult
from app.services.embedding import BaseEmbeddingService, get_embedding_service
from app.services.requirement_extractor import RequirementExtractor
from app.services.vector_store import QdrantVectorStore, get_vector_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Document Ingestion & Tender Processing"])


@router.post(
    "/analyze",
    response_model=TenderAnalysisResponse,
    summary="Extract technical requirements from a tender and find applicable BIS standards",
    description=(
        "Accepts the extraction result from /documents/upload, uses an LLM to identify "
        "structured technical procurement requirements, then searches the existing BIS "
        "standard database for applicable standards per requirement. "
        "Lifecycle, relationships, and compliance data are attached to each recommendation."
    ),
    status_code=status.HTTP_200_OK,
)
async def analyze_tender(
    extraction: DocumentExtractionResponse,
    vector_store: QdrantVectorStore = Depends(get_vector_store),
    embedding_svc: BaseEmbeddingService = Depends(get_embedding_service),
) -> TenderAnalysisResponse:
    """
    Full tender intelligence pipeline:
    1. Validate extraction has usable text.
    2. Extract structured requirements via LLM provider.
    3. For each requirement, search the existing BIS engine.
    4. Attach lifecycle/relationships/compliance to each recommended standard.
    5. Return TenderAnalysisResponse.
    """
    doc_id = extraction.document_id
    filename = extraction.filename

    # ── 1. Validate that extraction has usable content ────────────────────────
    if extraction.status == ExtractionStatus.FAILED.value and not extraction.extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The provided document extraction failed to produce any text. "
                "Cannot extract requirements from a document with no text content."
            ),
        )

    analysis_warnings: list[str] = list(extraction.warnings or [])
    if extraction.status == ExtractionStatus.PARTIAL.value:
        analysis_warnings.append(
            "Source document extraction was PARTIAL — some pages lacked text. "
            "Requirement coverage may be incomplete."
        )

    # ── 2. Extract requirements ───────────────────────────────────────────────
    try:
        extractor = RequirementExtractor()
        requirements, extraction_warnings = extractor.extract(extraction)
    except RuntimeError as exc:
        # Provider not configured (e.g., missing API key)
        logger.warning("Requirement extractor unavailable: %s", exc)
        return TenderAnalysisResponse(
            document_id=doc_id,
            filename=filename,
            extraction_status="FAILED",
            extraction_warnings=[str(exc)],
            requirement_count=0,
            requirements=[],
            analysis_warnings=analysis_warnings,
        )
    except Exception as exc:
        logger.error("Requirement extraction crashed for document %s: %s", doc_id, exc, exc_info=True)
        return TenderAnalysisResponse(
            document_id=doc_id,
            filename=filename,
            extraction_status="FAILED",
            extraction_warnings=[f"Requirement extraction error: {exc}"],
            requirement_count=0,
            requirements=[],
            analysis_warnings=analysis_warnings,
        )

    if not requirements:
        return TenderAnalysisResponse(
            document_id=doc_id,
            filename=filename,
            extraction_status="NO_REQUIREMENTS",
            extraction_warnings=extraction_warnings,
            requirement_count=0,
            requirements=[],
            analysis_warnings=analysis_warnings,
        )

    # ── 3 + 4. Search BIS engine per requirement ──────────────────────────────
    requirement_results: list[RequirementRecommendation] = []

    for req in requirements:
        rec_result = _search_for_requirement(
            requirement=req,
            vector_store=vector_store,
            embedding_svc=embedding_svc,
        )
        requirement_results.append(rec_result)

    # ── 5. Assemble response ──────────────────────────────────────────────────
    total = len(requirement_results)
    extraction_status = "SUCCESS" if not extraction_warnings else "PARTIAL"

    return TenderAnalysisResponse(
        document_id=doc_id,
        filename=filename,
        extraction_status=extraction_status,
        extraction_warnings=extraction_warnings,
        requirement_count=total,
        requirements=requirement_results,
        analysis_warnings=analysis_warnings,
    )


def _search_for_requirement(
    requirement: TenderRequirement,
    vector_store: QdrantVectorStore,
    embedding_svc: BaseEmbeddingService,
) -> RequirementRecommendation:
    """
    Searches the existing BIS engine for standards applicable to one requirement.
    Reuses the identical pipeline as the manual /search endpoint:
      embedding → Qdrant → rank_and_filter → lifecycle/relationships/compliance.

    Returns RequirementRecommendation with zero-or-more StandardResult items.
    A zero-result is valid (not an error).
    """
    from app.db.database import get_standard_by_number
    from app.services.compliance import ComplianceService
    from app.services.lifecycle import LifecycleService
    from app.services.ranker import rank_and_filter_candidates
    from app.services.relationships import get_relationship_service

    query_text = requirement.normalized_text.strip()
    rec_warnings: list[str] = []

    if not query_text:
        return RequirementRecommendation(
            requirement=requirement,
            recommendations=[],
            search_query_used="",
            recommendation_warnings=["normalized_text was empty; skipping search."],
        )

    try:
        query_vector = embedding_svc.embed_text(query_text)
        fetch_limit = max(settings.DEFAULT_SEARCH_LIMIT * 3, 20)
        raw_matches = vector_store.search(query_vector=query_vector, limit=fetch_limit)

        # Deduplicate and build candidates — same logic as search.py
        candidates: list[dict] = []
        seen_standards: set[str] = set()
        for m in raw_matches:
            payload = m.get("payload", {})
            std_number = payload.get("standard_number", "UNKNOWN")
            if std_number in seen_standards:
                continue
            seen_standards.add(std_number)
            raw_dense_score = round(m.get("score", 0.0), 4)
            db_record = get_standard_by_number(std_number) or {}
            full_scope = db_record.get("scope") or payload.get("scope", "")
            keywords = db_record.get("keywords") or payload.get("keywords") or []
            candidates.append({
                "db_id": db_record.get("id") or payload.get("db_id"),
                "standard_number": std_number,
                "title": db_record.get("title") or payload.get("title", ""),
                "dense_score": raw_dense_score,
                "similarity_score": raw_dense_score,
                "category": db_record.get("category") or payload.get("category"),
                "department": db_record.get("department") or payload.get("department"),
                "scope": full_scope,
                "scope_snippet": payload.get("scope_snippet") or (
                    full_scope[:280] + "..." if len(full_scope) > 280 else full_scope
                ),
                "keywords": keywords,
                "status": db_record.get("status") or payload.get("status", "ACTIVE"),
                "year_of_publication": db_record.get("year_of_publication") or payload.get("year_of_publication"),
                "edition": db_record.get("edition") or payload.get("edition"),
                "source_url": db_record.get("source_url") or payload.get("source_url"),
                "source_evidence_note": db_record.get("source_evidence_note") or payload.get("source_evidence_note"),
            })

        ranked_candidates = rank_and_filter_candidates(
            query=query_text,
            candidates=candidates,
            limit=settings.DEFAULT_SEARCH_LIMIT,
            threshold=settings.DEFAULT_SCORE_THRESHOLD,
        )

        # Attach lifecycle / relationships / compliance
        rel_service = get_relationship_service()
        lifecycle_service = LifecycleService()
        compliance_service = ComplianceService()

        results: list[StandardResult] = []
        for c in ranked_candidates:
            rel_data = rel_service.get_related_standards(c["standard_number"]) or {}
            rel_items = rel_data.get("relationships", [])
            rel_grouped = rel_data.get("grouped_by_type", {})
            lc_data = lifecycle_service.get_lifecycle(c["standard_number"])
            comp_data = compliance_service.get_compliance(c["standard_number"])

            results.append(StandardResult(
                db_id=c.get("db_id"),
                standard_number=c["standard_number"],
                title=c["title"],
                similarity_score=c["similarity_score"],
                relevance_label=c.get("relevance_label", "Medium"),
                explanation=c.get("explanation"),
                dense_score=c.get("dense_score"),
                metadata_score=c.get("metadata_score"),
                category=c.get("category"),
                department=c.get("department"),
                scope=c.get("scope", ""),
                scope_snippet=c.get("scope_snippet"),
                status=c.get("status", "ACTIVE"),
                year_of_publication=c.get("year_of_publication"),
                edition=c.get("edition"),
                source_url=c.get("source_url"),
                source_evidence_note=c.get("source_evidence_note"),
                relationships=rel_items,
                grouped_relationships=rel_grouped,
                lifecycle=lc_data,
                compliance=comp_data,
            ))

        if not results:
            rec_warnings.append(
                f"No BIS standards met the relevance threshold for: '{query_text[:80]}'"
            )

    except Exception as exc:
        logger.error(
            "BIS search failed for requirement '%s': %s",
            requirement.requirement_id, exc, exc_info=True,
        )
        rec_warnings.append(f"BIS search error: {exc}")
        results = []

    return RequirementRecommendation(
        requirement=requirement,
        recommendations=results,
        search_query_used=query_text,
        recommendation_warnings=rec_warnings,
    )
