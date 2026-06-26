"""
API routes for Shopify OAuth authentication and setup.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db, get_redis
from app.models.database import Store
from app.integrations.shopify import (
    get_shopify_auth_url,
    exchange_shopify_code,
    encrypt_token,
    register_shopify_webhooks
)
from app.tasks.sync import sync_shopify_products_task

router = APIRouter(prefix="/shopify", tags=["shopify_auth"])

@router.get("/authorize")
def shopify_authorize(
    shop: str = Query(..., description="The shop name or shop domain (e.g., store-name.myshopify.com)"),
    user_id: str = Query(..., description="The ID of the user initiating the store connection"),
    db: Session = Depends(get_db)
):
    """
    Redirect the merchant to Shopify for authorization.
    """
    # Clean the shop domain name
    shop_domain = shop.strip().lower()
    if not shop_domain.endswith(".myshopify.com") and "." not in shop_domain:
        shop_domain = f"{shop_domain}.myshopify.com"

    # Generate a unique state token to prevent CSRF
    state_token = f"{user_id}_{uuid.uuid4().hex}"
    
    # Save the state in Redis with 10-minute expiry
    redis_client = get_redis()
    if redis_client:
        redis_client.set(f"shopify_state:{state_token}", "valid", ex=600)

    # Build auth URL
    auth_url = get_shopify_auth_url(shop_domain, state_token)
    
    return RedirectResponse(url=auth_url)

@router.get("/callback")
def shopify_callback(
    code: str = Query(..., description="Shopify auth code"),
    shop: str = Query(..., description="Shop domain"),
    state: str = Query(..., description="CSRF state token"),
    db: Session = Depends(get_db)
):
    """
    Callback URL where Shopify redirects the merchant with an authorization code.
    Exchanges the code for a permanent access token, encrypts it, and triggers product sync.
    """
    # Clean shop domain
    shop_domain = shop.strip().lower()
    if not shop_domain.endswith(".myshopify.com") and "." not in shop_domain:
        shop_domain = f"{shop_domain}.myshopify.com"

    # Verify the state token exists in Redis
    redis_client = get_redis()
    if redis_client:
        state_exists = redis_client.exists(f"shopify_state:{state}")
        if not state_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state token. Please restart authorization."
            )
        # Delete state token from Redis once verified
        redis_client.delete(f"shopify_state:{state}")

    # Extract user_id from state (format: {user_id}_{uuid})
    try:
        user_id = state.split("_")[0]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed state token."
        )

    # Exchange authorization code for access token
    try:
        access_token = exchange_shopify_code(shop_domain, code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to retrieve access token from Shopify: {str(e)}"
        )

    # Check if a store already exists for this shop domain
    store = db.query(Store).filter(
        Store.platform == "shopify",
        Store.platform_domain == shop_domain
    ).first()

    # Register webhooks and get the webhook secret (HMAC signature key)
    webhook_secret = register_shopify_webhooks(shop_domain, access_token, settings.public_api_base_url)

    # Encrypt access token
    encrypted_token = encrypt_token(access_token)

    if store:
        # Update existing store details
        store.api_key_encrypted = encrypted_token
        store.webhook_secret = webhook_secret
        store.is_active = True
        store.index_status = "pending"
    else:
        # Create a new Store record in PostgreSQL
        store = Store(
            name=shop_domain.split(".")[0].replace("-", " ").title(),
            platform="shopify",
            platform_store_id=None,  # We can update this when syncing products
            platform_domain=shop_domain,
            api_key_encrypted=encrypted_token,
            webhook_secret=webhook_secret,
            is_active=True,
            index_status="pending"
        )
        db.add(store)

    db.commit()
    db.refresh(store)

    # Trigger Celery product sync task in the background
    sync_shopify_products_task.delay(store.id)

    return {
        "status": "success",
        "message": "Store authorized and product sync initiated.",
        "store_id": store.id,
        "platform_domain": store.platform_domain,
        "index_status": store.index_status
    }
