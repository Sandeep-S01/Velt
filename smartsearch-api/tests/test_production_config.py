import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_unsafe_defaults():
    with pytest.raises(ValidationError, match="Unsafe production settings"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="short",
            BACKEND_CORS_ORIGINS=["*"],
            ALLOWED_HOSTS=["*"],
        )


def test_production_accepts_explicit_secure_dependencies():
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a-secure-production-secret-with-32-bytes",
        SHOPIFY_CLIENT_SECRET="shopify-secret",
        SHOPIFY_ENCRYPTION_KEY="independent-fernet-key",
        DATABASE_URL="postgresql://user:password@db/velt",
        REDIS_URL="rediss://cache/0",
        BACKEND_CORS_ORIGINS=["https://dashboard.example.com"],
        ALLOWED_HOSTS=["api.example.com"],
        ALLOW_LOCAL_STORAGE_FALLBACK=False,
        MINIO_USE_SSL=True,
        ENABLE_DOCS=False,
        PUBLIC_API_BASE_URL="https://api.example.com",
    )

    assert settings.is_production
