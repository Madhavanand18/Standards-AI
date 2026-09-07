import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import init_db
from app.services.vector_store import get_vector_store
from app.services.embedding import get_embedding_service
from app.api.v1 import api_v1_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("standards_ai")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Standards-AI backend...")
    # Initialize SQLite tables
    init_db()
    # Initialize Vector Store Collection
    try:
        svc = get_embedding_service()
        store = get_vector_store()
        store.ensure_collection(dimension=svc.dimension)
        logger.info(f"Vector store initialized (collection: '{store.collection_name}').")
    except Exception as e:
        logger.warning(f"Vector store initialization deferred/failed: {e}")
    yield
    logger.info("Shutting down Standards-AI backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Core Semantic Recommendation Engine for Applicable Indian Standards (BIS) "
        "in Public Procurement. Provides deterministic, evidence-grounded search."
    ),
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for React / Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "ONLINE",
        "docs_url": "/docs",
        "health_url": f"{settings.API_V1_PREFIX}/health",
        "search_url": f"{settings.API_V1_PREFIX}/search"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
