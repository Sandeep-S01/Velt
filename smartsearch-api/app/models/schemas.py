"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Store schemas
class StoreBase(BaseModel):
    name: str
    platform: str
    platform_store_id: Optional[str] = None
    webhook_secret: Optional[str] = None
    is_active: bool = True
    sync_frequency_hours: int = 24
    widget_config: Optional[Dict[str, Any]] = None
    search_config: Optional[Dict[str, Any]] = None

class StoreCreate(StoreBase):
    pass

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None
    platform_store_id: Optional[str] = None
    webhook_secret: Optional[str] = None
    is_active: Optional[bool] = None  # Fixed: was str, should be bool
    sync_frequency_hours: Optional[int] = None
    widget_config: Optional[Dict[str, Any]] = None
    search_config: Optional[Dict[str, Any]] = None

class StoreResponse(StoreBase):
    id: str
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Product schemas
class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    inventory_count: int = 0
    is_active: bool = True
    product_metadata: Optional[Dict[str, Any]] = None

class ProductCreate(ProductBase):
    id: str  # Store's product ID
    store_id: str

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    inventory_count: Optional[int] = None
    is_active: Optional[bool] = None
    product_metadata: Optional[Dict[str, Any]] = None

class ProductResponse(ProductBase):
    id: str
    store_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# API Key schemas
class APIKeyBase(BaseModel):
    name: str
    is_active: bool = True
    expires_at: Optional[datetime] = None

class APIKeyCreate(APIKeyBase):
    pass

class APIKeyUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class APIKeyResponse(APIKeyBase):
    id: int
    key: str  # Only returned on creation
    store_id: str
    last_used_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True
    is_verified: bool = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class UserResponse(UserBase):
    id: str
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Search schemas (existing ones from main.py)
class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class SearchResult(BaseModel):
    id: str
    description: str
    metadata: dict
    score: float

# Enums
class PlatformEnum(str, Enum):
    SHOPIFY = "shopify"
    WOOCART = "woocommerce"
    CUSTOM = "custom"

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

# Ingest schemas for CSV/JSON upload
class ProductIngest(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    inventory_count: int = 0
    product_metadata: Optional[Dict[str, Any]] = None

class IngestRequest(BaseModel):
    store_id: str
    products: List[ProductIngest]
    sync_mode: Optional[str] = "upsert"

class IngestResponse(BaseModel):
    processed: int
    failed: int
    errors: List[str] = []