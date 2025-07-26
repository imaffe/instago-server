from typing import Any, List, Optional

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Instago Server"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    SUPABASE_URL: str
    SUPABASE_PROJECT_ID: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_JWT_SECRET: str

    DATABASE_URL: str

    GCS_BUCKET_NAME: str
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_TOKEN: str
    MILVUS_COLLECTION_NAME: str = "screenshots"

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_DIM: int = 1536

    # OpenRouter Configuration
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "qwen/qwen-vl-max"
    OPENROUTER_SITE_URL: Optional[str] = "https://instago.app"
    OPENROUTER_SITE_NAME: Optional[str] = "Instago"

    # Google Vertex AI Configuration
    VERTEX_AI_PROJECT: Optional[str] = None
    VERTEX_AI_LOCATION: str = "us-central1"
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"

    # Agent selection - "openai", "gemini", or "openrouter"
    AGENT_NAME: str = "openai"

    BACKEND_CORS_ORIGINS: Optional[List[AnyHttpUrl]] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


settings = Settings()
