import secrets
from typing import List, Optional, Union

from pydantic import field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Server
    SERVER_NAME: str = "PageIQ"
    SERVER_HOST: str = "https://pageiq.pompora.dev"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "https://pageiq.pompora.dev",
        "https://www.pageiq.com",
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vue dev server
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return v

    # Database
    # Default to SQLite for dev/test so the project runs without Postgres.
    # Production deployments should set this to Postgres (e.g. postgresql+psycopg://...).
    DATABASE_URL: str = "sqlite+pysqlite:///./pageiq.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Security
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_IDS: dict = {
        "free": None,
        "basic": "price_basic",
        "pro": "price_pro",
        "business": "price_business",
        "enterprise": "price_enterprise",
    }

    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "pageiq-screenshots"

    # Cloudflare
    CLOUDFLARE_API_TOKEN: Optional[str] = None
    CLOUDFLARE_ZONE_ID: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # Cache
    CACHE_TTL_SECONDS: int = 86400  # 24 hours

    # Screenshots
    SCREENSHOTS_DIR: str = "data/screenshots"
    SCREENSHOTS_URL_PREFIX: str = "/screenshots"

    # Batch processing
    BATCH_STATUS_TTL_SECONDS: int = 60 * 60 * 24  # 24 hours

    # Free tier
    FREE_TIER_REQUESTS_PER_MONTH: int = 100
    FREE_TIER_SLOW_QUEUE: bool = True

    # Debug
    DEBUG: bool = False

    # Project
    PROJECT_NAME: str = "PageIQ"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Trusted hosts
    ALLOWED_HOSTS: List[str] = [
        "pageiq.pompora.dev",
        "localhost",
        "127.0.0.1",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )

    # Computed properties
    @property
    def database_echo(self) -> bool:
        """Enable SQL query logging in development"""
        return self.DEBUG

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return not self.DEBUG

    @property
    def allowed_origins(self) -> List[str]:
        """Get allowed CORS origins as strings"""
        return [str(origin) for origin in self.BACKEND_CORS_ORIGINS]


settings = Settings()