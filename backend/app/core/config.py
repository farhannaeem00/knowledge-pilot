"""
Centralized application configuration, loaded from environment variables.
Every other module imports `settings` from here — nothing is hardcoded
elsewhere in the codebase.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "KnowledgePilot AI"
    APP_ENV: Literal["local", "staging", "production"] = "local"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    JWT_SECRET_KEY: str = Field(..., description="Signs JWTs. MUST be overridden outside local.")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    POSTGRES_USER: str = "knowledgepilot"
    POSTGRES_PASSWORD: str = "knowledgepilot"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "knowledgepilot"
    DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str | None, info):
        if v:
            return v
        d = info.data
        return (
            f"postgresql+asyncpg://{d.get('POSTGRES_USER')}:{d.get('POSTGRES_PASSWORD')}"
            f"@{d.get('POSTGRES_HOST')}:{d.get('POSTGRES_PORT')}/{d.get('POSTGRES_DB')}"
        )

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: str | None = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: str | None, info):
        if v:
            return v
        d = info.data
        return f"redis://{d.get('REDIS_HOST')}:{d.get('REDIS_PORT')}/0"

    # PRODUCTION TODO: replace with the real deployed frontend origin(s)
    # before going live - this wildcard-free localhost default is safe for
    # dev but must never be the value in a production .env.
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    DEFAULT_AI_PROVIDER: Literal["openai", "anthropic", "gemini", "azure_openai", "ollama"] = "openai"
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    AZURE_OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_ENDPOINT: str | None = None
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    GROQ_API_KEY: str | None = None

    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_UPLOAD_EXTENSIONS: list[str] = ["pdf", "docx", "txt", "md"]

    STORAGE_BACKEND: Literal["s3", "supabase", "local"] = "local"
    LOCAL_STORAGE_PATH: str = "/app/storage"
    S3_BUCKET_NAME: str | None = None
    S3_REGION: str | None = None
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
