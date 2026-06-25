"""
Product service for handling product-related operations.
"""

from sqlalchemy.orm import Session
from app.models.database import Product
from app.models.schemas import ProductCreate, ProductUpdate

def get_product(db: Session, product_id: str):
    """Get a product by ID."""
    return db.query(Product).filter(Product.id == product_id).first()

def get_products_by_store(db: Session, store_id: str, skip: int = 0, limit: int = 100):
    """Get products for a specific store with pagination."""
    return db.query(Product).filter(Product.store_id == store_id).offset(skip).limit(limit).all()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    """Get multiple products with pagination."""
    return db.query(Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate):
    """Create a new product."""
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: str, product: ProductUpdate):
    """Update an existing product."""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        update_data = product.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: str):
    """Delete a product."""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product