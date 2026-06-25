"""
Database integration tests.
"""

import pytest
from sqlalchemy.orm import Session
from app.models.database import Store, Product, APIKey, User, SearchQueryLog
from app.services.store_service import create_store, get_store, get_stores, update_store, delete_store
from app.services.product_service import create_product, get_product, get_products_by_store, update_product, delete_product
from app.services.user_service import create_user, get_user, get_users, update_user, delete_user, authenticate_user
from app.models.schemas import StoreCreate, StoreUpdate, ProductCreate, ProductUpdate, UserCreate, UserUpdate


def test_store_crud_operations(db_session: Session):
    """Test CRUD operations for Store model."""
    # Create
    store_data = StoreCreate(
        name="Test Store",
        platform="shopify",
        platform_store_id="store_123",
        is_active=True
    )
    db_store = create_store(db_session, store_data)
    assert db_store.id is not None
    assert db_store.name == "Test Store"
    assert db_store.platform == "shopify"

    # Read
    retrieved_store = get_store(db_session, db_store.id)
    assert retrieved_store is not None
    assert retrieved_store.name == "Test Store"

    # List
    stores = get_stores(db_session)
    assert len(stores) >= 1
    assert any(s.id == db_store.id for s in stores)

    # Update
    update_data = StoreUpdate(name="Updated Store Name")
    updated_store = update_store(db_session, db_store.id, update_data)
    assert updated_store is not None
    assert updated_store.name == "Updated Store Name"

    # Delete
    deleted_store = delete_store(db_session, db_store.id)
    assert deleted_store is not None
    assert delete_store(db_session, db_store.id) is None  # Already deleted


def test_product_crud_operations(db_session: Session):
    """Test CRUD operations for Product model."""
    # First create a store to associate with the product
    store_data = StoreCreate(
        name="Test Store for Product",
        platform="shopify",
        is_active=True
    )
    db_store = create_store(db_session, store_data)

    # Create
    product_data = ProductCreate(
        id="product_123",
        store_id=db_store.id,
        title="Test Product",
        description="A test product",
        price=29.99,
        category="Electronics",
        brand="TestBrand",
        is_active=True
    )
    db_product = create_product(db_session, product_data)
    assert db_product.id == "product_123"
    assert db_product.store_id == db_store.id
    assert db_product.title == "Test Product"

    # Read
    retrieved_product = get_product(db_session, db_product.id)
    assert retrieved_product is not None
    assert retrieved_product.title == "Test Product"

    # List by store
    products = get_products_by_store(db_session, db_store.id)
    assert len(products) >= 1
    assert any(p.id == db_product.id for p in products)

    # Update
    update_data = ProductUpdate(title="Updated Product Name")
    updated_product = update_product(db_session, db_product.id, update_data)
    assert updated_product is not None
    assert updated_product.title == "Updated Product Name"

    # Delete
    deleted_product = delete_product(db_session, db_product.id)
    assert deleted_product is not None
    assert delete_product(db_session, db_product.id) is None  # Already deleted


def test_user_crud_operations(db_session: Session):
    """Test CRUD operations for User model."""
    # Create
    user_data = UserCreate(
        email="test@example.com",
        full_name="Test User",
        password="password123",  # Shorter password to avoid bcrypt issues
        is_active=True,
        is_verified=False
    )
    db_user = create_user(db_session, user_data)
    assert db_user.id is not None
    assert db_user.email == "test@example.com"
    assert db_user.full_name == "Test User"

    # Read
    retrieved_user = get_user(db_session, db_user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"

    # List
    users = get_users(db_session)
    assert len(users) >= 1
    assert any(u.id == db_user.id for u in users)

    # Update
    update_data = UserUpdate(full_name="Updated User Name")
    updated_user = update_user(db_session, db_user.id, update_data)
    assert updated_user is not None
    assert updated_user.full_name == "Updated User Name"

    # Delete
    deleted_user = delete_user(db_session, db_user.id)
    assert deleted_user is not None
    assert delete_user(db_session, db_user.id) is None  # Already deleted


def test_model_relationships(db_session: Session):
    """Test relationships between models."""
    # Create a store
    store_data = StoreCreate(
        name="Relationship Test Store",
        platform="shopify",
        is_active=True
    )
    db_store = create_store(db_session, store_data)

    # Create products for the store
    product_data_1 = ProductCreate(
        id="product_1",
        store_id=db_store.id,
        title="Product 1",
        description="First product",
        price=10.00,
        category="Category A",
        is_active=True
    )
    product_data_2 = ProductCreate(
        id="product_2",
        store_id=db_store.id,
        title="Product 2",
        description="Second product",
        price=20.00,
        category="Category B",
        is_active=True
    )

    db_product_1 = create_product(db_session, product_data_1)
    db_product_2 = create_product(db_session, product_data_2)

    # Test store -> products relationship
    assert len(db_store.products) == 2
    product_ids = [p.id for p in db_store.products]
    assert "product_1" in product_ids
    assert "product_2" in product_ids

    # Test product -> store relationship
    assert db_product_1.store.id == db_store.id
    assert db_product_2.store.id == db_store.id
    assert db_product_1.store.name == "Relationship Test Store"
    assert db_product_2.store.name == "Relationship Test Store"


def test_api_key_model(db_session: Session):
    """Test APIKey model."""
    # Create a store first
    store_data = StoreCreate(
        name="API Key Test Store",
        platform="shopify",
        is_active=True
    )
    db_store = create_store(db_session, store_data)

    # Create API key
    api_key = APIKey(
        key="test_api_key_12345",
        store_id=db_store.id,
        name="Test Key",
        is_active=True
    )
    db_session.add(api_key)
    db_session.commit()
    db_session.refresh(api_key)

    assert api_key.id is not None
    assert api_key.key == "test_api_key_12345"
    assert api_key.store_id == db_store.id
    assert api_key.name == "Test Key"
    assert api_key.is_active is True

    # Test relationship
    assert api_key.store.id == db_store.id
    assert api_key.store.name == "API Key Test Store"


def test_search_query_log_model(db_session: Session):
    """Test SearchQueryLog model."""
    # Create a store first
    store_data = StoreCreate(
        name="Search Log Test Store",
        platform="shopify",
        is_active=True
    )
    db_store = create_store(db_session, store_data)

    # Create search log
    search_log = SearchQueryLog(
        store_id=db_store.id,
        query="test search query",
        results_count=5,
        clicked_product_id="product_123"
    )
    db_session.add(search_log)
    db_session.commit()
    db_session.refresh(search_log)

    assert search_log.id is not None
    assert search_log.store_id == db_store.id
    assert search_log.query == "test search query"
    assert search_log.results_count == 5
    assert search_log.clicked_product_id == "product_123"

    # Test relationship
    assert search_log.store.id == db_store.id
    assert search_log.store.name == "Search Log Test Store"