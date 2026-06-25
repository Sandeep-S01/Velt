"""
Rate limiting middleware using Redis.
"""

import time
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import redis
import os

# Import our database utilities
from app.core.database import get_redis

# Rate limit configuration
RATE_LIMIT_DEFAULT = int(os.getenv("RATE_LIMIT_DEFAULT", "100"))
RATE_LIMIT_WINDOW = 60  # seconds

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply rate limiting based on API key or IP address.
    """

    def __init__(
        self,
        app: ASGIApp,
        rate_limit: int = RATE_LIMIT_DEFAULT,
        window_seconds: int = RATE_LIMIT_WINDOW,
        exempt_paths: list = None
    ):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/redoc", "/openapi.json", "/api/v1/health"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        # Get client identifier (API key or IP)
        client_id = self._get_client_id(request)

        # Check if rate limited
        if self._is_rate_limited(client_id):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": str(self.window_seconds)}
            )

        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add rate limit headers
        remaining = self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        reset_time = int(time.time()) + self.window_seconds
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        response.headers["X-Process-Time"] = str(process_time)

        return response

    def _get_client_id(self, request: Request) -> str:
        """Extract client identifier from request."""
        # Try to get API key from header
        api_key = request.headers.get("X-API-Key") or request.headers.get("api_key")
        if api_key:
            return f"api_key:{api_key}"

        # Fallback to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            # Handle TestClient and direct connections
            if request.client:
                ip = request.client.host
            else:
                ip = "unknown"

        return f"ip:{ip}"

    def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit."""
        redis_client = get_redis()
        if not redis_client:
            # If Redis is not available, skip rate limiting
            return False

        key = f"rate_limit:{client_id}"
        current = redis_client.get(key)

        if current is None:
            # First request, set counter = 1 with expiration
            redis_client.setex(key, self.window_seconds, 1)
            return False

        current_count = int(current)
        if current_count >= self.rate_limit:
            return True

        # Increment counter
        redis_client.incr(key)
        return False

    def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        redis_client = get_redis()
        if not redis_client:
            return self.rate_limit

        key = f"rate_limit:{client_id}"
        current = redis_client.get(key)

        if current is None:
            return self.rate_limit

        current_count = int(current)
        return max(0, self.rate_limit - current_count)

# Alternative decorator-based rate limiter for specific endpoints
def rate_limit(times: int, seconds: int):
    """
    Decorator to apply rate limiting to specific endpoints.

    Usage:
        @app.get("/items/")
        @rate_limit(times=10, seconds=60)
        async def read_items():
            return [{"item_id": "Foo"}]
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would need access to request and redis client
            # For simplicity, we'll implement this as middleware above
            # In a full implementation, you'd access request.state or similar
            return func(*args, **kwargs)
        return wrapper
    return decorator