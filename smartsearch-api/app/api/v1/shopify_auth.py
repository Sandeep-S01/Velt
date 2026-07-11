"""
API routes for Shopify OAuth authentication and setup.
"""

import json
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
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
    ,normalize_shop_domain
    ,verify_shopify_oauth_hmac
)
from app.tasks.sync import sync_shopify_products_task
from app.utils.security import get_current_active_user

router = APIRouter(prefix="/shopify", tags=["shopify_auth"])
_test_oauth_states: dict[str, str] = {}

@router.get("/authorize")
def shopify_authorize(
    shop: str = Query(..., description="The shop name or shop domain (e.g., store-name.myshopify.com)"),
    current_user=Depends(get_current_active_user),
):
    """
    Redirect the merchant to Shopify for authorization.
    """
    # Clean the shop domain name
    try:
        shop_domain = normalize_shop_domain(shop)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Generate a unique state token to prevent CSRF
    state_token = secrets.token_urlsafe(32)
    state_data = json.dumps({"user_id": current_user.id, "shop": shop_domain})
    
    # Save the state in Redis with 10-minute expiry
    redis_client = get_redis()
    if redis_client:
        try:
            redis_client.set(f"shopify_state:{state_token}", state_data, ex=600)
        except Exception as exc:
            if not settings.TESTING:
                raise HTTPException(
                    status_code=503,
                    detail="OAuth state service unavailable",
                ) from exc
            _test_oauth_states[state_token] = state_data
    elif settings.TESTING:
        _test_oauth_states[state_token] = state_data
    else:
        raise HTTPException(status_code=503, detail="OAuth state service unavailable")

    # Build auth URL
    auth_url = get_shopify_auth_url(shop_domain, state_token)
    
    return RedirectResponse(url=auth_url)

@router.get("/callback")
def shopify_callback(
    code: str = Query(..., description="Shopify auth code"),
    shop: str = Query(..., description="Shop domain"),
    state: str = Query(..., description="CSRF state token"),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Callback URL where Shopify redirects the merchant with an authorization code.
    Exchanges the code for a permanent access token, encrypts it, and triggers product sync.
    """
    # Clean shop domain
    try:
        shop_domain = normalize_shop_domain(shop)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not verify_shopify_oauth_hmac(dict(request.query_params)):
        raise HTTPException(status_code=401, detail="Invalid Shopify callback signature")

    # Verify the state token exists in Redis
    redis_client = get_redis()
    state_key = f"shopify_state:{state}"
    if redis_client:
        try:
            state_data = redis_client.get(state_key)
            if state_data:
                redis_client.delete(state_key)
        except Exception as exc:
            if not settings.TESTING:
                raise HTTPException(
                    status_code=503,
                    detail="OAuth state service unavailable",
                ) from exc
            state_data = _test_oauth_states.pop(state, None)
    elif settings.TESTING:
        state_data = _test_oauth_states.pop(state, None)
    else:
        raise HTTPException(status_code=503, detail="OAuth state service unavailable")
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
    state_payload = json.loads(state_data)
    if state_payload.get("shop") != shop_domain:
        raise HTTPException(status_code=400, detail="OAuth state shop mismatch")
    owner_user_id = state_payload["user_id"]

    # Exchange authorization code for access token
    try:
        access_token = exchange_shopify_code(shop_domain, code)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        detail="Failed to retrieve Shopify access token"
        )

    # Check if a store already exists for this shop domain
    store = db.query(Store).filter(
        Store.platform == "shopify",
        Store.platform_domain == shop_domain,
        Store.owner_user_id == owner_user_id,
    ).first()

    # Register webhooks and get the webhook secret (HMAC signature key)
    register_shopify_webhooks(shop_domain, access_token, settings.public_api_base_url)

    # Encrypt access token
    encrypted_token = encrypt_token(access_token)

    if store:
        # Update existing store details
        store.api_key_encrypted = encrypted_token
        store.is_active = True
        store.index_status = "pending"
    else:
        # Create a new Store record in PostgreSQL
        store = Store(
            name=shop_domain.split(".")[0].replace("-", " ").title(),
            platform="shopify",
            platform_store_id=None,  # We can update this when syncing products
            platform_domain=shop_domain,
            owner_user_id=owner_user_id,
            api_key_encrypted=encrypted_token,
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
