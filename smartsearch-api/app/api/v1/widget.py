"""
API routes for the public JS Widget embedded in merchant storefronts.
These endpoints are public and CORS-enabled by default.
"""

import re
import time

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from app.core.database import get_db
from app.models.database import Store, Product, SearchQueryLog
from app.core.search_engine import SemanticSearchEngine

router = APIRouter(prefix="/widget", tags=["widget"])

# Schema definitions
class WidgetSearchRequest(BaseModel):
    store_id: str = Field(..., min_length=1, max_length=100)
    query: str = Field(..., min_length=1, max_length=200)
    limit: int = Field(default=5, ge=1, le=20)

class WidgetSearchCard(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    score: float

def get_search_engine(request: Request) -> SemanticSearchEngine:
    """Dependency to retrieve search engine singleton."""
    return request.app.state.search_engine


def get_public_store(
    store_id: str,
    widget_token: str,
    db: Session,
    origin: str | None = None,
) -> Store:
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.widget_token == widget_token,
        Store.is_active == True,
    ).first()
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    allowed_origins = store.widget_allowed_origins or []
    if allowed_origins and origin not in allowed_origins:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Origin not allowed")
    return store

@router.get("/config/{store_id}")
def get_widget_config(
    store_id: str,
    x_widget_token: str = Header(..., alias="X-Widget-Token"),
    origin: str | None = Header(None),
    db: Session = Depends(get_db),
):
    """
    Get the public widget configuration for a store.
    """
    store = get_public_store(store_id, x_widget_token, db, origin)
        
    # Return default widget config if not customized
    default_config = {
        "theme": "light",
        "primary_color": "#4F46E5",
        "position": "bottom-right",
        "placeholder_text": "Search for products...",
        "show_filters": True,
        "show_price": True,
        "show_rating": True,
        "enable_autocomplete": True
    }
    
    # Store.widget_config is stored as JSONB in Postgres, or dict in SQLAlchemy
    stored = store.widget_config or {}
    primary_color = stored.get("primary_color", default_config["primary_color"])
    if not isinstance(primary_color, str) or not re.fullmatch(
        r"#[0-9a-fA-F]{6}", primary_color
    ):
        primary_color = default_config["primary_color"]
    placeholder = stored.get("placeholder_text", default_config["placeholder_text"])
    if not isinstance(placeholder, str):
        placeholder = default_config["placeholder_text"]

    return {
        "theme": stored.get("theme") if stored.get("theme") in {"light", "dark"} else "light",
        "primary_color": primary_color,
        "position": stored.get("position")
        if stored.get("position") in {"bottom-left", "bottom-right"}
        else "bottom-right",
        "placeholder_text": placeholder[:100],
        "show_filters": bool(stored.get("show_filters", True)),
        "show_price": bool(stored.get("show_price", True)),
        "show_rating": bool(stored.get("show_rating", True)),
        "enable_autocomplete": bool(stored.get("enable_autocomplete", True)),
    }

@router.post("/search", response_model=List[WidgetSearchCard])
def widget_search(
    request_data: WidgetSearchRequest,
    response: Response,
    x_widget_token: str = Header(..., alias="X-Widget-Token"),
    origin: str | None = Header(None),
    db: Session = Depends(get_db),
    se: SemanticSearchEngine = Depends(get_search_engine)
):
    """
    Public semantic search endpoint optimized for the drop-in JS widget.
    Outputs simplified product fields and logs search queries for conversion analytics.
    """
    store_id = request_data.store_id
    query = request_data.query
    limit = request_data.limit

    # Verify store is active
    store = get_public_store(store_id, x_widget_token, db, origin)

    # Perform vector search
    threshold = float((store.search_config or {}).get("min_score_threshold", 0.25))
    threshold = max(0.0, min(1.0, threshold))
    started_at = time.perf_counter()
    try:
        raw_results = se.search_store(
            store_id=store_id,
            query=query,
            n_results=limit,
            min_score=threshold,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Semantic search failed"
        )

    formatted_results = []
    
    # Convert search results to public widget card schema
    for res in raw_results:
        # Load details from metadata stored in ChromaDB or fallback to PostgreSQL
        meta = res.get("metadata") or {}
        
        # Load from Postgres to ensure values are correct and fully up-to-date
        prod = db.query(Product).filter(
            Product.store_id == store_id,
            Product.external_id == res["id"],
            Product.is_active == True,
        ).first()
        if prod:
            formatted_results.append(WidgetSearchCard(
                id=prod.external_id,
                title=prod.title,
                description=prod.description,
                price=float(prod.price) if prod.price is not None else None,
                image_url=prod.image_url,
                product_url=prod.product_url,
                score=res["score"]
            ))
        else:
            # Fallback to metadata in ChromaDB if not found in Postgres
            formatted_results.append(WidgetSearchCard(
                id=res["id"],
                title=meta.get("title", ""),
                description=res.get("description"),
                price=meta.get("price"),
                image_url=meta.get("image_url"),
                product_url=meta.get("product_url"),
                score=res["score"]
            ))

    # Log search query to PostgreSQL for dashboard analytics
    log = SearchQueryLog(
        store_id=store_id,
        query=query,
        results_count=len(formatted_results),
        result_product_ids=[result.id for result in formatted_results],
        duration_ms=round((time.perf_counter() - started_at) * 1000, 2),
        clicked_product_id=None
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    response.headers["X-Query-Event-Token"] = log.event_token
    response.headers["Access-Control-Expose-Headers"] = "X-Query-Event-Token"

    return formatted_results

@router.get("/autocomplete")
def widget_autocomplete(
    store_id: str = Query(..., min_length=1, max_length=100, description="Store ID"),
    query: str = Query(..., min_length=1, max_length=100, description="The query prefix to search"),
    x_widget_token: str = Header(..., alias="X-Widget-Token"),
    origin: str | None = Header(None),
    db: Session = Depends(get_db)
):
    """
    Public autocomplete suggestion endpoint matching product titles in the store.
    """
    # Verify store is active
    get_public_store(store_id, x_widget_token, db, origin)

    # Prefix match on product titles
    results = db.query(Product.title).filter(
        Product.store_id == store_id,
        Product.title.ilike(f"%{query}%"),
        Product.is_active == True
    ).limit(5).all()

    suggestions = [r[0] for r in results]
    return {"suggestions": suggestions}
