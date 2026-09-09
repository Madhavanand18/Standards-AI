import logging
from fastapi import APIRouter, HTTPException, Query, Depends

from app.core.config import settings
from app.db.database import get_db_cursor, get_standard_by_number
from app.schemas.search import SearchRequest, SearchResponse, StandardResult, HealthResponse
from app.services.embedding import get_embedding_service, BaseEmbeddingService
from app.services.vector_store import get_vector_store, QdrantVectorStore
from app.services.ranker import rank_and_filter_candidates

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check(
    vector_store: QdrantVectorStore = Depends(get_vector_store),
    embedding_svc: BaseEmbeddingService = Depends(get_embedding_service)
):
    """
    Health check endpoint verifying database connectivity, vector index status,
    and embedding engine configuration.
    """
    standards_count = 0
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as cnt FROM standards")
            row = cursor.fetchone()
            standards_count = row["cnt"] if row else 0
    except Exception as e:
        logger.warning(f"Health check failed to query SQLite: {e}")

    collection_info = vector_store.get_collection_info()

    return HealthResponse(
        status="HEALTHY",
        project=settings.PROJECT_NAME,
        standards_in_db=standards_count,
        qdrant_collection_status=collection_info.get("status", "UNKNOWN"),
        points_indexed=collection_info.get("points_count", 0),
        embedding_model=embedding_svc.model_name if hasattr(embedding_svc, "model_name") else settings.EMBEDDING_MODEL_NAME,
        embedding_dimension=embedding_svc.dimension
    )


@router.post("/search", response_model=SearchResponse)
def search_standards(
    request: SearchRequest,
    vector_store: QdrantVectorStore = Depends(get_vector_store),
    embedding_svc: BaseEmbeddingService = Depends(get_embedding_service)
):
    """
    Semantic standards retrieval endpoint with domain metadata ranking and dynamic threshold filtering.
    Accepts procurement requirements or technical item description and returns
    relevance-ranked Indian Standards from Qdrant and SQLite.
    """
    query_text = request.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Search query must not be empty.")

    try:
        # 1. Generate dense query embedding locally
        query_vector = embedding_svc.embed_text(query_text)

        # 2. Retrieve candidate standards by cosine similarity from Qdrant
        fetch_limit = max(request.limit * 3, 20)
        raw_matches = vector_store.search(
            query_vector=query_vector,
            limit=fetch_limit
        )

        # 3. Format and deduplicate raw matches with canonical SQLite BIS metadata
        candidates: list[dict] = []
        seen_standards: set[str] = set()
        for m in raw_matches:
            payload = m.get("payload", {})
            std_number = payload.get("standard_number", "UNKNOWN")

            # Deduplicate by standard_number, keeping highest raw dense score
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
                "scope_snippet": payload.get("scope_snippet") or (full_scope[:280] + "..." if len(full_scope) > 280 else full_scope),
                "keywords": keywords,
                "status": db_record.get("status") or payload.get("status", "ACTIVE"),
                "year_of_publication": db_record.get("year_of_publication") or payload.get("year_of_publication"),
                "edition": db_record.get("edition") or payload.get("edition"),
                "source_url": db_record.get("source_url") or payload.get("source_url"),
                "source_evidence_note": db_record.get("source_evidence_note") or payload.get("source_evidence_note")
            })

        # 4. Re-rank with metadata enhancement and dynamic threshold filtering
        ranked_candidates = rank_and_filter_candidates(
            query=query_text,
            candidates=candidates,
            limit=request.limit,
            threshold=request.score_threshold
        )

        # 5. Format results with attached verified relationships, lifecycle, and compliance metadata
        from app.services.relationships import get_relationship_service
        from app.services.lifecycle import LifecycleService
        from app.services.compliance import ComplianceService
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

            results.append(
                StandardResult(
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
                    compliance=comp_data
                )
            )


        return SearchResponse(
            query=query_text,
            total_matches=len(results),
            results=results
        )

    except Exception as e:
        logger.error(f"Search failed for query '{query_text}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {str(e)}"
        )
