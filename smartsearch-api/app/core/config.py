"""
Application configuration.
"""

from pydantic import ConfigDict, model_validator
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "SmartSearch API"
    VERSION: str = "1.0.0"
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    API_V1_STR: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ISSUER: str = "velt-api"
    JWT_AUDIENCE: str = "velt-dashboard"

    # Rate limiting
    RATE_LIMIT_DEFAULT: int = int(os.getenv("RATE_LIMIT_DEFAULT", "100"))
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # Configure for production
    ALLOWED_HOSTS: List[str] = ["*"]
    ENABLE_DOCS: bool = True
    TRUST_PROXY_HEADERS: bool = False

    # Database (URL is handled separately in database.py)
    # These are defined as class attributes to allow env var loading but are not used in settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://smartsearch:smartsearch_pass@localhost:5433/smartsearch")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    # Shopify Integration Settings
    SHOPIFY_CLIENT_ID: str = os.getenv("SHOPIFY_CLIENT_ID", "mock_shopify_client_id")
    SHOPIFY_CLIENT_SECRET: str = os.getenv("SHOPIFY_CLIENT_SECRET", "mock_shopify_client_secret")
    SHOPIFY_ENCRYPTION_KEY: str = os.getenv("SHOPIFY_ENCRYPTION_KEY", "")
    PUBLIC_API_BASE_URL: str = os.getenv("PUBLIC_API_BASE_URL", "http://localhost:8000")
    SHOPIFY_REDIRECT_URI: str = os.getenv("SHOPIFY_REDIRECT_URI", "")
    SHOPIFY_SCOPES: str = os.getenv("SHOPIFY_SCOPES", "read_products,read_inventory")
    SHOPIFY_API_VERSION: str = os.getenv("SHOPIFY_API_VERSION", "2026-04")

    @property
    def public_api_base_url(self) -> str:
        return self.PUBLIC_API_BASE_URL.rstrip("/")

    @property
    def shopify_redirect_uri(self) -> str:
        return self.SHOPIFY_REDIRECT_URI or f"{self.public_api_base_url}{self.API_V1_STR}/shopify/callback"

    # MinIO / S3 Storage Settings
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_USE_SSL: bool = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "smartsearch-uploads")
    ALLOW_LOCAL_STORAGE_FALLBACK: bool = os.getenv(
        "ALLOW_LOCAL_STORAGE_FALLBACK", "true"
    ).lower() == "true"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @model_validator(mode="after")
    def validate_production_settings(self):
        if not self.is_production:
            return self

        invalid = []
        if len(self.SECRET_KEY) < 32 or "change" in self.SECRET_KEY.lower():
            invalid.append("SECRET_KEY")
        if self.SHOPIFY_CLIENT_SECRET in {"", "mock_shopify_client_secret"}:
            invalid.append("SHOPIFY_CLIENT_SECRET")
        if not self.SHOPIFY_ENCRYPTION_KEY:
            invalid.append("SHOPIFY_ENCRYPTION_KEY")
        if not self.DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://")):
            invalid.append("DATABASE_URL")
        if not self.REDIS_URL.startswith("rediss://"):
            invalid.append("REDIS_URL (rediss:// required)")
        if "*" in self.BACKEND_CORS_ORIGINS or not self.BACKEND_CORS_ORIGINS:
            invalid.append("BACKEND_CORS_ORIGINS")
        if "*" in self.ALLOWED_HOSTS or not self.ALLOWED_HOSTS:
            invalid.append("ALLOWED_HOSTS")
        if self.ALLOW_LOCAL_STORAGE_FALLBACK:
            invalid.append("ALLOW_LOCAL_STORAGE_FALLBACK")
        if not self.MINIO_USE_SSL:
            invalid.append("MINIO_USE_SSL")
        if self.ENABLE_DOCS:
            invalid.append("ENABLE_DOCS")
        if not self.PUBLIC_API_BASE_URL.startswith("https://"):
            invalid.append("PUBLIC_API_BASE_URL")
        if invalid:
            raise ValueError("Unsafe production settings: " + ", ".join(invalid))
        return self


    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra environment variables not defined in the model
    )

settings = Settings()
