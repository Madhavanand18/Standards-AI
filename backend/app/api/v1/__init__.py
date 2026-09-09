from fastapi import APIRouter
from app.api.v1.search import router as search_router
from app.api.v1.relationships import router as relationships_router
from app.api.v1.lifecycle import router as lifecycle_router
from app.api.v1.compliance import router as compliance_router
from app.api.v1.documents import router as documents_router
from app.api.v1.tender_analysis import router as tender_analysis_router

api_v1_router = APIRouter()
api_v1_router.include_router(search_router, tags=["Standards Search"])
api_v1_router.include_router(relationships_router, tags=["Standard Relationships"])
api_v1_router.include_router(lifecycle_router, tags=["Standard Lifecycle"])
api_v1_router.include_router(compliance_router, tags=["Standard Compliance & QCO"])
api_v1_router.include_router(documents_router, tags=["Document Ingestion & Tender Processing"])
api_v1_router.include_router(tender_analysis_router, tags=["Document Ingestion & Tender Processing"])
