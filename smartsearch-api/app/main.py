"""
Main FastAPI application for SmartSearch API.
"""

import time
import logging
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.core.database import create_tables, get_redis
from app.core.config import settings
from app.core.middleware import RateLimitMiddleware
from app.core.observability import REQUEST_COUNT, REQUEST_LATENCY, configure_logging
from app.api.v1 import api_router

# Configure logging
configure_logging(settings.ENVIRONMENT)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    logger.info("Starting up SmartSearch API...")
    if not settings.is_production:
        create_tables()
        logger.info("Development database tables created/verified")

    # Initialize Redis connection
    redis_client = get_redis()
    if redis_client:
        try:
            redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            if settings.is_production:
                raise RuntimeError("Redis is required in production") from e
            logger.warning("Redis unavailable during development startup")

    # Initialize ChromaDB persistent client path if ensured
    chroma_path = settings.CHROMA_DB_PATH

    # Initialize search engine singleton
    from app.core.search_engine import SemanticSearchEngine
    app.state.search_engine = SemanticSearchEngine(db_path=chroma_path)
    logger.info("Semantic Search Engine singleton initialized")

    yield

    # Shutdown
    logger.info("Shutting down SmartSearch API...")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Semantic search for e-commerce products",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENABLE_DOCS else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.ENABLE_DOCS else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.ENABLE_DOCS else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    logger.exception("Unhandled request error trace_id=%s", trace_id)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "trace_id": trace_id},
    )

# Request processing time middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request.state.trace_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request.state.trace_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    route = request.scope.get("route")
    route_path = getattr(route, "path", "unmatched")
    REQUEST_COUNT.labels(request.method, route_path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.method, route_path).observe(process_time)
    return response

@app.get("/health/live", tags=["health"])
async def liveness_check():
    return {"status": "healthy", "service": "smartsearch-api", "version": settings.VERSION}


@app.get("/health/ready", tags=["health"])
async def readiness_check():
    # Check database connection
    try:
        from app.core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        db_status = "unhealthy"

    # Check Redis connection
    redis_client = get_redis()
    if redis_client:
        try:
            redis_client.ping()
            redis_status = "healthy"
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            redis_status = "unhealthy"
    else:
        redis_status = "not configured"

    try:
        search_engine = getattr(app.state, "search_engine", None)
        if search_engine is None:
            chroma_status = "unhealthy"
        else:
            search_engine.client.heartbeat()
            chroma_status = "healthy"
    except Exception as e:
        logger.warning(f"Chroma health check failed: {e}")
        chroma_status = "unhealthy"

    healthy = (
        db_status == "healthy"
        and redis_status == "healthy"
        and chroma_status == "healthy"
    )
    return JSONResponse(status_code=200 if healthy else 503, content={
        "status": "healthy" if healthy else "unhealthy",
        "service": "smartsearch-api",
        "version": settings.VERSION,
        "checks": {
            "database": db_status,
            "redis": redis_status,
            "chroma": chroma_status
        }
    })


@app.get("/health", tags=["health"])
async def health_check():
    return await readiness_check()


@app.get("/metrics", include_in_schema=False)
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Redirects for standard documentation paths
@app.get("/docs", include_in_schema=False)
async def docs_redirect():
    if not settings.ENABLE_DOCS:
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")

@app.get("/redoc", include_in_schema=False)
async def redoc_redirect():
    if not settings.ENABLE_DOCS:
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return RedirectResponse(url=f"{settings.API_V1_STR}/redoc")

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to SmartSearch API",
        "version": settings.VERSION,
        "docs": "/api/v1/docs"
    }
