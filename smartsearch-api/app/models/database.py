"""
SQLAlchemy database models for SmartSearch API.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Store(Base):
    """Store model representing an e-commerce store connected to SmartSearch."""
    __tablename__ = "stores"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    name = Column(String, nullable=False)
    platform = Column(String, nullable=False)  # shopify, woocommerce, custom
    platform_store_id = Column(String, nullable=True)  # ID from the platform
    platform_domain = Column(String, nullable=True)  # e.g., shop.myshopify.com
    api_key_encrypted = Column(String, nullable=True)
    webhook_secret = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    sync_frequency_hours = Column(Integer, default=24)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    index_status = Column(String, default="pending")  # pending, indexing, ready, error
    index_progress_percent = Column(Integer, default=0)
    total_product_count = Column(Integer, default=0)
    indexed_product_count = Column(Integer, default=0)
    widget_config = Column(JSON, nullable=True)
    search_config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="store", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="store", cascade="all, delete-orphan")

class Product(Base):
    """Product model representing a product in a store."""
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)  # Store's product ID
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=True)
    category = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    product_url = Column(String, nullable=True)
    inventory_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    product_metadata = Column(JSON, nullable=True)  # Flexible metadata storage
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    store = relationship("Store", back_populates="products")

class APIKey(Base):
    """API key model for store authentication."""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    name = Column(String, nullable=False)  # Friendly name for the key
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    store = relationship("Store", back_populates="api_keys")

class User(Base):
    """User model for dashboard authentication."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SearchQueryLog(Base):
    """Log of search queries for analytics."""
    __tablename__ = "search_query_logs"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    query = Column(Text, nullable=False)
    results_count = Column(Integer, nullable=False)
    clicked_product_id = Column(String, nullable=True)  # Which product was clicked
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    store = relationship("Store")

class WebhookEvent(Base):
    """Webhook event model to track inbound webhook event processing."""
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    event_type = Column(String, nullable=False)  # e.g., 'products/create', 'products/update'
    source = Column(String, nullable=False)      # 'shopify'
    external_id = Column(String, nullable=True)   # External event ID
    payload = Column(JSON, nullable=False)
    status = Column(String, default="pending")   # pending, processing, completed, failed
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    store = relationship("Store")