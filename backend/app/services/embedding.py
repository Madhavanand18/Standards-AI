from abc import ABC, abstractmethod
import logging
from typing import Sequence
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

class BaseEmbeddingService(ABC):
    """Abstract interface for embedding generation."""

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generates an embedding vector for a single string."""
        pass

    @abstractmethod
    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Generates embedding vectors for a batch of strings."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the embedding vector dimension."""
        pass


class FastEmbedService(BaseEmbeddingService):
    """
    Local multilingual embedding service powered by FastEmbed (ONNX Runtime).
    100% free, runs locally on CPU without external API keys or cloud dependencies.
    """

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self._model = None
        self._dimension = settings.EMBEDDING_DIMENSION

    def _get_model(self):
        if self._model is None:
            logger.info(f"Loading local embedding model: {self.model_name}...")
            try:
                from fastembed import TextEmbedding
                self._model = TextEmbedding(model_name=self.model_name)
                logger.info(f"Model {self.model_name} loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load embedding model {self.model_name}: {e}")
                # Fallback to standard fastembed default model if specific name fails
                logger.info("Attempting fallback to BAAI/bge-small-en-v1.5...")
                from fastembed import TextEmbedding
                self._model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
                self.model_name = "BAAI/bge-small-en-v1.5"
                self._dimension = 384
        return self._model

    def embed_text(self, text: str) -> list[float]:
        model = self._get_model()
        cleaned_text = text.strip() if text else ""
        embeddings = list(model.embed([cleaned_text]))
        vec = embeddings[0]
        if isinstance(vec, np.ndarray):
            return vec.tolist()
        return list(vec)

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self._get_model()
        cleaned = [t.strip() if t else "" for t in texts]
        embeddings = list(model.embed(cleaned))
        results = []
        for vec in embeddings:
            if isinstance(vec, np.ndarray):
                results.append(vec.tolist())
            else:
                results.append(list(vec))
        return results

    @property
    def dimension(self) -> int:
        return self._dimension


# Global singleton instance
_embedding_service_instance: BaseEmbeddingService | None = None

def get_embedding_service() -> BaseEmbeddingService:
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = FastEmbedService()
    return _embedding_service_instance
