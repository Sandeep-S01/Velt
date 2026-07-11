"""
SQLAlchemy database models for SmartSearch API.
"""

from sqlalchemy import Boolean, Column, DateTime, DECIMAL, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import secrets
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())


def generate_widget_token():
    return f"ss_widget_{secrets.token_urlsafe(24)}"

class Store(Base):
    """Store model representing an e-commerce store connected to SmartSearch."""
    __tablename__ = "stores"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    owner_user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    widget_token = Column(String, unique=True, nullable=False, default=generate_widget_token)
    widget_allowed_origins = Column(JSON, nullable=True)
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
    owner = relationship("User", back_populates="stores")

class Product(Base):
    """Product model representing a product in a store."""
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("store_id", "external_id", name="uq_products_store_external_id"),
    )

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    external_id = Column(String, nullable=False)
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
    key = Column(String, unique=True, index=True, nullable=True)  # Legacy migration only
    key_hash = Column(String, unique=True, index=True, nullable=True)
    key_prefix = Column(String, index=True, nullable=True)
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    name = Column(String, nullable=False)  # Friendly name for the key
    scopes = Column(String, nullable=False, default="search,ingest")
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
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

    stores = relationship("Store", back_populates="owner")

class SearchQueryLog(Base):
    """Log of search queries for analytics."""
    __tablename__ = "search_query_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_token = Column(String, unique=True, nullable=False, default=generate_uuid, index=True)
    store_id = Column(String, ForeignKey("stores.id"), nullable=False)
    query = Column(Text, nullable=False)
    results_count = Column(Integer, nullable=False)
    result_product_ids = Column(JSON, nullable=True)
    duration_ms = Column(Float, nullable=True)
    clicked_product_id = Column(String, nullable=True)  # Which product was clicked
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    store = relationship("Store")


class SearchClickEvent(Base):
    """Immutable click attribution event for a search result."""
    __tablename__ = "search_click_events"
    __table_args__ = (
        UniqueConstraint("query_log_id", name="uq_search_click_events_query_log"),
    )

    id = Column(String, primary_key=True, default=generate_uuid)
    query_log_id = Column(Integer, ForeignKey("search_query_logs.id", ondelete="CASCADE"), nullable=False)
    store_id = Column(String, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    product_external_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class WebhookEvent(Base):
    """Webhook event model to track inbound webhook event processing."""
    __tablename__ = "webhook_events"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_webhook_events_source_external_id"),
    )

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
