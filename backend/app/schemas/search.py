from pydantic import BaseModel, Field
from typing import Any
from app.core.config import settings

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Technical specification or product description for procurement")
    limit: int = Field(
        default=settings.DEFAULT_SEARCH_LIMIT,
        ge=1,
        le=settings.MAX_SEARCH_LIMIT,
        description="Maximum number of standards to return"
    )

class StandardResult(BaseModel):
    db_id: int | None = None
    standard_number: str
    title: str
    similarity_score: float
    category: str | None = None
    department: str | None = None
    scope: str
    scope_snippet: str | None = None
    status: str = "ACTIVE"
    year_of_publication: int | None = None
    edition: str | None = None
    source_url: str | None = None
    source_evidence_note: str | None = None

class SearchResponse(BaseModel):
    query: str
    total_matches: int
    results: list[StandardResult]
    audit_disclaimer: str = (
        "Anti-Hallucination Disclaimer: Semantic similarity scores indicate mathematical "
        "relevance to official BIS standard scopes. These results represent potentially applicable "
        "standards and do not constitute legal certification or formal procurement authority approval."
    )

class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    project: str
    standards_in_db: int
    qdrant_collection_status: str
    points_indexed: int
    embedding_model: str
    embedding_dimension: int
