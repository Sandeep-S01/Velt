"""
API routes for bulk product ingestion.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.utils.security import verify_api_key
from app.models.schemas import IngestRequest, IngestResponse
from app.services.product_service import get_product, create_product, update_product
from app.models.schemas import ProductCreate, ProductUpdate
from app.core.search_engine import SemanticSearchEngine

router = APIRouter(prefix="/ingest", tags=["ingest"])

def get_search_engine(request: Request) -> SemanticSearchEngine:
    """Dependency to retrieve search engine singleton."""
    return request.app.state.search_engine

@router.post("", response_model=IngestResponse)
def ingest_products(
    request: IngestRequest,
    db: Session = Depends(get_db),
    api_key_info: tuple = Depends(verify_api_key),
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
):
    """
    Ingest multiple products at once.
    Requires a valid API key.
    """
    api_key, store = api_key_info

    # Verify that the store_id in the request matches the store associated with the API key
    if str(store.id) != request.store_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not match store_id in request"
        )

    processed = 0
    failed = 0
    errors = []
    products_to_index = []

    for product_in in request.products:
        try:
            product_dict = product_in.dict()
            product_dict["store_id"] = request.store_id
            product_dict["is_active"] = True  # Default to active on ingestion

            # Upsert into PostgreSQL DB
            db_product = get_product(db, product_id=product_in.id)
            if db_product:
                # Update
                update_data = ProductUpdate(**product_dict)
                update_product(db, product_id=product_in.id, product=update_data)
            else:
                # Create
                create_data = ProductCreate(**product_dict)
                create_product(db, product=create_data)

            processed += 1
            products_to_index.append(product_dict)
        except Exception as e:
            failed += 1
            errors.append(f"Product {product_in.id}: {str(e)}")

    # Batch index the products in ChromaDB
    if products_to_index:
        try:
            search_engine.index_store_products(store_id=request.store_id, products=products_to_index)
        except Exception as e:
            errors.append(f"Vector Database Indexing Error: {str(e)}")

    return IngestResponse(
        processed=processed,
        failed=failed,
        errors=errors[:10]  # Limit error messages returned
    )
