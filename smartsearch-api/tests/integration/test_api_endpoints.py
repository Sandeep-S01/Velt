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
from app.core.config import settings
from app.core.search_engine import SemanticSearchEngine
from app.models.database import Product, SearchQueryLog
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


def test_registration_requires_policy_acceptance_and_configured_invite(client):
    missing_acceptance = client.post(
        "/api/v1/auth/register",
        json={
            "email": "no-terms@example.com",
            "full_name": "No Terms",
            "password": "securepassword123",
        },
    )
    assert missing_acceptance.status_code == 422

    previous_invite = settings.BETA_INVITE_CODE
    settings.BETA_INVITE_CODE = "private-beta-code-123"
    try:
        rejected = client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrong-invite@example.com",
                "full_name": "Wrong Invite",
                "password": "securepassword123",
                "invite_code": "wrong-code",
                "accept_terms": True,
            },
        )
        assert rejected.status_code == 403

        accepted = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invited@example.com",
                "full_name": "Invited Merchant",
                "password": "securepassword123",
                "invite_code": "private-beta-code-123",
                "accept_terms": True,
            },
        )
        assert accepted.status_code == 200
    finally:
        settings.BETA_INVITE_CODE = previous_invite


def test_metrics_require_configured_bearer_token(client):
    previous_token = settings.METRICS_TOKEN
    settings.METRICS_TOKEN = "test-metrics-token-with-at-least-32-bytes"
    try:
        assert client.get("/metrics").status_code == 404
        authorized = client.get(
            "/metrics",
            headers={"Authorization": f"Bearer {settings.METRICS_TOKEN}"},
        )
        assert authorized.status_code == 200
        assert authorized.headers["content-type"].startswith("text/plain")
    finally:
        settings.METRICS_TOKEN = previous_token

def test_full_api_workflow(client):
    """Test user registration, login, store creation, api key auth, product ingest, and search."""

    live_response = client.get("/health/live")
    assert live_response.status_code == 200
    assert live_response.json()["release"] == settings.RELEASE_SHA

    demo_response = client.post(
        "/api/v1/demo/search",
        json={"query": "something to keep drinks cold under 40", "limit": 3},
    )
    assert demo_response.status_code == 200
    demo_data = demo_response.json()
    assert demo_data["applied_filters"]["price_max"] == 40.0
    assert demo_data["products"]
    assert all(product["price"] <= 40 for product in demo_data["products"])
    assert demo_data["products"][0]["id"] == "bottle-insulated"
    
    # 1. Register a new user
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "merchant@example.com",
            "full_name": "Merchant Joe",
            "password": "securepassword123",
            "accept_terms": True,
        }
    )
    assert register_response.status_code == 200
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
    
    # 4. Generate an API key. The secret is returned once and never listed again.
    key_response = client.post(
        f"/api/v1/stores/{store_id}/keys",
        json={"name": "Test Ingest Key", "scopes": ["search", "ingest"]},
        headers=headers,
    )
    assert key_response.status_code == 200
    api_key_str = key_response.json()["key"]
    listed_keys = client.get(f"/api/v1/stores/{store_id}/keys", headers=headers)
    assert listed_keys.status_code == 200
    assert "key" not in listed_keys.json()[0]
    
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

    filtered_search_response = client.post(
        "/api/v1/search",
        headers=ingest_headers,
        json={
            "query": "insulated water bottle under 50",
            "limit": 5,
            "filters": {"price_max": 50},
        },
    )
    assert filtered_search_response.status_code == 200
    filtered_results = filtered_search_response.json()
    assert filtered_results
    assert all(result["metadata"]["price"] <= 50 for result in filtered_results)
    
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

    # 10. A second merchant cannot access this store or its resources.
    other_register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "other@example.com",
            "full_name": "Other Merchant",
            "password": "securepassword456",
            "accept_terms": True,
        },
    )
    assert other_register.status_code == 200
    other_login = client.post(
        "/api/v1/auth/token",
        data={"username": "other@example.com", "password": "securepassword456"},
    )
    assert other_login.status_code == 200
    other_headers = {
        "Authorization": f"Bearer {other_login.json()['access_token']}"
    }

    assert client.get(f"/api/v1/stores/{store_id}", headers=other_headers).status_code == 404
    assert client.get(
        f"/api/v1/products/store/{store_id}", headers=other_headers
    ).status_code == 404
    assert client.get(
        f"/api/v1/analytics/{store_id}", headers=other_headers
    ).status_code == 404
    assert client.get(
        f"/api/v1/stores/{store_id}/keys", headers=other_headers
    ).status_code == 404
    assert all(
        store["id"] != store_id
        for store in client.get("/api/v1/stores/", headers=other_headers).json()
    )

    delete_response = client.delete(f"/api/v1/stores/{store_id}", headers=headers)
    assert delete_response.status_code == 200
    assert app.state.search_engine._get_store_collection(store_id).count() == 0
    db = TestingSessionLocal()
    assert db.query(Product).filter(Product.store_id == store_id).count() == 0
    assert db.query(SearchQueryLog).filter(SearchQueryLog.store_id == store_id).count() == 0
    db.close()


def test_account_deletion_requires_password_and_removes_owned_data(client):
    registration = client.post(
        "/api/v1/auth/register",
        json={
            "email": "delete-me@example.com",
            "full_name": "Delete Me",
            "password": "securepassword123",
            "accept_terms": True,
        },
    )
    assert registration.status_code == 200

    login = client.post(
        "/api/v1/auth/token",
        data={"username": "delete-me@example.com", "password": "securepassword123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    store = client.post(
        "/api/v1/stores/",
        headers=headers,
        json={"name": "Disposable Store", "platform": "custom"},
    )
    assert store.status_code == 200
    store_id = store.json()["id"]
    app.state.search_engine._get_store_collection(store_id).add(
        ids=["delete-vector"],
        embeddings=[[0.0] * 384],
        documents=["temporary product"],
        metadatas=[{"store_id": store_id}],
    )

    rejected = client.request(
        "DELETE",
        "/api/v1/auth/me",
        headers=headers,
        json={"password": "wrong-password"},
    )
    assert rejected.status_code == 403

    deleted = client.request(
        "DELETE",
        "/api/v1/auth/me",
        headers=headers,
        json={"password": "securepassword123"},
    )
    assert deleted.status_code == 200
    assert client.post(
        "/api/v1/auth/token",
        data={"username": "delete-me@example.com", "password": "securepassword123"},
    ).status_code == 401
    assert app.state.search_engine._get_store_collection(store_id).count() == 0
