"""
Shopify integration helper module.
Handles OAuth flow, encrypted token storage, product syncing, and webhooks.
"""

import base64
import os
import json
import urllib.request
import urllib.error
import hashlib
from typing import Dict, Any, List
from cryptography.fernet import Fernet
from app.core.config import settings

# Deriving a Fernet key from settings.SECRET_KEY to keep things clean if no explicit key is provided
_key = os.getenv("SHOPIFY_ENCRYPTION_KEY")
if not _key:
    # Fernet keys must be 32 url-safe base64-encoded bytes
    h = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    _key = base64.urlsafe_b64encode(h).decode()

_fernet = Fernet(_key.encode())

def encrypt_token(token: str) -> str:
    """Encrypt Shopify access token."""
    if not token:
        return ""
    return _fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted: str) -> str:
    """Decrypt Shopify access token."""
    if not encrypted:
        return ""
    try:
        return _fernet.decrypt(encrypted.encode()).decode()
    except Exception:
        return ""

def get_shopify_auth_url(shop_domain: str, state: str) -> str:
    """
    Generate Shopify OAuth authorization URL.
    """
    # Clean shop domain (e.g., store.myshopify.com)
    shop = shop_domain.strip().lower()
    if not shop.endswith(".myshopify.com") and "." not in shop:
        shop = f"{shop}.myshopify.com"
        
    query_params = urllib.parse.urlencode({
        "client_id": settings.SHOPIFY_CLIENT_ID,
        "scope": settings.SHOPIFY_SCOPES,
        "redirect_uri": settings.shopify_redirect_uri,
        "state": state
    })
    return f"https://{shop}/admin/oauth/authorize?{query_params}"

def exchange_shopify_code(shop_domain: str, code: str) -> str:
    """
    Exchange temporary Shopify authorization code for an access token.
    """
    shop = shop_domain.strip().lower()
    if not shop.endswith(".myshopify.com") and "." not in shop:
        shop = f"{shop}.myshopify.com"

    url = f"https://{shop}/admin/oauth/access_token"
    data = json.dumps({
        "client_id": settings.SHOPIFY_CLIENT_ID,
        "client_secret": settings.SHOPIFY_CLIENT_SECRET,
        "code": code
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    # For local testing, allow bypassing real Shopify call if configured to mock
    if settings.SHOPIFY_CLIENT_ID == "mock_shopify_client_id" or code.startswith("mock_"):
        return f"mock_access_token_for_{shop_domain}"

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode())
            return res_data["access_token"]
    except urllib.error.URLError as e:
        raise Exception(f"Failed to exchange Shopify authorization code: {e}")

def register_shopify_webhooks(shop_domain: str, access_token: str, webhook_base_url: str) -> str:
    """
    Register product webhooks (create, update, delete) for a Shopify store.
    Returns the webhook secret key if returned or generated.
    """
    # In Shopify, we register webhooks individually.
    # Topic list: products/create, products/update, products/delete
    topics = ["products/create", "products/update", "products/delete"]
    
    # We will generate a webhook secret for this store/webhook setup to verify requests
    webhook_secret = hashlib.sha256(f"{shop_domain}_{access_token}".encode()).hexdigest()

    # For testing or mock setup, bypass actual Shopify registration
    if access_token.startswith("mock_"):
        return webhook_secret

    for topic in topics:
        url = f"https://{shop_domain}/admin/api/2024-01/webhooks.json"
        webhook_address = f"{webhook_base_url.rstrip('/')}/api/v1/webhooks/shopify"
        payload = {
            "webhook": {
                "topic": topic,
                "address": webhook_address,
                "format": "json"
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": access_token
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                pass
        except urllib.error.URLError as e:
            # We can log warnings but continue. In sandbox environments this might fail, so we log.
            print(f"Warning: Failed to register Shopify webhook for topic {topic}: {e}")

    return webhook_secret

def fetch_shopify_products(shop_domain: str, access_token: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch products from Shopify REST Admin API.
    """
    if access_token.startswith("mock_"):
        # Return mock product payload for local testing
        return [
            {
                "id": 123456,
                "title": "Mock Shopify Product A",
                "body_html": "This is a great mockup product from Shopify store",
                "vendor": "ShopifyMock",
                "product_type": "Test",
                "images": [{"src": "https://example.com/mock-a.jpg"}],
                "variants": [{"price": "19.99", "inventory_quantity": 100}]
            },
            {
                "id": 789012,
                "title": "Mock Shopify Product B",
                "body_html": "Another awesome product description",
                "vendor": "ShopifyMock",
                "product_type": "Test",
                "images": [{"src": "https://example.com/mock-b.jpg"}],
                "variants": [{"price": "49.99", "inventory_quantity": 5}]
            }
        ]

    url = f"https://{shop_domain}/admin/api/2024-01/products.json?limit={limit}"
    req = urllib.request.Request(
        url,
        headers={"X-Shopify-Access-Token": access_token}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode())
            return res_data.get("products", [])
    except urllib.error.URLError as e:
        raise Exception(f"Failed to fetch Shopify products: {e}")
