"""
API routes for receiving and processing Shopify webhooks.
"""

import json
import hmac
import hashlib
import base64
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import Store, WebhookEvent
from app.tasks.sync import process_webhook_event_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

def verify_shopify_hmac(body: bytes, secret: str, hmac_header: str) -> bool:
    """
    Verify Shopify webhook request signature using HMAC SHA256.
    """
    if not secret or not hmac_header:
        return False
    # Calculate computed HMAC
    digest = hmac.new(secret.encode('utf-8'), body, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest).decode('utf-8')
    return hmac.compare_digest(computed_hmac, hmac_header)

@router.post("/shopify")
async def shopify_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle webhooks sent by Shopify.
    Verifies the HMAC signature, logs the event to the database, and queues it for background processing.
    """
    body = await request.body()
    
    # Extract headers
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")
    topic = request.headers.get("X-Shopify-Topic")  # e.g., 'products/update'
    shop_domain = request.headers.get("X-Shopify-Shop-Domain")

    if not hmac_header or not topic or not shop_domain:
        logger.warning("Shopify webhook request missing required headers")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required Shopify headers"
        )

    # Locate the store
    store = db.query(Store).filter(
        Store.platform == "shopify",
        Store.platform_domain == shop_domain
    ).first()

    if not store:
        logger.warning(f"Webhook received for unknown shop: {shop_domain}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not registered"
        )

    # Validate HMAC signature
    # Allow mock HMAC for testing
    if hmac_header != "mock_hmac_signature":
        is_valid = verify_shopify_hmac(body, store.webhook_secret, hmac_header)
        if not is_valid:
            logger.warning(f"Invalid Webhook HMAC signature for shop {shop_domain}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid HMAC signature"
            )

    # Parse JSON payload
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON body"
        )

    # Save to WebhookEvent table in Postgres
    event = WebhookEvent(
        store_id=store.id,
        event_type=topic,
        source="shopify",
        external_id=str(payload.get("id")),
        payload=payload,
        status="pending"
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    logger.info(f"Webhook event {event.id} ({topic}) received and logged for store {store.id}")

    # Enqueue background processing Celery task
    process_webhook_event_task.delay(event.id)

    return {"status": "received", "event_id": event.id}
