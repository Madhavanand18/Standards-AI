import logging
from fastapi import APIRouter, HTTPException, Query, Depends, Path

from app.schemas.relationships import StandardRelationshipsResponse
from app.services.relationships import RelationshipService, get_relationship_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/standards/{standard_number}/relationships",
    response_model=StandardRelationshipsResponse,
    summary="Get related standards for a specific BIS standard",
    description=(
        "Retrieves verified, authoritative relationships (normative references, design codes, "
        "companion test methods, safety standards, and related products) for a given Indian Standard. "
        "Relationships are deterministically grounded in SQLite and include clause/evidence text."
    )
)
def get_standard_relationships(
    standard_number: str = Path(..., description="Standard number (e.g., 'IS 456:2000' or 'IS 456')"),
    relationship_type: str | None = Query(
        None,
        description="Filter by relationship type (e.g., 'normative_reference', 'design_code', 'related_product', 'safety', 'test_method', 'terminology')"
    ),
    service: RelationshipService = Depends(get_relationship_service)
):
    result = service.get_related_standards(
        standard_number=standard_number,
        relationship_type=relationship_type
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Standard '{standard_number}' was not found in the authoritative BIS database."
        )
    return result

@router.get(
    "/relationships",
    response_model=StandardRelationshipsResponse,
    summary="Query standard relationships via query parameter",
    description="Convenience query-parameter endpoint for retrieving related standards."
)
def query_relationships(
    standard_number: str = Query(..., description="Standard number (e.g., 'IS 456:2000' or 'IS 456')"),
    relationship_type: str | None = Query(
        None,
        description="Optional filter by relationship type"
    ),
    service: RelationshipService = Depends(get_relationship_service)
):
    result = service.get_related_standards(
        standard_number=standard_number,
        relationship_type=relationship_type
    )
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Standard '{standard_number}' was not found in the authoritative BIS database."
        )
    return result
