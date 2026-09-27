import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import init_db, get_db_cursor
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
    # 1. Initialize SQLite schema
    init_db()

    # 2. Check and ensure database contains required seed data
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as cnt FROM standards")
            row = cursor.fetchone()
            std_count = row["cnt"] if row else 0
        if std_count == 0:
            logger.info("Standards table is empty. Running initial database seeding from fixtures...")
            from app.db.init_db import seed_database
            seed_database(reset=False)
            logger.info("Database seeding completed.")
    except Exception as e:
        logger.warning(f"Database seed check deferred/failed: {e}")

    # 3. Initialize Vector Store Collection & check indexing
    try:
        svc = get_embedding_service()
        store = get_vector_store()
        store.ensure_collection(dimension=svc.dimension)
        logger.info(f"Vector store initialized (collection: '{store.collection_name}').")

        # If freshly created collection has 0 points, index the seed standards
        col_info = store.get_collection_info()
        if col_info.get("points_count", 0) == 0:
            logger.info("Vector collection has 0 indexed points. Indexing seed standards...")
            from app.services.indexer import index_standards
            indexed = index_standards(embedding_svc=svc, vector_store=store)
            logger.info(f"Indexed {indexed} standards into vector store.")
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

# CORS middleware: configurable via FRONTEND_ORIGIN env var
raw_origins = [o.strip() for o in settings.FRONTEND_ORIGIN.split(",") if o.strip()] or ["*"]
allow_creds = settings.CORS_ALLOW_CREDENTIALS and ("*" not in raw_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=raw_origins,
    allow_credentials=allow_creds,
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
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT)
