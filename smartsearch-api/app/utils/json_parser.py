"""
JSON parser utility for product ingestion.
"""

import json
from typing import List, Dict, Any

def parse_products_json(json_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Parse JSON bytes, map fields dynamically, and clean raw data.
    """
    content = json_bytes.decode('utf-8', errors='ignore')
    data = json.loads(content)
    
    # Handle wrapped structures
    if isinstance(data, dict):
        for key in ('products', 'items', 'listings', 'data'):
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
        else:
            data = [data]
            
    if not isinstance(data, list):
        raise ValueError("Invalid JSON format. Expected list of products or dictionary containing a product list.")
        
    products = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            continue
            
        # Resolve ID
        p_id = None
        for id_key in ('id', 'external_id', 'product_id', 'sku'):
            if id_key in item and item[id_key]:
                p_id = str(item[id_key]).strip()
                break
        if not p_id:
            p_id = f"json_row_{idx}"
            
        # Resolve title
        title = None
        for title_key in ('title', 'name', 'product_name'):
            if title_key in item and item[title_key]:
                title = str(item[title_key]).strip()
                break
        if not title:
            continue
            
        # Resolve description
        description = None
        for desc_key in ('description', 'desc', 'body_html', 'body'):
            if desc_key in item and item[desc_key]:
                description = str(item[desc_key]).strip()
                break
                
        # Resolve price
        price = None
        for price_key in ('price', 'cost', 'msrp'):
            if price_key in item and item[price_key] is not None:
                try:
                    price = float(item[price_key])
                except (ValueError, TypeError):
                    pass
                break
                
        # Resolve inventory
        inventory = 0
        for inv_key in ('inventory_count', 'inventory', 'quantity', 'qty', 'stock'):
            if inv_key in item and item[inv_key] is not None:
                try:
                    inventory = int(item[inv_key])
                except (ValueError, TypeError):
                    pass
                break

        # Resolve category, brand, media, url
        category = item.get('category') or item.get('type') or item.get('product_type')
        brand = item.get('brand') or item.get('vendor')
        image_url = item.get('image_url') or item.get('image') or item.get('img')
        product_url = item.get('product_url') or item.get('url') or item.get('handle')

        # Resolve active
        is_active = item.get('is_active', True)
        if isinstance(is_active, str):
            is_active = is_active.strip().lower() in ('true', '1', 'yes', 'y')
        else:
            is_active = bool(is_active)

        product = {
            "id": p_id,
            "title": title,
            "description": str(description) if description else None,
            "price": price,
            "category": str(category) if category else None,
            "brand": str(brand) if brand else None,
            "image_url": str(image_url) if image_url else None,
            "product_url": str(product_url) if product_url else None,
            "inventory_count": inventory,
            "is_active": is_active,
            "product_metadata": item
        }
        products.append(product)
        
    return products
