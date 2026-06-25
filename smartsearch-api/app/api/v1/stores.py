"""
API routes for store management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io

from app.core.database import get_db
from app.utils.security import get_current_active_user, verify_api_key
from app.models.database import Store, User, APIKey
from app.models.schemas import StoreCreate, StoreUpdate, StoreResponse, APIKeyCreate, APIKeyResponse
from app.services.store_service import (
    get_store, get_stores, create_store, update_store, delete_store
)

router = APIRouter(prefix="/stores", tags=["stores"])

@router.post("/", response_model=StoreResponse)
def create_new_store(
    store: StoreCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new store."""
    return create_store(db=db, store=store)

@router.get("/", response_model=List[StoreResponse])
def read_stores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Retrieve stores with pagination."""
    stores = get_stores(db, skip=skip, limit=limit)
    return stores

@router.get("/{store_id}", response_model=StoreResponse)
def read_store(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific store by ID."""
    db_store = get_store(db, store_id=store_id)
    if db_store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return db_store

@router.put("/{store_id}", response_model=StoreResponse)
def update_existing_store(
    store_id: str,
    store: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update a store."""
    db_store = update_store(db, store_id=store_id, store=store)
    if db_store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return db_store

@router.delete("/{store_id}")
def delete_existing_store(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Delete a store."""
    success = delete_store(db, store_id=store_id)
    if not success:
        raise HTTPException(status_code=404, detail="Store not found")
    return {"message": "Store deleted successfully"}

from fastapi import Request
from app.core.search_engine import SemanticSearchEngine
from app.services.product_service import get_product, create_product, update_product
from app.models.schemas import ProductCreate, ProductUpdate

def get_search_engine(request: Request) -> SemanticSearchEngine:
    """Dependency to retrieve search engine singleton."""
    return request.app.state.search_engine

@router.post("/{store_id}/products/upload")
async def upload_products_csv(
    store_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    api_key_info: tuple = Depends(verify_api_key),
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
):
    """
    Upload products via CSV file.
    Requires valid API key for the store.
    """
    api_key, store = api_key_info

    # Verify that the store_id matches the API key's store
    if str(store.id) != store_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not match store"
        )

    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )

    # Read and parse CSV
    contents = await file.read()
    csv_file = io.StringIO(contents.decode('utf-8'))
    csv_reader = csv.DictReader(csv_file)

    # Process products
    products_created = 0
    products_failed = 0
    errors = []
    products_to_index = []

    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 since header is row 1
        try:
            # Validate required fields
            if not row.get('id') or not row.get('title'):
                errors.append(f"Row {row_num}: Missing required fields (id, title)")
                products_failed += 1
                continue

            # Create product object
            product_data = {
                "id": row['id'],
                "store_id": store_id,
                "title": row['title'],
                "description": row.get('description'),
                "price": float(row['price']) if row.get('price') else None,
                "category": row.get('category'),
                "brand": row.get('brand'),
                "image_url": row.get('image_url'),
                "product_url": row.get('product_url'),
                "inventory_count": int(row['inventory_count']) if row.get('inventory_count') else 0,
                "is_active": row.get('is_active', 'true').lower() == 'true'
            }

            # Upsert into PostgreSQL DB
            db_product = get_product(db, product_id=product_data["id"])
            if db_product:
                # Update existing product
                update_data = ProductUpdate(**product_data)
                update_product(db, product_id=product_data["id"], product=update_data)
            else:
                # Create new product
                create_data = ProductCreate(**product_data)
                create_product(db, product=create_data)

            products_created += 1
            products_to_index.append(product_data)

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            products_failed += 1

    # Batch index the uploaded products in ChromaDB
    if products_to_index:
        try:
            search_engine.index_store_products(store_id=store_id, products=products_to_index)
        except Exception as e:
            errors.append(f"Vector Database Indexing Error: {str(e)}")

    return {
        "store_id": store_id,
        "filename": file.filename,
        "products_processed": products_created + products_failed,
        "products_created": products_created,
        "products_failed": products_failed,
        "errors": errors[:10]  # Limit errors returned
    }

import secrets

@router.post("/{store_id}/keys", response_model=APIKeyResponse)
def create_store_api_key(
    store_id: str,
    key_in: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Generate a new API key for the store."""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
        
    new_key = f"ss_live_{secrets.token_hex(20)}"
    
    db_api_key = APIKey(
        key=new_key,
        store_id=store_id,
        name=key_in.name,
        is_active=key_in.is_active,
        expires_at=key_in.expires_at
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

@router.get("/{store_id}/keys", response_model=List[APIKeyResponse])
def get_store_api_keys(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Retrieve active API keys for the store."""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
        
    return db.query(APIKey).filter(APIKey.store_id == store_id).all()

@router.delete("/{store_id}/keys/{key_id}")
def revoke_store_api_key(
    store_id: str,
    key_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Revoke/Delete an API key."""
    db_key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.store_id == store_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="API key not found")
        
    db.delete(db_key)
    db.commit()
    return {"message": "API key revoked successfully"}