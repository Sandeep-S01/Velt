"""Public semantic-search playground backed by a small curated catalog."""

from threading import Lock
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.core.query_parser import derive_search_filters
from app.core.search_engine import SemanticSearchEngine


router = APIRouter(prefix="/demo", tags=["demo"])
DEMO_STORE_ID = "velt-public-demo"
_demo_index_lock = Lock()

DEMO_PRODUCTS = [
    {
        "id": "jacket-storm-shell",
        "title": "StormShield Pro Shell",
        "description": "Lightweight breathable waterproof rain jacket for hiking and travel.",
        "price": 110.0,
        "category": "Jackets",
        "brand": "Northline",
    },
    {
        "id": "jacket-windbreaker",
        "title": "Packable Trail Windbreaker",
        "description": "Ultralight wind resistant jacket that packs into its own pocket.",
        "price": 89.0,
        "category": "Jackets",
        "brand": "Northline",
    },
    {
        "id": "shoe-derby",
        "title": "Derby Leather Office Shoes",
        "description": "Black formal leather shoes with a cushioned sole for long office days.",
        "price": 89.0,
        "category": "Footwear",
        "brand": "Alden Row",
    },
    {
        "id": "shoe-oxford",
        "title": "Sleek Oxford Loafers",
        "description": "Professional black slip-on loafers for business and formal wear.",
        "price": 75.0,
        "category": "Footwear",
        "brand": "Alden Row",
    },
    {
        "id": "hoodie-alpine",
        "title": "Alpine Thermal Hoodie",
        "description": "Warm blue winter hoodie with soft fleece and thermal lining.",
        "price": 68.0,
        "category": "Hoodies",
        "brand": "Hearth",
    },
    {
        "id": "hoodie-pullover",
        "title": "Classic Cozy Pullover",
        "description": "Soft navy cotton pullover for cool weather and relaxed weekends.",
        "price": 59.0,
        "category": "Hoodies",
        "brand": "Hearth",
    },
    {
        "id": "bottle-insulated",
        "title": "Summit Insulated Bottle",
        "description": "Leakproof stainless steel bottle that keeps drinks cold for 24 hours.",
        "price": 32.0,
        "category": "Outdoors",
        "brand": "Summit",
    },
    {
        "id": "chair-ergonomic",
        "title": "Ergonomic Mesh Office Chair",
        "description": "Breathable desk chair with lumbar support for long work sessions.",
        "price": 199.0,
        "category": "Furniture",
        "brand": "Workwell",
    },
]


class DemoSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=200)
    limit: int = Field(default=3, ge=1, le=5)


class DemoSearchProduct(BaseModel):
    id: str
    title: str
    description: str
    price: float
    category: str
    score: float


class DemoSearchResponse(BaseModel):
    query: str
    applied_filters: dict[str, Any]
    products: list[DemoSearchProduct]


def get_search_engine(request: Request) -> SemanticSearchEngine:
    return request.app.state.search_engine


def _ensure_demo_catalog(search_engine: SemanticSearchEngine) -> None:
    if getattr(search_engine, "_velt_demo_ready", False):
        return
    with _demo_index_lock:
        if getattr(search_engine, "_velt_demo_ready", False):
            return
        search_engine.index_store_products(DEMO_STORE_ID, DEMO_PRODUCTS)
        search_engine._velt_demo_ready = True


@router.post("/search", response_model=DemoSearchResponse)
def search_demo_catalog(
    request_data: DemoSearchRequest,
    search_engine: SemanticSearchEngine = Depends(get_search_engine),
):
    """Run a real semantic query against the public demonstration catalog."""
    try:
        _ensure_demo_catalog(search_engine)
        filters = derive_search_filters(request_data.query)
        results = search_engine.search_store(
            DEMO_STORE_ID,
            request_data.query,
            n_results=request_data.limit,
            min_score=0.0,
            filters=filters,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The semantic-search demo is temporarily unavailable",
        ) from exc

    return DemoSearchResponse(
        query=request_data.query,
        applied_filters=filters,
        products=[
            DemoSearchProduct(
                id=result["id"],
                title=result["metadata"]["title"],
                description=result["description"],
                price=float(result["metadata"]["price"]),
                category=result["metadata"]["category"],
                score=result["score"],
            )
            for result in results
        ],
    )
