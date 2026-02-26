"""
Mining AI Platform - Application Configuration.

All settings are loaded from environment variables via pydantic-settings.
Use get_settings() everywhere to access config (cached singleton).
"""

from functools import lru_cache
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Environment ---
    ENVIRONMENT: str = "development"

    # --- PostgreSQL ---
    DATABASE_URL: str = (
        "postgresql+asyncpg://mining_user:mining_pass@localhost:5432/mining_ai"
    )
    DATABASE_URL_SYNC: str = (
        "postgresql+psycopg2://mining_user:mining_pass@localhost:5432/mining_ai"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # --- Redis ---
    REDIS_URL: str = "redis://:redis_pass@localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://:redis_pass@localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://:redis_pass@localhost:6379/1"

    # --- ChromaDB ---
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_API_KEY: Optional[str] = None
    CHROMA_COLLECTION_DOCUMENTS: str = "mining_documents"
    CHROMA_COLLECTION_RESEARCH: str = "mining_research"

    # --- Security ---
    SECRET_KEY: str = "changeme-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # --- AI Providers ---
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-opus-4-6"

    # --- Embedding ---
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    # --- Document Processing ---
    MAX_UPLOAD_SIZE_MB: int = 50

    # --- Feature Flags ---
    ENABLE_RESEARCH_AGENT: bool = True
    ENABLE_DOCUMENT_PROCESSING: bool = True
    ENABLE_PROTOTYPE_GENERATOR: bool = True

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings singleton. Import and call this everywhere."""
    return Settings()
