import os
import pandas as pd
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, create_tables
from app.models.database import User, Store, APIKey, Product
from app.services.user_service import pwd_context
from app.core.search_engine import SemanticSearchEngine

def seed():
    # Make sure tables exist
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Check if user already exists
        user = db.query(User).filter(User.email == "admin@example.com").first()
        if not user:
            print("Creating seed user admin@example.com...")
            hashed_password = pwd_context.hash("Password123!")
            user = User(
                email="admin@example.com",
                password_hash=hashed_password,
                full_name="Admin User",
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created user with ID: {user.id}")
        else:
            print(f"User admin@example.com already exists with ID: {user.id}")

        # Check if store already exists
        store_id = "boutique-jewels-store"
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            print("Creating seed store Boutique Jewels...")
            store = Store(
                id=store_id,
                name="Boutique Jewels",
                platform="custom",
                platform_store_id="custom_store_1",
                is_active=True,
                widget_config={
                    "theme": "light",
                    "primary_color": "#4F46E5",
                    "position": "bottom-right",
                    "placeholder_text": "Search for products...",
                    "show_filters": True,
                    "show_price": True,
                    "show_rating": True,
                    "results_per_page": 10,
                    "enable_autocomplete": True,
                    "enable_voice_search": False
                },
                search_config={
                    "min_score_threshold": 0.25,
                    "max_results": 50,
                    "enable_synonyms": True,
                    "enable_spell_check": True,
                    "fallback_to_keyword": True,
                    "boost_recent": False,
                    "boost_popular": False
                }
            )
            db.add(store)
            db.commit()
            db.refresh(store)
            print(f"Created store: {store.name}")
        else:
            print(f"Store Boutique Jewels already exists with ID: {store.id}")

        # Check if API key already exists
        api_key = db.query(APIKey).filter(APIKey.store_id == store_id).first()
        if not api_key:
            print("Creating seed API key...")
            api_key = APIKey(
                key="ss_key_boutique_jewels_12345",
                store_id=store_id,
                name="Default Sandbox Key",
                is_active=True
            )
            db.add(api_key)
            db.commit()
            print("Created API key: ss_key_boutique_jewels_12345")
        else:
            print(f"API key already exists: {api_key.key}")

        # Load and ingest sample products
        csv_path = "data/sample_products.csv"
        if os.path.exists(csv_path):
            print("Seeding sample products...")
            df = pd.read_csv(csv_path)
            products_list = []
            for idx, row in df.iterrows():
                prod_id = str(row['id'])
                # Check if product already exists in SQLite
                db_prod = db.query(Product).filter(Product.id == prod_id, Product.store_id == store_id).first()
                
                # Setup product properties
                product_data = {
                    "id": prod_id,
                    "store_id": store_id,
                    "title": str(row['title']),
                    "description": str(row['description']),
                    "price": float(row['price']),
                    "category": str(row['category']),
                    "is_active": True
                }
                
                if not db_prod:
                    db_prod = Product(**product_data)
                    db.add(db_prod)
                else:
                    for k, v in product_data.items():
                        setattr(db_prod, k, v)
                
                products_list.append(product_data)
            
            db.commit()
            print(f"Seeded {len(products_list)} products in SQLite.")

            # Ingest in ChromaDB
            chroma_path = os.path.join(os.path.dirname(__file__), "app", "chroma_db")
            os.makedirs(chroma_path, exist_ok=True)
            search_engine = SemanticSearchEngine(db_path=chroma_path)
            search_engine.index_store_products(store_id=store_id, products=products_list)
            print(f"Indexed {len(products_list)} products in ChromaDB at {chroma_path}.")
            
            # Update store count
            store.indexed_product_count = len(products_list)
            store.total_product_count = len(products_list)
            store.index_status = "ready"
            db.commit()
        else:
            print("Error: data/sample_products.csv not found!")

        print("Seeding completed successfully!")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed()
