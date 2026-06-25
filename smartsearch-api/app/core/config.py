"""
Application configuration.
"""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import List, Union
import os

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "SmartSearch API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate limiting
    RATE_LIMIT_DEFAULT: int = int(os.getenv("RATE_LIMIT_DEFAULT", "100"))
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # Configure for production

    # Database (URL is handled separately in database.py)
    # These are defined as class attributes to allow env var loading but are not used in settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://smartsearch:smartsearch_pass@localhost:5433/smartsearch")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    # Shopify Integration Settings
    SHOPIFY_CLIENT_ID: str = os.getenv("SHOPIFY_CLIENT_ID", "mock_shopify_client_id")
    SHOPIFY_CLIENT_SECRET: str = os.getenv("SHOPIFY_CLIENT_SECRET", "mock_shopify_client_secret")
    SHOPIFY_REDIRECT_URI: str = os.getenv("SHOPIFY_REDIRECT_URI", "http://localhost:8000/api/v1/shopify/callback")
    SHOPIFY_SCOPES: str = os.getenv("SHOPIFY_SCOPES", "read_products,read_inventory")

    # MinIO / S3 Storage Settings
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_USE_SSL: bool = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "smartsearch-uploads")


    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra environment variables not defined in the model
    )

settings = Settings()