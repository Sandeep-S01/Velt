"""
Integration tests for CSV/JSON file upload, widget search/autocomplete, and click analytics.
"""

import pytest
from fastapi.testclient import TestClient
import os
import shutil
import io

import app.core.database
# Stub out database and Redis connections on app lifespan to prevent starting them up
app.core.database.create_tables = lambda: None
app.core.database.get_redis = lambda: None

from app.main import app
from app.core.database import get_db, Base
from app.core.search_engine import SemanticSearchEngine
from app.models.database import Store, Product, SearchQueryLog, APIKey, User
from tests.conftest import engine, TestingSessionLocal
from app.core.config import settings

TEST_CHROMA_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_widget_chroma_db"))
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

def test_upload_and_widget_flow(test_client):
    """Test full flow: user register -> create store -> upload CSV -> widget query -> log click -> fetch analytics."""
    
    # 1. Register a new user
    register_response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner@store.com",
            "full_name": "Store Owner",
            "password": "ownerpassword123"
        }
    )
    assert register_response.status_code == 200
    user_id = register_response.json()["id"]
    
    # 2. Login to get JWT
    login_response = test_client.post(
        "/api/v1/auth/token",
        data={
            "username": "owner@store.com",
            "password": "ownerpassword123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Store
    store_response = test_client.post(
        "/api/v1/stores/",
        json={
            "name": "Widget Emporium",
            "platform": "custom",
            "is_active": True,
            "sync_frequency_hours": 24
        },
        headers=user_headers
    )
    assert store_response.status_code == 200
    store_id = store_response.json()["id"]

    # 4. Generate an API Key for this store manually in DB for testing
    db = TestingSessionLocal()
    api_key_str = "ss_live_widget_test_api_key_456"
    api_key_obj = APIKey(
        key=api_key_str,
        store_id=store_id,
        name="Widget Test Key",
        is_active=True
    )
    db.add(api_key_obj)
    db.commit()
    db.close()

    api_headers = {"X-API-Key": api_key_str}

    # 5. Upload CSV file using the upload API
    csv_content = (
        "sku,product_name,desc,price,brand,inventory\n"
        "item_1,Wireless Bluetooth Headset,Noise-canceling over-ear wireless headphones.,89.99,SoundWave,200\n"
        "item_2,Smart LED Light Bulb,RGB color-changing smart bulb compatible with voice assistants.,15.50,GlowTech,50\n"
    )
    csv_file = io.BytesIO(csv_content.encode("utf-8"))
    
    upload_response = test_client.post(
        "/api/v1/upload",
        data={"store_id": store_id},
        files={"file": ("products.csv", csv_file, "text/csv")},
        headers=api_headers
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["status"] == "success"
    
    # Verify products exist in Postgres
    db = TestingSessionLocal()
    db_products = db.query(Product).filter(Product.store_id == store_id).all()
    assert len(db_products) == 2
    assert any(p.title == "Wireless Bluetooth Headset" for p in db_products)
    
    # Verify store progress updated
    store = db.query(Store).filter(Store.id == store_id).first()
    assert store.index_status == "ready"
    assert store.indexed_product_count == 2
    db.close()

    # 6. Test Widget Config Endpoint
    config_resp = test_client.get(f"/api/v1/widget/config/{store_id}")
    assert config_resp.status_code == 200
    assert config_resp.json()["primary_color"] == "#4F46E5"

    # 7. Test Widget Search Endpoint
    search_resp = test_client.post(
        "/api/v1/widget/search",
        json={"store_id": store_id, "query": "listening to music without cables", "limit": 2}
    )
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) >= 1
    assert results[0]["id"] == "item_1"
    assert results[0]["title"] == "Wireless Bluetooth Headset"

    # 8. Test Autocomplete Endpoint
    autocomplete_resp = test_client.get(
        f"/api/v1/widget/autocomplete?store_id={store_id}&query=wireless"
    )
    assert autocomplete_resp.status_code == 200
    suggestions = autocomplete_resp.json()["suggestions"]
    assert "Wireless Bluetooth Headset" in suggestions

    # 9. Test Click Tracking Analytics
    # Check that a search query log was recorded
    db = TestingSessionLocal()
    query_log = db.query(SearchQueryLog).filter(SearchQueryLog.store_id == store_id).first()
    assert query_log is not None
    assert query_log.query == "listening to music without cables"
    query_log_id = query_log.id
    db.close()

    # Log click event
    click_resp = test_client.post(
        "/api/v1/analytics/click",
        json={
            "query_log_id": query_log_id,
            "clicked_product_id": "item_1"
        }
    )
    assert click_resp.status_code == 200
    assert click_resp.json()["clicked_product_id"] == "item_1"

    # Verify Click in DB
    db = TestingSessionLocal()
    updated_query_log = db.query(SearchQueryLog).filter(SearchQueryLog.id == query_log_id).first()
    assert updated_query_log.clicked_product_id == "item_1"
    db.close()

    # 10. Fetch dashboard analytics using dashboard authenticated user session
    analytics_resp = test_client.get(
        f"/api/v1/analytics/{store_id}",
        headers=user_headers
    )
    assert analytics_resp.status_code == 200
    analytics_data = analytics_resp.json()
    assert analytics_data["total_searches"] == 1
    assert analytics_data["click_through_rate"] == 1.0
    assert analytics_data["top_queries"][0]["query"] == "listening to music without cables"
    assert analytics_data["top_clicked_products"][0]["title"] == "Wireless Bluetooth Headset"
