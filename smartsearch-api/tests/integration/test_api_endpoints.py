"""
Integration tests for the SmartSearch API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
import os
import shutil
import io

import app.core.database
# Mock table creation and Redis checks for the app startup lifespan to avoid connecting to Postgres/Redis
app.core.database.create_tables = lambda: None
app.core.database.get_redis = lambda: None

from app.main import app
from app.core.database import get_db, Base
from app.core.search_engine import SemanticSearchEngine
from app.models.database import APIKey, Store, Product
from tests.conftest import engine, TestingSessionLocal

# Create a temporary directory for test ChromaDB
TEST_CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "test_chroma_db")

@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Setup and teardown test ChromaDB folder."""
    os.makedirs(TEST_CHROMA_DB_PATH, exist_ok=True)
    yield
    if os.path.exists(TEST_CHROMA_DB_PATH):
        shutil.rmtree(TEST_CHROMA_DB_PATH, ignore_errors=True)

@pytest.fixture(scope="function")
def client():
    """Create test client with overridden dependencies."""
    # Override get_db to use SQLite test session
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Initialize search engine singleton on the app state using test ChromaDB
    test_search_engine = SemanticSearchEngine(db_path=TEST_CHROMA_DB_PATH)
    app.state.search_engine = test_search_engine
    
    # Clean up test database tables
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as c:
        yield c
        
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

def test_full_api_workflow(client):
    """Test user registration, login, store creation, api key auth, product ingest, and search."""
    
    # 1. Register a new user
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "merchant@example.com",
            "full_name": "Merchant Joe",
            "password": "securepassword123"
        }
    )
    assert register_response.status_code == 200
    user_id = register_response.json()["id"]
    assert register_response.json()["email"] == "merchant@example.com"
    
    # 2. Login to get JWT
    login_response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "merchant@example.com",
            "password": "securepassword123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create a store using the JWT token
    store_response = client.post(
        "/api/v1/stores/",
        json={
            "name": "Joe's Gear",
            "platform": "shopify",
            "platform_store_id": "store_joe_99",
            "is_active": True,
            "sync_frequency_hours": 24
        },
        headers=headers
    )
    assert store_response.status_code == 200
    store_id = store_response.json()["id"]
    
    # 4. Generate an API Key for this store manually in DB for testing
    db = TestingSessionLocal()
    api_key_str = "ss_live_joe_test_api_key_123"
    api_key_obj = APIKey(
        key=api_key_str,
        store_id=store_id,
        name="Test Ingest Key",
        is_active=True
    )
    db.add(api_key_obj)
    db.commit()
    db.close()
    
    # 5. Ingest products via JSON payload using API Key header authentication
    ingest_headers = {"X-API-Key": api_key_str}
    products_payload = {
        "store_id": store_id,
        "products": [
            {
                "id": "p1",
                "title": "Ergonomic Mesh Chair Pro",
                "description": "Breathable mesh office chair with full lumbar support and adjustable headrest.",
                "price": 199.99,
                "category": "Furniture"
            },
            {
                "id": "p2",
                "title": "Insulated Metal Water Bottle",
                "description": "Double-walled vacuum insulated water bottle. Keeps water freezing cold for 24 hours.",
                "price": 24.50,
                "category": "Outdoors"
            }
        ]
    }
    ingest_response = client.post(
        "/api/v1/ingest",
        json=products_payload,
        headers=ingest_headers
    )
    assert ingest_response.status_code == 200
    assert ingest_response.json()["processed"] == 2
    assert ingest_response.json()["failed"] == 0
    
    # 6. Verify that products are stored in Postgres test database
    db = TestingSessionLocal()
    db_products = db.query(Product).filter(Product.store_id == store_id).all()
    assert len(db_products) == 2
    assert any(p.title == "Ergonomic Mesh Chair Pro" for p in db_products)
    db.close()
    
    # 7. Query semantic search for "comfort seat for long work hours" using header authentication
    search_response = client.post(
        "/api/v1/search",
        json={"query": "comfort seat for long work hours", "limit": 3},
        headers=ingest_headers
    )
    assert search_response.status_code == 200
    results = search_response.json()
    assert len(results) >= 1
    # The ergonomic chair should rank first with a higher score than the water bottle
    assert results[0]["id"] == "p1"
    assert " lumbar " in results[0]["description"] or " chair " in results[0]["description"]
    
    # 8. Test CSV Ingest via upload endpoint
    csv_content = (
        "id,title,description,price,category\n"
        "p3,Organic Green Tea Box,Matcha and loose leaf organic green tea rich in antioxidants.,14.99,Grocery\n"
        "p4,Running Shoes Men,Comfortable running shoe with cushioned sole.,65.00,Sports\n"
    )
    csv_file = io.BytesIO(csv_content.encode("utf-8"))
    
    upload_response = client.post(
        f"/api/v1/stores/{store_id}/products/upload",
        files={"file": ("test_products.csv", csv_file, "text/csv")},
        headers=ingest_headers
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["products_created"] == 2
    assert upload_response.json()["products_failed"] == 0
    
    # 9. Query semantic search for "hot antioxidant beverage" using query param fallback API key
    search_query_param_response = client.post(
        f"/api/v1/search?api_key={api_key_str}",
        json={"query": "hot antioxidant beverage"}
    )
    assert search_query_param_response.status_code == 200
    results_query = search_query_param_response.json()
    assert len(results_query) >= 1
    # Green tea should rank first
    assert results_query[0]["id"] == "p3"
