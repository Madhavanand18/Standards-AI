from fastapi import APIRouter
from app.api.v1.search import router as search_router
from app.api.v1.relationships import router as relationships_router

api_v1_router = APIRouter()
api_v1_router.include_router(search_router, tags=["Standards Search"])
api_v1_router.include_router(relationships_router, tags=["Standard Relationships"])

