"""Validation helpers for production service connection URLs."""

from __future__ import annotations

import re
from urllib.parse import urlparse

RENDER_PRIVATE_KEY_VALUE_HOST = re.compile(r"^red-[a-z0-9-]+$")


def is_secure_redis_url(value: str) -> bool:
    """Accept TLS Redis or Render's documented private-network URL format."""
    parsed = urlparse(value)
    if not parsed.hostname:
        return False
    if parsed.scheme == "rediss":
        return True
    return parsed.scheme == "redis" and bool(
        RENDER_PRIVATE_KEY_VALUE_HOST.fullmatch(parsed.hostname.lower())
    )
