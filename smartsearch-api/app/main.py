"""
Main FastAPI application for SmartSearch API.
"""

import os
import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.database import create_tables, get_redis
from app.core.config import settings
from app.core.middleware import RateLimitMiddleware
from app.api.v1 import api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    logger.info("Starting up SmartSearch API...")
    create_tables()
    logger.info("Database tables created/verified")

    # Initialize Redis connection
    redis_client = get_redis()
    if redis_client:
        try:
            redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")

    # Initialize ChromaDB persistent client path if ensured
    chroma_path = os.path.join(os.path.dirname(__file__), "chroma_db")
    os.makedirs(chroma_path, exist_ok=True)
    logger.info(f"ChromaDB path ensured: {chroma_path}")

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
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
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

# Add trusted host middleware (for production)
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=settings.ALLOWED_HOSTS
# )

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Request processing time middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
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

    return {
        "status": "healthy",
        "service": "smartsearch-api",
        "version": settings.VERSION,
        "checks": {
            "database": db_status,
            "redis": redis_status
        }
    }

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to SmartSearch API",
        "version": settings.VERSION,
        "docs": "/api/v1/docs"
    }