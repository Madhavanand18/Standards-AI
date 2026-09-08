"""
Compliance API endpoints — deterministic BIS standard regulatory compliance & QCO metadata.

Endpoint: GET /api/v1/standards/{standard_number}/compliance

All data is grounded in verified Gazette notifications and BIS compulsory certification schemes.
No LLM inference is performed at any stage.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.compliance import StandardCompliance
from app.services.compliance import ComplianceService

router = APIRouter(prefix="/standards", tags=["Standard Compliance & QCO"])

_compliance_service = ComplianceService()


@router.get(
    "/{standard_number}/compliance",
    response_model=StandardCompliance,
    summary="Get verified regulatory compliance and QCO metadata for a BIS standard",
    description=(
        "Returns certification status, certification scheme, QCO applicability, "
        "issuing ministry, enforcement date, and official evidence source for the specified BIS standard. "
        "All data is sourced exclusively from official Gazette orders and BIS compulsory certification registries; "
        "no regulatory mandate is inferred by AI."
    ),
)
async def get_standard_compliance(standard_number: str) -> StandardCompliance:
    """
    Retrieve verified compliance metadata for a BIS standard.

    - **standard_number**: BIS standard number, e.g. ``IS+1786%3A2008`` or ``IS 2062:2011``.
    """
    comp = _compliance_service.get_compliance(standard_number)
    if comp is None:
        raise HTTPException(
            status_code=404,
            detail=f"No compliance record found for standard: '{standard_number}'. "
                   "Ensure the standard number matches exactly (e.g. 'IS 1786:2008').",
        )
    return comp
