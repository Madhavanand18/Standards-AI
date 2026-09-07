import logging
from typing import Any

from app.db.database import get_all_standards
from app.services.embedding import get_embedding_service, BaseEmbeddingService
from app.services.vector_store import get_vector_store, QdrantVectorStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def build_semantic_text(standard: dict[str, Any]) -> str:
    """
    Constructs a rich text representation of the standard for embedding.
    Combines standard number, title, category, keywords, and scope.
    """
    parts = []
    if standard.get("standard_number"):
        parts.append(f"Standard: {standard['standard_number']}")
    if standard.get("title"):
        parts.append(f"Title: {standard['title']}")
    if standard.get("category"):
        parts.append(f"Category: {standard['category']}")
    keywords = standard.get("keywords")
    if keywords:
        if isinstance(keywords, list):
            parts.append(f"Keywords: {', '.join(keywords)}")
        elif isinstance(keywords, str):
            parts.append(f"Keywords: {keywords}")
    if standard.get("scope"):
        parts.append(f"Scope: {standard['scope']}")
    return " | ".join(parts)

def index_standards(
    embedding_svc: BaseEmbeddingService | None = None,
    vector_store: QdrantVectorStore | None = None
) -> int:
    """
    Reads all standards from SQLite, generates dense embeddings,
    and indexes them into Qdrant.
    """
    logger.info("Starting standards indexing pipeline...")
    standards = get_all_standards()
    if not standards:
        logger.warning("No standards found in SQLite to index. Run app.db.init_db first.")
        return 0

    logger.info(f"Found {len(standards)} standards in SQLite database.")

    svc = embedding_svc or get_embedding_service()
    store = vector_store or get_vector_store()

    # Ensure collection exists with correct dimension
    store.ensure_collection(dimension=svc.dimension)

    # Build semantic texts
    texts = [build_semantic_text(s) for s in standards]
    logger.info(f"Generating dense embeddings for {len(texts)} standards using {svc.dimension}-d model...")
    embeddings = svc.embed_batch(texts)

    # Upsert into Qdrant
    logger.info("Upserting vectors and metadata into Qdrant...")
    count = store.upsert_records(records=standards, vectors=embeddings)
    logger.info(f"Successfully indexed {count} standards into Qdrant collection '{store.collection_name}'.")
    return count

if __name__ == "__main__":
    index_standards()
