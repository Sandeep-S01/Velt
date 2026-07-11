"""
Validate a production-like environment file before deploying.

Usage:
    python scripts/preflight_production_env.py --env-file .env.production
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

PLACEHOLDER_MARKERS = (
    "change-me",
    "example.com",
    "mock_",
    "replace-",
    "your-secret",
)

REQUIRED_KEYS = {
    "ENVIRONMENT",
    "SECRET_KEY",
    "SHOPIFY_CLIENT_ID",
    "SHOPIFY_CLIENT_SECRET",
    "SHOPIFY_ENCRYPTION_KEY",
    "PUBLIC_API_BASE_URL",
    "DATABASE_URL",
    "REDIS_URL",
    "BACKEND_CORS_ORIGINS",
    "ALLOWED_HOSTS",
    "ENABLE_DOCS",
    "MINIO_ENDPOINT",
    "MINIO_ACCESS_KEY",
    "MINIO_SECRET_KEY",
    "MINIO_USE_SSL",
    "ALLOW_LOCAL_STORAGE_FALLBACK",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", required=True, help="Path to the env file to validate")
    args = parser.parse_args()

    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"Missing env file: {env_path}", file=sys.stderr)
        return 1

    values = parse_env_file(env_path)
    errors = validate_values(values)
    if errors:
        print("Preflight failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Preflight passed: production-like environment is deployable.")
    return 0


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            values[f"__invalid_line_{line_number}"] = raw_line
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def validate_values(values: dict[str, str]) -> list[str]:
    errors: list[str] = []

    invalid_lines = sorted(key for key in values if key.startswith("__invalid_line_"))
    errors.extend(f"Invalid env syntax at {key.removeprefix('__invalid_line_')}" for key in invalid_lines)

    missing = sorted(key for key in REQUIRED_KEYS if not values.get(key))
    errors.extend(f"Missing required value: {key}" for key in missing)

    for key, value in values.items():
        lowered = value.lower()
        if any(marker in lowered for marker in PLACEHOLDER_MARKERS):
            errors.append(f"{key} still contains a placeholder value")

    if values.get("ENVIRONMENT", "").lower() != "production":
        errors.append("ENVIRONMENT must be production for staging/prod deploy checks")

    if len(values.get("SECRET_KEY", "")) < 32:
        errors.append("SECRET_KEY must be at least 32 characters")

    if values.get("ENABLE_DOCS", "").lower() != "false":
        errors.append("ENABLE_DOCS must be false")

    if values.get("ALLOW_LOCAL_STORAGE_FALLBACK", "").lower() != "false":
        errors.append("ALLOW_LOCAL_STORAGE_FALLBACK must be false")

    if values.get("MINIO_USE_SSL", "").lower() != "true":
        errors.append("MINIO_USE_SSL must be true")

    public_api_base_url = values.get("PUBLIC_API_BASE_URL", "")
    if not public_api_base_url.startswith("https://"):
        errors.append("PUBLIC_API_BASE_URL must use https://")

    redis_url = values.get("REDIS_URL", "")
    if not redis_url.startswith("rediss://"):
        errors.append("REDIS_URL must use rediss://")

    database_url = values.get("DATABASE_URL", "")
    if not database_url.startswith(("postgresql://", "postgresql+psycopg2://")):
        errors.append("DATABASE_URL must use PostgreSQL")

    for key in ("PUBLIC_API_BASE_URL", "DATABASE_URL", "REDIS_URL"):
        if values.get(key) and not urlparse(values[key]).scheme:
            errors.append(f"{key} is not a valid URL")

    for key in ("BACKEND_CORS_ORIGINS", "ALLOWED_HOSTS"):
        value = values.get(key, "")
        if "*" in value:
            errors.append(f"{key} must not contain wildcard origins/hosts")
        if "localhost" in value or "127.0.0.1" in value:
            errors.append(f"{key} must not contain local development hosts")

    os.environ.update(values)
    try:
        from cryptography.fernet import Fernet

        Fernet(values.get("SHOPIFY_ENCRYPTION_KEY", "").encode("utf-8"))
    except Exception:
        errors.append("SHOPIFY_ENCRYPTION_KEY must be a valid Fernet key")

    return errors


if __name__ == "__main__":
    raise SystemExit(main())
