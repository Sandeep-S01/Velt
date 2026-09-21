from app.integrations import shopify


def test_webhooks_are_registered_through_graphql(monkeypatch):
    calls = []

    def fake_request(shop_domain, access_token, query, variables):
        calls.append((shop_domain, access_token, query, variables))
        return {
            "webhookSubscriptionCreate": {
                "webhookSubscription": {"id": "gid://shopify/WebhookSubscription/1"},
                "userErrors": [],
            }
        }

    monkeypatch.setattr(shopify, "_shopify_graphql_request", fake_request)

    shopify.register_shopify_webhooks(
        "test-shop.myshopify.com",
        "real-token",
        "https://api.example.com/",
    )

    assert [call[3]["topic"] for call in calls] == [
        "PRODUCTS_CREATE",
        "PRODUCTS_UPDATE",
        "PRODUCTS_DELETE",
    ]
    assert all(
        call[3]["subscription"]["uri"] == "https://api.example.com/api/v1/webhooks/shopify"
        for call in calls
    )


def test_graphql_catalog_pagination_and_normalization(monkeypatch):
    calls = []

    def fake_request(shop_domain, access_token, query, variables):
        calls.append((shop_domain, access_token, query, variables))
        if variables["after"] is None:
            return {
                "products": {
                    "nodes": [{
                        "legacyResourceId": "101",
                        "title": "Trail Shoe",
                        "descriptionHtml": "Built for rough trails",
                        "handle": "trail-shoe",
                        "vendor": "Velt Test",
                        "productType": "Footwear",
                        "status": "ACTIVE",
                        "totalInventory": 8,
                        "onlineStoreUrl": "https://shop.example/products/trail-shoe",
                        "priceRangeV2": {"minVariantPrice": {"amount": "79.00"}},
                        "featuredMedia": {"preview": {"image": {"url": "https://img.example/shoe.jpg"}}},
                    }],
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor-1"},
                }
            }
        return {
            "products": {
                "nodes": [],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            }
        }

    monkeypatch.setattr(shopify, "_shopify_graphql_request", fake_request)

    products = shopify.fetch_shopify_products("test-shop.myshopify.com", "real-token")

    assert len(calls) == 2
    assert calls[1][3]["after"] == "cursor-1"
    assert products == [{
        "id": "101",
        "handle": "trail-shoe",
        "status": "active",
        "title": "Trail Shoe",
        "body_html": "Built for rough trails",
        "vendor": "Velt Test",
        "product_type": "Footwear",
        "online_store_url": "https://shop.example/products/trail-shoe",
        "images": [{"src": "https://img.example/shoe.jpg"}],
        "variants": [{"price": "79.00", "inventory_quantity": 8}],
    }]
