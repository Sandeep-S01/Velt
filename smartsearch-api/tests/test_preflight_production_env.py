from cryptography.fernet import Fernet

from scripts.preflight_production_env import validate_values


def valid_production_values() -> dict[str, str]:
    return {
        "ENVIRONMENT": "production",
        "SECRET_KEY": "a-production-secret-with-at-least-32-characters",
        "BETA_INVITE_CODE": "a-private-beta-invite-code",
        "METRICS_TOKEN": "a-private-metrics-token-with-32-bytes",
        "SHOPIFY_CLIENT_ID": "shopify-client-id",
        "SHOPIFY_CLIENT_SECRET": "shopify-client-secret",
        "SHOPIFY_ENCRYPTION_KEY": Fernet.generate_key().decode(),
        "PUBLIC_API_BASE_URL": "https://api.staging.velt.test",
        "DASHBOARD_BASE_URL": "https://dashboard.staging.velt.test",
        "DATABASE_URL": "postgresql://velt:password@database.internal/velt",
        "REDIS_URL": "rediss://:password@redis.internal/0",
        "BACKEND_CORS_ORIGINS": '["https://dashboard.staging.velt.test"]',
        "ALLOWED_HOSTS": '["api.staging.velt.test"]',
        "ENABLE_DOCS": "false",
        "MINIO_ENDPOINT": "objects.internal:9000",
        "MINIO_ACCESS_KEY": "staging-access-key",
        "MINIO_SECRET_KEY": "staging-secret-key",
        "MINIO_USE_SSL": "true",
        "ALLOW_LOCAL_STORAGE_FALLBACK": "false",
    }


def test_preflight_accepts_complete_production_configuration():
    assert validate_values(valid_production_values()) == []


def test_preflight_requires_invite_and_https_dashboard():
    values = valid_production_values()
    values["BETA_INVITE_CODE"] = "short"
    values["DASHBOARD_BASE_URL"] = "http://dashboard.staging.velt.test"

    errors = validate_values(values)

    assert "BETA_INVITE_CODE must be at least 16 characters" in errors
    assert "DASHBOARD_BASE_URL must use https://" in errors


def test_preflight_requires_private_metrics_token():
    values = valid_production_values()
    values["METRICS_TOKEN"] = "short"

    errors = validate_values(values)

    assert "METRICS_TOKEN must be at least 32 characters" in errors
