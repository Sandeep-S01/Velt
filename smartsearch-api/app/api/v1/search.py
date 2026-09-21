"""
API routes for semantic search.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import time

from app.core.database import get_db
from app.utils.security import require_api_key_scope, verify_api_key
from app.core.search_engine import SemanticSearchEngine
from app.core.query_parser import derive_search_filters
from app.models.schemas import SearchRequest, SearchResult
from app.models.database import SearchQueryLog

router = APIRouter(prefix="/search", tags=["search"])

# Dependency to retrieve the search engine singleton
def get_search_engine(request: Request) -> SemanticSearchEngine:
    """Get the search engine singleton from application state."""
    return request.app.state.search_engine

@router.post("", response_model=List[SearchResult])
def semantic_search(
    request: SearchRequest,
    response: Response,
    db: Session = Depends(get_db),
    api_key_info: tuple = Depends(verify_api_key),
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
):
    """
    Search for products using semantic meaning.
    Requires valid API key.
    """
    api_key, store = api_key_info
    require_api_key_scope(api_key, "search")

    try:
        started_at = time.perf_counter()
        threshold = float((store.search_config or {}).get("min_score_threshold", 0.25))
        filters = derive_search_filters(
            request.query,
            request.filters.model_dump(exclude_none=True) if request.filters else None,
        )
        if (store.search_config or {}).get("exclude_out_of_stock"):
            filters.setdefault("in_stock", True)
        results = search_engine.search_store(
            store_id=store.id,
            query=request.query,
            n_results=request.limit or 5,
            min_score=max(0.0, min(1.0, threshold)),
            filters=filters,
        )

        formatted_results = [
            SearchResult(
                id=r['id'],
                description=r['description'],
                metadata=r['metadata'],
                score=r['score']
            )
            for r in results
        ]
        log = SearchQueryLog(
            store_id=store.id,
            query=request.query,
            results_count=len(formatted_results),
            result_product_ids=[result.id for result in formatted_results],
            duration_ms=round((time.perf_counter() - started_at) * 1000, 2),
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        response.headers["X-Query-Event-Token"] = log.event_token
        return formatted_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: GET endpoint for simple search queries
@router.get("", response_model=List[SearchResult])
def search_get(
    q: str,
    response: Response,
    limit: Optional[int] = 5,
    db: Session = Depends(get_db),
    api_key_info: tuple = Depends(verify_api_key),
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
):
    """
    Search for products using GET request (for simple queries).
    Requires valid API key.
    """
    search_request = SearchRequest(query=q, limit=limit)
    return semantic_search(search_request, response, db, api_key_info, search_engine)
