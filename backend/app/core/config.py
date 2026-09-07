from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base workspace directory (one level up from backend)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_DIR = BACKEND_DIR.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API Settings
    PROJECT_NAME: str = "SIH26108 BIS Standards Recommendation Engine"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # SQLite Database
    SQLITE_DB_PATH: Path = WORKSPACE_DIR / "data" / "db" / "standards.db"
    SEED_DATA_PATH: Path = WORKSPACE_DIR / "data" / "raw" / "bis_seed_standards.json"

    # Search Settings
    DEFAULT_SEARCH_LIMIT: int = 10
    MAX_SEARCH_LIMIT: int = 50

    # Qdrant Vector DB Settings
    # If QDRANT_URL is not set, QdrantClient uses local embedded disk storage
    QDRANT_URL: str | None = None
    QDRANT_STORAGE_PATH: Path = WORKSPACE_DIR / "data" / "qdrant_storage"
    QDRANT_COLLECTION_NAME: str = "bis_standards"

    # Embedding Model Settings (Local, 0 API keys)
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIMENSION: int = 384

settings = Settings()
