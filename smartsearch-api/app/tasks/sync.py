"""
Background Celery tasks for product synchronization and webhook processing.
"""

import logging
import os
from datetime import datetime
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.database import Store, Product, WebhookEvent
from app.integrations.shopify import decrypt_token, fetch_shopify_products
from app.core.config import settings

logger = logging.getLogger(__name__)

_search_engine = None

def get_search_engine():
    """Get or initialize the SemanticSearchEngine singleton for background task workers."""
    global _search_engine
    if _search_engine is None:
        import sys
        if "pytest" in sys.modules:
            try:
                from app.main import app
                if hasattr(app, "state") and hasattr(app.state, "search_engine"):
                    _search_engine = app.state.search_engine
            except Exception:
                pass
        
        if _search_engine is None:
            from app.core.search_engine import SemanticSearchEngine
            path = os.path.abspath(settings.CHROMA_DB_PATH)
            os.makedirs(path, exist_ok=True)
            _search_engine = SemanticSearchEngine(db_path=path)
    return _search_engine

@celery_app.task(name="app.tasks.sync.sync_shopify_products_task")
def sync_shopify_products_task(store_id: str) -> None:
    """
    Background task to sync all products from a merchant's Shopify store.
    """
    logger.info(f"Starting product sync for store {store_id}")
    db = SessionLocal()
    try:
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            logger.error(f"Store {store_id} not found")
            return
            
        store.index_status = "indexing"
        store.index_progress_percent = 10
        db.commit()

        # Decrypt token
        access_token = decrypt_token(store.api_key_encrypted)
        if not access_token:
            logger.error(f"No access token found/decrypted for store {store_id}")
            store.index_status = "error"
            db.commit()
            return

        # Fetch products
        shopify_products = fetch_shopify_products(store.platform_domain, access_token)
        store.total_product_count = len(shopify_products)
        store.index_progress_percent = 30
        db.commit()

        # Transform and save products
        products_to_index = []
        indexed_count = 0
        
        for idx, shopify_product in enumerate(shopify_products):
            ext_id = str(shopify_product["id"])
            title = shopify_product["title"]
            desc = shopify_product.get("body_html") or ""
            
            # Extract price and inventory
            variants = shopify_product.get("variants", [])
            price = None
            inventory = 0
            if variants:
                price = float(variants[0].get("price")) if variants[0].get("price") else None
                inventory = int(variants[0].get("inventory_quantity") or 0)
                
            # Extract image
            images = shopify_product.get("images", [])
            image_url = images[0].get("src") if images else None
            
            brand = shopify_product.get("vendor")
            category = shopify_product.get("product_type")

            # Check if exists in db
            product = db.query(Product).filter(Product.store_id == store_id, Product.id == ext_id).first()
            if not product:
                product = Product(id=ext_id, store_id=store_id)
                db.add(product)
                
            product.title = title
            product.description = desc
            product.price = price
            product.inventory_count = inventory
            product.image_url = image_url
            product.brand = brand
            product.category = category
            product.is_active = True
            product.product_metadata = shopify_product
            
            # Format product dictionary for ChromaDB
            products_to_index.append({
                "id": ext_id,
                "title": title,
                "description": desc,
                "price": price,
                "category": category,
                "brand": brand,
                "image_url": image_url,
                "is_active": True
            })
            
            indexed_count += 1
            
        db.commit()

        # Index in ChromaDB
        if products_to_index:
            se = get_search_engine()
            se.index_store_products(store_id=store_id, products=products_to_index)

        # Update store status
        store.index_status = "ready"
        store.index_progress_percent = 100
        store.indexed_product_count = indexed_count
        store.last_sync_at = datetime.utcnow()
        db.commit()
        logger.info(f"Successfully synced {indexed_count} products for store {store_id}")
        
    except Exception as e:
        logger.exception(f"Error syncing products for store {store_id}: {e}")
        db.rollback()
        store = db.query(Store).filter(Store.id == store_id).first()
        if store:
            store.index_status = "error"
            db.commit()
    finally:
        db.close()

