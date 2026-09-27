import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base backend directory
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

# Robust workspace directory resolution:
# 1. Respect explicit WORKSPACE_DIR environment variable if set.
# 2. If BACKEND_DIR.parent / "data" exists, workspace is the repo root.
# 3. If BACKEND_DIR / "data" exists, workspace is BACKEND_DIR.
# 4. Fallback to BACKEND_DIR.parent.
_env_workspace = os.getenv("WORKSPACE_DIR")
if _env_workspace:
    WORKSPACE_DIR = Path(_env_workspace).resolve()
elif (BACKEND_DIR.parent / "data").exists():
    WORKSPACE_DIR = BACKEND_DIR.parent
elif (BACKEND_DIR / "data").exists():
    WORKSPACE_DIR = BACKEND_DIR
else:
    WORKSPACE_DIR = BACKEND_DIR.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Settings
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # API Settings
    PROJECT_NAME: str = "SIH26108 BIS Standards Recommendation Engine"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # CORS Settings
    # Comma-separated list of allowed origins (e.g. "https://example.com,http://localhost:5173"), or "*"
    FRONTEND_ORIGIN: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = False

    # SQLite Database
    SQLITE_DB_PATH: Path = WORKSPACE_DIR / "data" / "db" / "standards.db"
    SEED_DATA_PATH: Path = WORKSPACE_DIR / "data" / "raw" / "bis_seed_standards.json"
    SEED_RELATIONSHIPS_PATH: Path = WORKSPACE_DIR / "data" / "raw" / "bis_seed_relationships.json"
    SEED_LIFECYCLE_PATH: Path = WORKSPACE_DIR / "data" / "raw" / "bis_seed_lifecycle.json"
    SEED_COMPLIANCE_PATH: Path = WORKSPACE_DIR / "data" / "raw" / "bis_seed_compliance.json"

    # Search Settings
    DEFAULT_SEARCH_LIMIT: int = 10
    MAX_SEARCH_LIMIT: int = 50
    DEFAULT_SCORE_THRESHOLD: float = 0.38

    # Qdrant Vector DB Settings
    # If QDRANT_URL is not set, QdrantClient uses local embedded disk storage
    QDRANT_URL: str | None = None
    QDRANT_STORAGE_PATH: Path = WORKSPACE_DIR / "data" / "qdrant_storage"
    QDRANT_COLLECTION_NAME: str = "bis_standards"

    # Embedding Model Settings (Local, 0 API keys)
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384

    # Document Ingestion Settings (Run 6A)
    MAX_DOCUMENT_SIZE_MB: int = 20
    DOCUMENT_STORAGE_PATH: Path = WORKSPACE_DIR / "data" / "documents"

    # Requirement Extraction Settings (Run 6B)
    # Provider: "gemini" for production, "mock" for tests / offline use
    EXTRACTION_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str | None = None
    GEMINI_REQUIREMENT_MODEL: str = "gemini-2.0-flash"
    # Maximum words per extraction chunk (larger docs are split at this boundary)
    REQUIREMENT_MAX_CHUNK_WORDS: int = 3000

    # Sarvam AI Translation Settings (Feature 2)
    SARVAM_API_KEY: str | None = None
    SARVAM_TRANSLATE_MODEL: str = "sarvam-translate:v1"
    SARVAM_TRANSLATE_URL: str = "https://api.sarvam.ai/translate"
    SARVAM_REQUEST_TIMEOUT_SECONDS: float = 10.0

settings = Settings()
