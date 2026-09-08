import logging
from fastapi import APIRouter, HTTPException, Query, Depends

from app.core.config import settings
from app.db.database import get_db_cursor, get_standard_by_number
from app.schemas.search import SearchRequest, SearchResponse, StandardResult, HealthResponse
from app.services.embedding import get_embedding_service, BaseEmbeddingService
from app.services.vector_store import get_vector_store, QdrantVectorStore

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
    Semantic standards retrieval endpoint.
    Accepts procurement requirements or technical item description and returns
    relevance-ranked Indian Standards from Qdrant and SQLite.
    """
    query_text = request.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Search query must not be empty.")

    try:
        # 1. Generate dense query embedding locally
        query_vector = embedding_svc.embed_text(query_text)

        # 2. Retrieve top matching standards by cosine similarity
        matches = vector_store.search(
            query_vector=query_vector,
            limit=request.limit
        )

        # 3. Format results with canonical SQLite BIS metadata (deduplicating by standard_number)
        results: list[StandardResult] = []
        seen_standards: set[str] = set()
        for m in matches:
            payload = m.get("payload", {})
            std_number = payload.get("standard_number", "UNKNOWN")

            # Deduplicate by standard_number, keeping only the highest-scoring result
            if std_number in seen_standards:
                continue
            seen_standards.add(std_number)

            score = round(m.get("score", 0.0), 4)

            # Ensure confidence is clamped between 0 and 1
            clamped_score = max(0.0, min(1.0, score))

            db_record = get_standard_by_number(std_number) or {}
            full_scope = db_record.get("scope") or payload.get("scope", "")

            results.append(
                StandardResult(
                    db_id=db_record.get("id") or payload.get("db_id"),
                    standard_number=std_number,
                    title=db_record.get("title") or payload.get("title", ""),
                    similarity_score=clamped_score,
                    category=db_record.get("category") or payload.get("category"),
                    department=db_record.get("department") or payload.get("department"),
                    scope=full_scope,
                    scope_snippet=payload.get("scope_snippet") or (full_scope[:280] + "..." if len(full_scope) > 280 else full_scope),
                    status=db_record.get("status") or payload.get("status", "ACTIVE"),
                    year_of_publication=db_record.get("year_of_publication") or payload.get("year_of_publication"),
                    edition=db_record.get("edition") or payload.get("edition"),
                    source_url=db_record.get("source_url") or payload.get("source_url"),
                    source_evidence_note=db_record.get("source_evidence_note") or payload.get("source_evidence_note")
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
