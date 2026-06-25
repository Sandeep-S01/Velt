"""
API routes for store search analytics and click tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.models.database import SearchQueryLog, Product, Store
from app.utils.security import get_current_active_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Schema definitions
class SearchClickRequest(BaseModel):
    query_log_id: int
    clicked_product_id: str

class QueryStat(BaseModel):
    query: str
    count: int

class ClickedProductStat(BaseModel):
    product_id: str
    title: str
    click_count: int

class AnalyticsDashboardResponse(BaseModel):
    total_searches: int
    no_results_count: int
    click_through_rate: float
    top_queries: List[QueryStat]
    top_clicked_products: List[ClickedProductStat]

@router.post("/click")
def track_search_click(
    request_data: SearchClickRequest,
    db: Session = Depends(get_db)
):
    """
    Log a click event on a product search result card.
    Updates the query log entry to attribute the conversion.
    """
    query_log = db.query(SearchQueryLog).filter(SearchQueryLog.id == request_data.query_log_id).first()
    if not query_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search query log entry not found."
        )

    # Update clicked product ID
    query_log.clicked_product_id = request_data.clicked_product_id
    db.commit()

    return {
        "status": "success",
        "message": "Click tracked successfully.",
        "query_log_id": query_log.id,
        "clicked_product_id": query_log.clicked_product_id
    }

@router.get("/{store_id}", response_model=AnalyticsDashboardResponse)
def get_store_analytics(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Retrieve search performance and conversion analytics metrics for a store's merchant dashboard.
    Requires dashboard user authentication.
    """
    # Verify store exists
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found."
        )

    # 1. Total searches
    total_searches = db.query(SearchQueryLog).filter(SearchQueryLog.store_id == store_id).count()

    # 2. No results count
    no_results_count = db.query(SearchQueryLog).filter(
        SearchQueryLog.store_id == store_id,
        SearchQueryLog.results_count == 0
    ).count()

    # 3. Click-through rate (CTR) calculation
    clicked_searches = db.query(SearchQueryLog).filter(
        SearchQueryLog.store_id == store_id,
        SearchQueryLog.clicked_product_id.isnot(None)
    ).count()
    
    ctr = 0.0
    if total_searches > 0:
        ctr = round(float(clicked_searches) / float(total_searches), 4)

    # 4. Top Queries
    top_queries_raw = db.query(
        SearchQueryLog.query,
        func.count(SearchQueryLog.id).label("count")
    ).filter(
        SearchQueryLog.store_id == store_id
    ).group_by(
        SearchQueryLog.query
    ).order_by(
        func.count(SearchQueryLog.id).desc()
    ).limit(10).all()

    top_queries = [QueryStat(query=q[0], count=q[1]) for q in top_queries_raw]

    # 5. Top Clicked Products
    top_clicks_raw = db.query(
        SearchQueryLog.clicked_product_id,
        func.count(SearchQueryLog.id).label("count")
    ).filter(
        SearchQueryLog.store_id == store_id,
        SearchQueryLog.clicked_product_id.isnot(None)
    ).group_by(
        SearchQueryLog.clicked_product_id
    ).order_by(
        func.count(SearchQueryLog.id).desc()
    ).limit(10).all()

    top_clicked_products = []
    for item in top_clicks_raw:
        product_id, click_count = item[0], item[1]
        prod = db.query(Product).filter(Product.store_id == store_id, Product.id == product_id).first()
        title = prod.title if prod else "Unknown Product"
        top_clicked_products.append(ClickedProductStat(
            product_id=product_id,
            title=title,
            click_count=click_count
        ))

    return AnalyticsDashboardResponse(
        total_searches=total_searches,
        no_results_count=no_results_count,
        click_through_rate=ctr,
        top_queries=top_queries,
        top_clicked_products=top_clicked_products
    )
