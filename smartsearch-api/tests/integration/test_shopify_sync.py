"""
Integration tests for Shopify OAuth connection, webhook processing, and Celery sync tasks.
"""

import pytest
from fastapi.testclient import TestClient
import os
import shutil
import json
import base64
import hmac
import hashlib

import app.core.database
# Stub out database and Redis connections on app lifespan to prevent starting them up
app.core.database.create_tables = lambda: None
app.core.database.get_redis = lambda: None

from app.main import app
from app.core.database import get_db, Base
from app.core.search_engine import SemanticSearchEngine
from app.models.database import Store, Product, WebhookEvent, User
from app.integrations.shopify import decrypt_token
from tests.conftest import engine, TestingSessionLocal
from app.core.config import settings

TEST_CHROMA_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_shopify_chroma_db"))
settings.CHROMA_DB_PATH = TEST_CHROMA_DB_PATH


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Setup and teardown test ChromaDB folder."""
    os.makedirs(TEST_CHROMA_DB_PATH, exist_ok=True)
    yield
    if os.path.exists(TEST_CHROMA_DB_PATH):
        shutil.rmtree(TEST_CHROMA_DB_PATH, ignore_errors=True)

@pytest.fixture(scope="function")
def test_client():
    """Create test client with database overrides."""
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    
    # Initialize search engine singleton using test path
    test_search_engine = SemanticSearchEngine(db_path=TEST_CHROMA_DB_PATH)
    app.state.search_engine = test_search_engine
    
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as c:
        yield c
        
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

def test_shopify_oauth_flow(test_client):
    """Test authorize redirect and callback handling."""
    # 1. Authorize redirect
    auth_resp = test_client.get(
        "/api/v1/shopify/authorize?shop=my-test-store&user_id=user123",
        follow_redirects=False
    )
    assert auth_resp.status_code == 307
    location = auth_resp.headers["location"]
    assert "my-test-store.myshopify.com" in location
    assert "client_id=" in location
    assert "state=user123_" in location

    # 2. Callback exchange
    # Generate state parameter to simulate callback
    state_param = "user123_abcde12345"
    callback_resp = test_client.get(
        f"/api/v1/shopify/callback?code=mock_authorization_code&shop=my-test-store&state={state_param}"
    )
    assert callback_resp.status_code == 200
    res_data = callback_resp.json()
    assert res_data["status"] == "success"
    store_id = res_data["store_id"]
    
    # Verify Store is in Postgres
    db = TestingSessionLocal()
    store = db.query(Store).filter(Store.id == store_id).first()
    assert store is not None
    assert store.platform == "shopify"
    assert store.platform_domain == "my-test-store.myshopify.com"
    assert store.index_status == "ready"
    
    # Verify Decrypted Access Token
    token = decrypt_token(store.api_key_encrypted)
    assert token == "mock_access_token_for_my-test-store.myshopify.com"

    # Verify that products are synced inline (due to celery eager mode)
    db_products = db.query(Product).filter(Product.store_id == store_id).all()
    assert len(db_products) == 2
    assert any(p.title == "Mock Shopify Product A" for p in db_products)
    assert any(p.title == "Mock Shopify Product B" for p in db_products)
    
    # Verify that products are searchable in ChromaDB
    se = app.state.search_engine
    results = se.search_store(store_id=store_id, query="awesome product description", n_results=3)
    assert len(results) >= 1
    assert results[0]["id"] == "789012"  # Mock product B ID
    db.close()

def test_shopify_webhooks(test_client):
    """Test webhook signature verification and async update/delete events."""
    db = TestingSessionLocal()
    # Create the store first
    store = Store(
        name="Webhook Shop",
        platform="shopify",
        platform_domain="webhook-shop.myshopify.com",
        webhook_secret="supersecretwebhookkey",
        index_status="ready"
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    store_id = store.id
    db.close()

    # 1. Test Webhook Update/Create Event
    product_update_payload = {
        "id": 112233,
        "title": "Shiny New Shoes",
        "body_html": "These shoes are very shiny and new.",
        "vendor": "ShinyCo",
        "product_type": "Footwear",
        "variants": [{"price": "99.99", "inventory_quantity": 50}],
        "images": [{"src": "https://example.com/shoes.jpg"}]
    }

    # Post update webhook
    headers = {
        "X-Shopify-Shop-Domain": "webhook-shop.myshopify.com",
        "X-Shopify-Topic": "products/update",
        "X-Shopify-Hmac-Sha256": "mock_hmac_signature",
        "Content-Type": "application/json"
    }
    
    webhook_resp = test_client.post(
        "/api/v1/webhooks/shopify",
        json=product_update_payload,
        headers=headers
    )
    assert webhook_resp.status_code == 200
    event_id = webhook_resp.json()["event_id"]

    db = TestingSessionLocal()
    # Verify WebhookEvent status
    event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
    assert event is not None
    assert event.status == "completed"

    # Verify Product in Database
    prod = db.query(Product).filter(Product.store_id == store_id, Product.id == "112233").first()
    assert prod is not None
    assert prod.title == "Shiny New Shoes"
    assert float(prod.price) == 99.99
    
    # Verify searchable in ChromaDB
    se = app.state.search_engine
    results = se.search_store(store_id=store_id, query="shiny footwear", n_results=1)
    assert len(results) == 1
    assert results[0]["id"] == "112233"
    assert "shiny" in results[0]["description"]
    db.close()

    # 2. Test Webhook Delete Event
    product_delete_payload = {
        "id": 112233
    }
    headers["X-Shopify-Topic"] = "products/delete"
    
    delete_resp = test_client.post(
        "/api/v1/webhooks/shopify",
        json=product_delete_payload,
        headers=headers
    )
    assert delete_resp.status_code == 200
    
    db = TestingSessionLocal()
    # Verify deleted in Postgres
    deleted_prod = db.query(Product).filter(Product.store_id == store_id, Product.id == "112233").first()
    assert deleted_prod is None
    
    # Verify deleted in ChromaDB
    results_after_delete = se.search_store(store_id=store_id, query="shiny footwear", n_results=1)
    assert len(results_after_delete) == 0
    db.close()
