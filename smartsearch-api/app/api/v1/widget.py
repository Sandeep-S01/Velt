"""
API routes for the public JS Widget embedded in merchant storefronts.
These endpoints are public and CORS-enabled by default.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.models.database import Store, Product, SearchQueryLog
from app.core.search_engine import SemanticSearchEngine

router = APIRouter(prefix="/widget", tags=["widget"])

# Schema definitions
class WidgetSearchRequest(BaseModel):
    store_id: str
    query: str
    limit: Optional[int] = 5

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

@router.get("/config/{store_id}")
def get_widget_config(store_id: str, db: Session = Depends(get_db)):
    """
    Get the public widget configuration for a store.
    """
    store = db.query(Store).filter(Store.id == store_id, Store.is_active == True).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found or inactive"
        )
        
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
    config = store.widget_config or default_config
    return config

@router.post("/search", response_model=List[WidgetSearchCard])
def widget_search(
    request_data: WidgetSearchRequest,
    response: Response,
    db: Session = Depends(get_db),
    se: SemanticSearchEngine = Depends(get_search_engine)
):
    """
    Public semantic search endpoint optimized for the drop-in JS widget.
    Outputs simplified product fields and logs search queries for conversion analytics.
    """
    store_id = request_data.store_id
    query = request_data.query
    limit = request_data.limit or 5

    # Verify store is active
    store = db.query(Store).filter(Store.id == store_id, Store.is_active == True).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found or inactive"
        )

    # Perform vector search
    try:
        raw_results = se.search_store(store_id=store_id, query=query, n_results=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )

    formatted_results = []
    
    # Convert search results to public widget card schema
    for res in raw_results:
        # Load details from metadata stored in ChromaDB or fallback to PostgreSQL
        meta = res.get("metadata") or {}
        
        # Load from Postgres to ensure values are correct and fully up-to-date
        prod = db.query(Product).filter(Product.store_id == store_id, Product.id == res["id"]).first()
        if prod:
            formatted_results.append(WidgetSearchCard(
                id=prod.id,
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
        clicked_product_id=None
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    response.headers["X-Query-Log-ID"] = str(log.id)
    response.headers["Access-Control-Expose-Headers"] = "X-Query-Log-ID"

    return formatted_results

@router.get("/autocomplete")
def widget_autocomplete(
    store_id: str = Query(..., description="Store ID"),
    query: str = Query(..., description="The query prefix to search"),
    db: Session = Depends(get_db)
):
    """
    Public autocomplete suggestion endpoint matching product titles in the store.
    """
    # Verify store is active
    store = db.query(Store).filter(Store.id == store_id, Store.is_active == True).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found or inactive"
        )

    # Prefix match on product titles
    results = db.query(Product.title).filter(
        Product.store_id == store_id,
        Product.title.ilike(f"%{query}%"),
        Product.is_active == True
    ).limit(5).all()

    suggestions = [r[0] for r in results]
    return {"suggestions": suggestions}
