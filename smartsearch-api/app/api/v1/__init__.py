"""
Main API router that includes all version 1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1 import auth, products, stores, search, ingest, shopify_auth, webhooks, upload, widget, analytics

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="", tags=["authentication"])
api_router.include_router(stores.router, prefix="", tags=["stores"])
api_router.include_router(products.router, prefix="", tags=["products"])
api_router.include_router(search.router, prefix="", tags=["search"])
api_router.include_router(ingest.router, prefix="", tags=["ingest"])
api_router.include_router(shopify_auth.router, prefix="", tags=["shopify_auth"])
api_router.include_router(webhooks.router, prefix="", tags=["webhooks"])
api_router.include_router(upload.router, prefix="", tags=["upload"])
api_router.include_router(widget.router, prefix="", tags=["widget"])
api_router.include_router(analytics.router, prefix="", tags=["analytics"])

# Health check endpoint
@api_router.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "smartsearch-api"}