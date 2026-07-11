"""
Product service for handling product-related operations.
"""

from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.database import Product
from app.models.schemas import ProductCreate, ProductUpdate

def get_product(db: Session, product_id: str, store_id: str | None = None):
    """Get a product by internal or store-scoped external ID."""
    query = db.query(Product).filter(
        or_(Product.id == product_id, Product.external_id == product_id)
    )
    if store_id is not None:
        query = query.filter(Product.store_id == store_id)
    return query.first()

def get_products_by_store(db: Session, store_id: str, skip: int = 0, limit: int = 100):
    """Get products for a specific store with pagination."""
    return db.query(Product).filter(Product.store_id == store_id).offset(skip).limit(limit).all()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    """Get multiple products with pagination."""
    return db.query(Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate):
    """Create a new product."""
    product_data = product.model_dump()
    external_id = product_data.pop("id")
    db_product = Product(**product_data, external_id=external_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(
    db: Session,
    product_id: str,
    product: ProductUpdate,
    store_id: str | None = None,
):
    """Update an existing product."""
    db_product = get_product(db, product_id=product_id, store_id=store_id)
    if db_product:
        update_data = product.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: str, store_id: str | None = None):
    """Delete a product."""
    db_product = get_product(db, product_id=product_id, store_id=store_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product
