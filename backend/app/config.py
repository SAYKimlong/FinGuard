"""FinGuard configuration — loads from the project-root .env file."""

import json
from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://finguard:finguard@localhost:5555/finguard"
    DATABASE_URL_SYNC: str = "postgresql+psycopg://finguard:finguard@localhost:5555/finguard"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3.1:8b"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    UPLOAD_DIR: str = "./storage/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    CORS_ORIGINS: str = "http://localhost:3000"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    @model_validator(mode="after")
    def validate_production_security(self):
        """Fail closed when production is configured with development defaults."""
        if self.APP_ENV.strip().lower() not in {"production", "prod"}:
            return self

        if (
            self.SECRET_KEY == "change-me-to-a-random-secret-key"
            or len(self.SECRET_KEY) < 32
        ):
            raise ValueError(
                "Production requires SECRET_KEY to be a unique random value "
                "of at least 32 characters."
            )

        if self.DEBUG:
            raise ValueError("DEBUG must be false when APP_ENV is production.")

        database_urls = (self.DATABASE_URL, self.DATABASE_URL_SYNC)
        unsafe_database_markers = ("finguard:finguard@", "finguard_secret")
        if any(
            marker in url
            for url in database_urls
            for marker in unsafe_database_markers
        ):
            raise ValueError(
                "Production database URLs must not use repository development credentials."
            )

        return self

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from string or JSON."""
        val = self.CORS_ORIGINS
        if val.startswith("["):
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                pass
        return [origin.strip() for origin in val.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    model_config = {
        "env_file": "../.env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
