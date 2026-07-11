"""
API routes for store search analytics and click tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import List
from app.core.database import get_db
from app.models.database import Product, SearchClickEvent, SearchQueryLog
from app.utils.security import get_current_active_user, get_owned_store

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Schema definitions
class SearchClickRequest(BaseModel):
    query_event_token: str = Field(..., min_length=20, max_length=100)
    clicked_product_id: str = Field(..., min_length=1, max_length=255)

class QueryStat(BaseModel):
    query: str
    count: int
    clicks: int

class DailySearchStat(BaseModel):
    date: str
    searches: int

class ZeroResultQueryStat(BaseModel):
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
    queries_without_results: List[ZeroResultQueryStat]
    daily_searches: List[DailySearchStat]
    average_latency_ms: float

@router.post("/click")
def track_search_click(
    request_data: SearchClickRequest,
    db: Session = Depends(get_db)
):
    """
    Log a click event on a product search result card.
    Updates the query log entry to attribute the conversion.
    """
    query_log = db.query(SearchQueryLog).filter(
        SearchQueryLog.event_token == request_data.query_event_token
    ).first()
    if not query_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search query log entry not found."
        )

    if request_data.clicked_product_id not in (query_log.result_product_ids or []):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product click")

    product_exists = db.query(Product.id).filter(
        Product.store_id == query_log.store_id,
        Product.external_id == request_data.clicked_product_id,
        Product.is_active == True,
    ).first()
    if product_exists is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product click")

    existing_click = db.query(SearchClickEvent).filter(
        SearchClickEvent.query_log_id == query_log.id
    ).first()
    if existing_click is None:
        db.add(SearchClickEvent(
            query_log_id=query_log.id,
            store_id=query_log.store_id,
            product_external_id=request_data.clicked_product_id,
        ))
    db.commit()

    return {
        "status": "success",
        "message": "Click tracked successfully.",
        "query_event_token": query_log.event_token,
        "clicked_product_id": request_data.clicked_product_id
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
    get_owned_store(db, store_id, current_user.id)

    # 1. Total searches
    total_searches = db.query(SearchQueryLog).filter(SearchQueryLog.store_id == store_id).count()

    # 2. No results count
    no_results_count = db.query(SearchQueryLog).filter(
        SearchQueryLog.store_id == store_id,
        SearchQueryLog.results_count == 0
    ).count()

    # 3. Click-through rate (CTR) calculation
    clicked_searches = db.query(SearchClickEvent).filter(
        SearchClickEvent.store_id == store_id
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

    clicks_by_query_raw = db.query(
        SearchQueryLog.query,
        func.count(SearchClickEvent.id),
    ).join(
        SearchClickEvent,
        SearchClickEvent.query_log_id == SearchQueryLog.id,
    ).filter(
        SearchQueryLog.store_id == store_id
    ).group_by(SearchQueryLog.query).all()
    clicks_by_query = dict(clicks_by_query_raw)
    top_queries = [
        QueryStat(query=q[0], count=q[1], clicks=clicks_by_query.get(q[0], 0))
        for q in top_queries_raw
    ]

    # 5. Top Clicked Products
    top_clicks_raw = db.query(
        SearchClickEvent.product_external_id,
        func.count(SearchClickEvent.id).label("count")
    ).filter(
        SearchClickEvent.store_id == store_id,
    ).group_by(
        SearchClickEvent.product_external_id
    ).order_by(
        func.count(SearchClickEvent.id).desc()
    ).limit(10).all()

    top_clicked_products = []
    for item in top_clicks_raw:
        product_id, click_count = item[0], item[1]
        prod = db.query(Product).filter(
            Product.store_id == store_id,
            Product.external_id == product_id,
        ).first()
        title = prod.title if prod else "Unknown Product"
        top_clicked_products.append(ClickedProductStat(
            product_id=product_id,
            title=title,
            click_count=click_count
        ))

    zero_result_raw = db.query(
        SearchQueryLog.query,
        func.count(SearchQueryLog.id),
    ).filter(
        SearchQueryLog.store_id == store_id,
        SearchQueryLog.results_count == 0,
    ).group_by(SearchQueryLog.query).order_by(func.count(SearchQueryLog.id).desc()).limit(10).all()

    daily_raw = db.query(
        func.date(SearchQueryLog.created_at),
        func.count(SearchQueryLog.id),
    ).filter(SearchQueryLog.store_id == store_id).group_by(
        func.date(SearchQueryLog.created_at)
    ).order_by(func.date(SearchQueryLog.created_at)).all()

    average_latency = db.query(func.avg(SearchQueryLog.duration_ms)).filter(
        SearchQueryLog.store_id == store_id,
        SearchQueryLog.duration_ms.isnot(None),
    ).scalar() or 0.0

    return AnalyticsDashboardResponse(
        total_searches=total_searches,
        no_results_count=no_results_count,
        click_through_rate=ctr,
        top_queries=top_queries,
        top_clicked_products=top_clicked_products,
        queries_without_results=[ZeroResultQueryStat(query=q, count=count) for q, count in zero_result_raw],
        daily_searches=[DailySearchStat(date=str(day), searches=count) for day, count in daily_raw],
        average_latency_ms=round(float(average_latency), 2),
    )
