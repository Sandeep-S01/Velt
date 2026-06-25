"""
Store service for handling store-related operations.
"""

from sqlalchemy.orm import Session
from app.models.database import Store
from app.models.schemas import StoreCreate, StoreUpdate

def get_store(db: Session, store_id: str):
    """Get a store by ID."""
    return db.query(Store).filter(Store.id == store_id).first()

def get_store_by_name(db: Session, name: str):
    """Get a store by name."""
    return db.query(Store).filter(Store.name == name).first()

def get_stores(db: Session, skip: int = 0, limit: int = 100):
    """Get multiple stores with pagination."""
    return db.query(Store).offset(skip).limit(limit).all()

def create_store(db: Session, store: StoreCreate):
    """Create a new store."""
    db_store = Store(**store.dict())
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

def update_store(db: Session, store_id: str, store: StoreUpdate):
    """Update an existing store."""
    db_store = db.query(Store).filter(Store.id == store_id).first()
    if db_store:
        update_data = store.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_store, field, value)
        db.commit()
        db.refresh(db_store)
    return db_store

def delete_store(db: Session, store_id: str):
    """Delete a store."""
    db_store = db.query(Store).filter(Store.id == store_id).first()
    if db_store:
        db.delete(db_store)
        db.commit()
    return db_store