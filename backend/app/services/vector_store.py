import logging
from pathlib import Path
from typing import Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import settings

logger = logging.getLogger(__name__)

class QdrantVectorStore:
    def __init__(
        self,
        url: str | None = None,
        storage_path: Path | str | None = None,
        collection_name: str | None = None
    ):
        self.collection_name = collection_name or settings.QDRANT_COLLECTION_NAME
        self.url = url or settings.QDRANT_URL
        self.storage_path = Path(storage_path or settings.QDRANT_STORAGE_PATH)

        if self.url:
            logger.info(f"Connecting to remote Qdrant server at: {self.url}")
            self.client = QdrantClient(url=self.url)
        elif str(self.storage_path) == ":memory:":
            logger.info("Using in-memory Qdrant storage")
            self.client = QdrantClient(location=":memory:")
        else:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using local embedded Qdrant storage at: {self.storage_path}")
            # Retry a few times in case previous reload worker is releasing file lock
            import time
            for attempt in range(4):
                try:
                    self.client = QdrantClient(path=str(self.storage_path))
                    break
                except RuntimeError as e:
                    if "already accessed" in str(e) and attempt < 3:
                        logger.warning(f"Qdrant lock busy, retrying in 0.5s (attempt {attempt + 1}/3)...")
                        time.sleep(0.5)
                    else:
                        raise

    def ensure_collection(self, dimension: int = 384) -> None:
        """Ensures the collection exists with correct vector size and Cosine distance."""
        existing_collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in existing_collections:
            logger.info(f"Creating Qdrant collection: '{self.collection_name}' (dim={dimension}, metric=Cosine)...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=dimension,
                    distance=qmodels.Distance.COSINE
                )
            )
            logger.info(f"Collection '{self.collection_name}' created.")
        else:
            logger.info(f"Collection '{self.collection_name}' already exists.")

    def recreate_collection(self, dimension: int = 384) -> None:
        """Deletes collection if exists and creates a clean new collection."""
        existing_collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name in existing_collections:
            logger.info(f"Recreating Qdrant collection '{self.collection_name}'...")
            self.client.delete_collection(self.collection_name)
        self.ensure_collection(dimension=dimension)

    def get_collection_info(self) -> dict[str, Any]:
        """Returns metadata and count of vectors in the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            points_count = getattr(info, "points_count", 0) or 0
            vectors_count = getattr(info, "indexed_vectors_count", points_count) or points_count
            return {
                "collection_name": self.collection_name,
                "status": str(info.status),
                "points_count": points_count,
                "vectors_count": vectors_count
            }
        except Exception as e:
            logger.warning(f"Error fetching collection info: {e}")
            return {
                "collection_name": self.collection_name,
                "status": "NOT_FOUND",
                "points_count": 0,
                "vectors_count": 0
            }

    def upsert_records(
        self,
        records: list[dict[str, Any]],
        vectors: list[list[float]]
    ) -> int:
        """Upserts standards records and their dense vector embeddings into Qdrant."""
        if len(records) != len(vectors):
            raise ValueError("Record count must equal vector count")

        points = []
        for idx, (record, vector) in enumerate(zip(records, vectors)):
            point_id = record.get("id") or (idx + 1)
            scope = record.get("scope", "")
            scope_snippet = scope[:280] + "..." if len(scope) > 280 else scope

            payload = {
                "db_id": record.get("id"),
                "standard_number": record.get("standard_number"),
                "title": record.get("title"),
                "category": record.get("category"),
                "department": record.get("department"),
                "year_of_publication": record.get("year_of_publication"),
                "edition": record.get("edition"),
                "status": record.get("status", "ACTIVE"),
                "source_url": record.get("source_url"),
                "source_evidence_note": record.get("source_evidence_note"),
                "scope_snippet": scope_snippet,
                "scope": scope,
                "keywords": record.get("keywords") or []
            }

            points.append(
                qmodels.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Upserted {len(points)} points into collection '{self.collection_name}'.")
        return len(points)

    def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        score_threshold: float = 0.0
    ) -> list[dict[str, Any]]:
        """Performs cosine similarity vector search on bis_standards."""
        # Use query_points (modern Qdrant client method) or fallback to search
        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold if score_threshold > 0 else None,
                with_payload=True
            ).points
        except Exception:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold if score_threshold > 0 else None,
                with_payload=True
            )

        matched = []
        for point in results:
            payload = point.payload or {}
            matched.append({
                "id": point.id,
                "score": float(point.score),
                "payload": payload
            })
        return matched

_vector_store_instance: QdrantVectorStore | None = None

def get_vector_store() -> QdrantVectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = QdrantVectorStore()
    return _vector_store_instance
