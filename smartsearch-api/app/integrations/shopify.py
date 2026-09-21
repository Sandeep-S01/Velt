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
import hmac
import re
import urllib.parse
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
SHOP_DOMAIN_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*\.myshopify\.com$")


def normalize_shop_domain(shop: str) -> str:
    domain = shop.strip().lower()
    if "." not in domain:
        domain = f"{domain}.myshopify.com"
    if not SHOP_DOMAIN_PATTERN.fullmatch(domain):
        raise ValueError("Invalid Shopify shop domain")
    return domain


def verify_shopify_oauth_hmac(params: dict[str, str]) -> bool:
    supplied_hmac = params.get("hmac", "")
    if not supplied_hmac or not settings.SHOPIFY_CLIENT_SECRET:
        return False
    message = "&".join(
        f"{key}={value}"
        for key, value in sorted(params.items())
        if key not in {"hmac", "signature"}
    )
    expected = hmac.new(
        settings.SHOPIFY_CLIENT_SECRET.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, supplied_hmac)

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
    shop = normalize_shop_domain(shop_domain)
        
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
    shop = normalize_shop_domain(shop_domain)

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
    if settings.TESTING and code.startswith("mock_"):
        return f"mock_access_token_for_{shop_domain}"

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode())
            return res_data["access_token"]
    except urllib.error.URLError as e:
        raise Exception(f"Failed to exchange Shopify authorization code: {e}")

def register_shopify_webhooks(shop_domain: str, access_token: str, webhook_base_url: str) -> None:
    """
    Register product webhooks (create, update, delete) for a Shopify store.
    Returns the webhook secret key if returned or generated.
    """
    # For testing or mock setup, bypass actual Shopify registration
    if settings.TESTING and access_token.startswith("mock_"):
        return

    mutation = """
        mutation CreateWebhook(
          $topic: WebhookSubscriptionTopic!,
          $subscription: WebhookSubscriptionInput!
        ) {
          webhookSubscriptionCreate(topic: $topic, webhookSubscription: $subscription) {
            webhookSubscription { id topic uri }
            userErrors { field message }
          }
        }
    """
    webhook_uri = f"{webhook_base_url.rstrip('/')}/api/v1/webhooks/shopify"
    for topic in ("PRODUCTS_CREATE", "PRODUCTS_UPDATE", "PRODUCTS_DELETE"):
        try:
            payload = _shopify_graphql_request(
                shop_domain,
                access_token,
                mutation,
                {"topic": topic, "subscription": {"uri": webhook_uri}},
            )
            user_errors = payload["webhookSubscriptionCreate"].get("userErrors") or []
            if user_errors:
                messages = "; ".join(error["message"] for error in user_errors)
                print(f"Warning: Failed to register Shopify webhook for {topic}: {messages}")
        except Exception as exc:
            # A failed subscription should not discard a completed OAuth connection.
            print(f"Warning: Failed to register Shopify webhook for {topic}: {exc}")

    return None

def fetch_shopify_products(shop_domain: str, access_token: str, limit: int = 250) -> List[Dict[str, Any]]:
    """
    Fetch and normalize all products from Shopify's GraphQL Admin API.
    """
    if settings.TESTING and access_token.startswith("mock_"):
        # Return mock product payload for local testing
        return [
            {
                "id": 123456,
                "handle": "mock-shopify-product-a",
                "status": "active",
                "title": "Mock Shopify Product A",
                "body_html": "This is a great mockup product from Shopify store",
                "vendor": "ShopifyMock",
                "product_type": "Test",
                "images": [{"src": "https://example.com/mock-a.jpg"}],
                "variants": [{"price": "19.99", "inventory_quantity": 100}]
            },
            {
                "id": 789012,
                "handle": "mock-shopify-product-b",
                "status": "active",
                "title": "Mock Shopify Product B",
                "body_html": "Another awesome product description",
                "vendor": "ShopifyMock",
                "product_type": "Test",
                "images": [{"src": "https://example.com/mock-b.jpg"}],
                "variants": [{"price": "49.99", "inventory_quantity": 5}]
            }
        ]

    query = """
        query CatalogProducts($first: Int!, $after: String) {
          products(first: $first, after: $after) {
            nodes {
              legacyResourceId
              title
              descriptionHtml
              handle
              vendor
              productType
              status
              totalInventory
              onlineStoreUrl
              priceRangeV2 { minVariantPrice { amount } }
              featuredMedia { preview { image { url } } }
            }
            pageInfo { hasNextPage endCursor }
          }
        }
    """
    page_size = max(1, min(limit, 250))
    products: List[Dict[str, Any]] = []
    cursor = None
    while True:
        payload = _shopify_graphql_request(
            shop_domain,
            access_token,
            query,
            {"first": page_size, "after": cursor},
        )
        connection = payload["products"]
        products.extend(_normalize_shopify_product(node) for node in connection["nodes"])
        page_info = connection["pageInfo"]
        if not page_info["hasNextPage"]:
            return products
        cursor = page_info.get("endCursor")
        if not cursor:
            raise RuntimeError("Shopify returned a paginated product response without a cursor")


def _shopify_graphql_request(
    shop_domain: str,
    access_token: str,
    query: str,
    variables: Dict[str, Any],
) -> Dict[str, Any]:
    shop = normalize_shop_domain(shop_domain)
    url = f"https://{shop}/admin/api/{settings.SHOPIFY_API_VERSION}/graphql.json"
    request = urllib.request.Request(
        url,
        data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Shopify GraphQL request failed: {exc}") from exc

    if payload.get("errors"):
        messages = "; ".join(error.get("message", "Unknown error") for error in payload["errors"])
        raise RuntimeError(f"Shopify GraphQL error: {messages}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError("Shopify GraphQL response did not include data")
    return data


def _normalize_shopify_product(node: Dict[str, Any]) -> Dict[str, Any]:
    media = node.get("featuredMedia") or {}
    preview = media.get("preview") or {}
    image = preview.get("image") or {}
    price_range = node.get("priceRangeV2") or {}
    minimum_price = price_range.get("minVariantPrice") or {}
    return {
        "id": node["legacyResourceId"],
        "handle": node.get("handle") or "",
        "status": str(node.get("status") or "ACTIVE").lower(),
        "title": node.get("title") or "",
        "body_html": node.get("descriptionHtml") or "",
        "vendor": node.get("vendor") or "",
        "product_type": node.get("productType") or "",
        "online_store_url": node.get("onlineStoreUrl") or "",
        "images": [{"src": image["url"]}] if image.get("url") else [],
        "variants": [{
            "price": minimum_price.get("amount"),
            "inventory_quantity": node.get("totalInventory") or 0,
        }],
    }
