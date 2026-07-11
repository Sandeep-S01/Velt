"""
API routes for product management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.database import Product, Store
from app.models.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.utils.security import get_current_active_user, get_owned_product, get_owned_store
from app.services.product_service import (
    get_products_by_store,
    create_product, update_product, delete_product
)

router = APIRouter(prefix="/products", tags=["products"])

from fastapi import Request
from app.core.search_engine import SemanticSearchEngine

def get_search_engine(request: Request) -> SemanticSearchEngine:
    """Dependency to retrieve search engine singleton."""
    return request.app.state.search_engine

@router.post("/", response_model=ProductResponse)
def create_new_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
):
    """Create a new product."""
    get_owned_store(db, product.store_id, current_user.id)
    db_product = create_product(db=db, product=product)

    # Index in ChromaDB
    try:
        product_dict = {
            "id": db_product.external_id,
            "title": db_product.title,
            "description": db_product.description,
            "price": float(db_product.price) if db_product.price is not None else None,
            "category": db_product.category,
            "brand": db_product.brand,
            "image_url": db_product.image_url,
            "product_url": db_product.product_url,
            "is_active": db_product.is_active,
        }
        search_engine.index_store_products(store_id=db_product.store_id, products=[product_dict])
    except Exception as e:
        # Log error, but return created product successfully
        print(f"ChromaDB Indexing Error: {str(e)}")

    return db_product

@router.get("/", response_model=List[ProductResponse])
def read_products(
    skip: int = 0,
    limit: int = 100,
    store_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Retrieve products with optional store filter and pagination."""
    if store_id:
        get_owned_store(db, store_id, current_user.id)
        products = get_products_by_store(db, store_id=store_id, skip=skip, limit=limit)
    else:
        products = db.query(Product).join(Store).filter(
            Store.owner_user_id == current_user.id
        ).offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
def read_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific product by ID."""
    return get_owned_product(db, product_id, current_user.id)

@router.put("/{product_id}", response_model=ProductResponse)
def update_existing_product(
    product_id: str,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
):
    """Update a product."""
    owned_product = get_owned_product(db, product_id, current_user.id)
    db_product = update_product(
        db,
        product_id=owned_product.id,
        product=product,
        store_id=owned_product.store_id,
    )

    # Index updated product in ChromaDB
    try:
        product_dict = {
            "id": db_product.external_id,
            "title": db_product.title,
            "description": db_product.description,
            "price": float(db_product.price) if db_product.price is not None else None,
            "category": db_product.category,
            "brand": db_product.brand,
            "image_url": db_product.image_url,
            "product_url": db_product.product_url,
            "is_active": db_product.is_active,
        }
        search_engine.index_store_products(store_id=db_product.store_id, products=[product_dict])
    except Exception as e:
        print(f"ChromaDB Re-indexing Error: {str(e)}")

    return db_product

@router.delete("/{product_id}")
def delete_existing_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
):
    """Delete a product."""
    db_product = get_owned_product(db, product_id, current_user.id)

    store_id = db_product.store_id
    success = delete_product(db, product_id=db_product.id, store_id=db_product.store_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete from ChromaDB
    try:
        search_engine.delete_store_products(store_id=store_id, ids=[db_product.external_id])
    except Exception as e:
        print(f"ChromaDB Deletion Error: {str(e)}")

    return {"message": "Product deleted successfully"}

@router.get("/store/{store_id}", response_model=List[ProductResponse])
def read_products_by_store(
    store_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all products for a specific store."""
    get_owned_store(db, store_id, current_user.id)
    products = get_products_by_store(db, store_id=store_id, skip=skip, limit=limit)
    return products