@celery_app.task(name="app.tasks.sync.process_webhook_event_task")
def process_webhook_event_task(event_id: str) -> None:
    """
    Background task to process a single Shopify webhook event.
    """
    logger.info(f"Processing webhook event {event_id}")
    db = SessionLocal()
    try:
        event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
        if not event:
            logger.error(f"WebhookEvent {event_id} not found")
            return
            
        event.status = "processing"
        db.commit()

        store_id = event.store_id
        payload = event.payload
        event_type = event.event_type  # products/create, products/update, products/delete
        
        se = get_search_engine()

        if event_type in ("products/create", "products/update"):
            ext_id = str(payload["id"])
            title = payload["title"]
            desc = payload.get("body_html") or ""
            
            # Extract price and inventory
            variants = payload.get("variants", [])
            price = None
            inventory = 0
            if variants:
                price = float(variants[0].get("price")) if variants[0].get("price") else None
                inventory = int(variants[0].get("inventory_quantity") or 0)
                
            # Extract image
            images = payload.get("images", [])
            image_url = images[0].get("src") if images else None
            
            brand = payload.get("vendor")
            category = payload.get("product_type")

            # Update PostgreSQL
            product = db.query(Product).filter(Product.store_id == store_id, Product.id == ext_id).first()
            if not product:
                product = Product(id=ext_id, store_id=store_id)
                db.add(product)
                
            product.title = title
            product.description = desc
            product.price = price
            product.inventory_count = inventory
            product.image_url = image_url
            product.brand = brand
            product.category = category
            product.is_active = True
            product.product_metadata = payload
            db.commit()

            # Index in ChromaDB
            product_dict = {
                "id": ext_id,
                "title": title,
                "description": desc,
                "price": price,
                "category": category,
                "brand": brand,
                "image_url": image_url,
                "is_active": True
            }
            se.index_store_products(store_id=store_id, products=[product_dict])
            logger.info(f"Webhook indexed product {ext_id} for store {store_id}")
            
        elif event_type == "products/delete":
            ext_id = str(payload["id"])
            
            # Delete from PostgreSQL
            product = db.query(Product).filter(Product.store_id == store_id, Product.id == ext_id).first()
            if product:
                db.delete(product)
                db.commit()
                
            # Delete from ChromaDB
            se.delete_store_products(store_id=store_id, ids=[ext_id])
            logger.info(f"Webhook deleted product {ext_id} for store {store_id}")

        # Update webhook status
        event.status = "completed"
        event.processed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        logger.exception(f"Error processing webhook event {event_id}: {e}")
        db.rollback()
        event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
        if event:
            event.status = "failed"
            event.error_message = str(e)
            db.commit()
    finally:
        db.close()

@celery_app.task(name="app.tasks.sync.process_uploaded_file_task")
def process_uploaded_file_task(store_id: str, file_key: str, file_type: str) -> None:
    """
    Background task to process an uploaded CSV or JSON file containing products.
    """
    logger.info(f"Starting file processing for store {store_id}, file: {file_key}")
    db = SessionLocal()
    try:
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            logger.error(f"Store {store_id} not found")
            return
            
        store.index_status = "indexing"
        store.index_progress_percent = 10
        db.commit()

        # Download file content
        from app.utils.storage import storage_client
        file_bytes = storage_client.download_file(file_key)
        store.index_progress_percent = 30
        db.commit()

        # Parse file content
        if file_type.lower() == "csv":
            from app.utils.csv_parser import parse_products_csv
            parsed_products = parse_products_csv(file_bytes)
        elif file_type.lower() == "json":
            from app.utils.json_parser import parse_products_json
            parsed_products = parse_products_json(file_bytes)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
            
        store.total_product_count = len(parsed_products)
        store.index_progress_percent = 50
        db.commit()

        # Transform and save products
        products_to_index = []
        indexed_count = 0
        
        for idx, item in enumerate(parsed_products):
            ext_id = str(item["id"])
            title = item["title"]
            desc = item.get("description") or ""
            price = item.get("price")
            inventory = item.get("inventory_count", 0)
            image_url = item.get("image_url")
            product_url = item.get("product_url")
            brand = item.get("brand")
            category = item.get("category")
            is_active = item.get("is_active", True)
            
            # Check if exists in db
            product = db.query(Product).filter(Product.store_id == store_id, Product.id == ext_id).first()
            if not product:
                product = Product(id=ext_id, store_id=store_id)
                db.add(product)
                
            product.title = title
            product.description = desc
            product.price = price
            product.inventory_count = inventory
            product.image_url = image_url
            product.product_url = product_url
            product.brand = brand
            product.category = category
            product.is_active = is_active
            product.product_metadata = item.get("product_metadata")
            
            # Format product dictionary for ChromaDB
            products_to_index.append({
                "id": ext_id,
                "title": title,
                "description": desc,
                "price": price,
                "category": category,
                "brand": brand,
                "image_url": image_url,
                "is_active": is_active
            })
            
            indexed_count += 1
            
        db.commit()

        # Index in ChromaDB
        if products_to_index:
            se = get_search_engine()
            se.index_store_products(store_id=store_id, products=products_to_index)

        # Update store status
        store.index_status = "ready"
        store.index_progress_percent = 100
        store.indexed_product_count = indexed_count
        store.last_sync_at = datetime.utcnow()
        db.commit()
        logger.info(f"Successfully processed and indexed {indexed_count} products for store {store_id}")
        
    except Exception as e:
        logger.exception(f"Error processing uploaded file for store {store_id}: {e}")
        db.rollback()
        store = db.query(Store).filter(Store.id == store_id).first()
        if store:
            store.index_status = "error"
            db.commit()
    finally:
        db.close()

