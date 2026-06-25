"""
API routes for semantic search.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.utils.security import verify_api_key
from app.core.search_engine import SemanticSearchEngine
from app.models.schemas import SearchRequest, SearchResult
import os

router = APIRouter(prefix="/search", tags=["search"])

# Dependency to retrieve the search engine singleton
def get_search_engine(request: Request) -> SemanticSearchEngine:
    """Get the search engine singleton from application state."""
    return request.app.state.search_engine

@router.post("", response_model=List[SearchResult])
def semantic_search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    api_key_info: tuple = Depends(verify_api_key),
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
):
    """
    Search for products using semantic meaning.
    Requires valid API key.
    """
    api_key, store = api_key_info

    try:
        results = search_engine.search_store(store_id=store.id, query=request.query, n_results=request.limit or 5)

        # Convert to the expected format
        return [
            SearchResult(
                id=r['id'],
                description=r['description'],
                metadata=r['metadata'],
                score=r['score']
            )
            for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: GET endpoint for simple search queries
@router.get("", response_model=List[SearchResult])
def search_get(
    q: str,
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
    return semantic_search(search_request, db, api_key_info, search_engine)