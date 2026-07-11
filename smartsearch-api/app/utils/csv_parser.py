"""
CSV parser utility for product ingestion.
"""

import io
import csv
from typing import List, Dict, Any

MAX_PRODUCTS_PER_FILE = 50_000
MAX_TITLE_LENGTH = 500
MAX_DESCRIPTION_LENGTH = 20_000

def parse_products_csv(csv_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Parse CSV bytes, map headers dynamically to match schema standard, and clean row data.
    """
    content = csv_bytes.decode('utf-8', errors='ignore')
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    if len(rows) > MAX_PRODUCTS_PER_FILE:
        raise ValueError(f"Catalog exceeds {MAX_PRODUCTS_PER_FILE} product limit")
    
    # Mapping table mapping lowercase variants to standardized database columns
    col_map = {}
    for col in reader.fieldnames or []:
        col_lower = str(col).strip().lower()
        if col_lower in ('id', 'external_id', 'product_id', 'sku'):
            col_map[col] = 'id'
        elif col_lower in ('title', 'name', 'product_name'):
            col_map[col] = 'title'
        elif col_lower in ('description', 'desc', 'body_html', 'body'):
            col_map[col] = 'description'
        elif col_lower in ('price', 'cost', 'msrp'):
            col_map[col] = 'price'
        elif col_lower in ('category', 'type', 'product_type'):
            col_map[col] = 'category'
        elif col_lower in ('brand', 'vendor'):
            col_map[col] = 'brand'
        elif col_lower in ('image_url', 'image', 'img', 'image_src'):
            col_map[col] = 'image_url'
        elif col_lower in ('product_url', 'url', 'handle', 'handle_url'):
            col_map[col] = 'product_url'
        elif col_lower in ('inventory_count', 'inventory', 'quantity', 'qty', 'stock'):
            col_map[col] = 'inventory_count'
        elif col_lower in ('is_active', 'active', 'published'):
            col_map[col] = 'is_active'
    
    products = []
    for row in rows:
        normalized_row = {
            col_map.get(key, key): _clean_csv_value(value)
            for key, value in row.items()
        }

        raw_id = normalized_row.get('id')
        if _is_blank(raw_id):
            continue
        p_id = str(raw_id).strip()[:255]
            
        raw_title = normalized_row.get('title')
        if _is_blank(raw_title):
            # Skip row if title is completely missing
            continue
        title = str(raw_title).strip()[:MAX_TITLE_LENGTH]
            
        price_val = normalized_row.get('price')
        price = float(price_val) if not _is_blank(price_val) else None
        if price is not None and price < 0:
            raise ValueError(f"Negative price for product {p_id}")
        
        inventory_val = normalized_row.get('inventory_count', 0)
        try:
            inventory = max(0, int(float(inventory_val))) if not _is_blank(inventory_val) else 0
        except ValueError:
            inventory = 0
            
        active_val = normalized_row.get('is_active', True)
        if isinstance(active_val, str):
            is_active = active_val.strip().lower() in ('true', '1', 'yes', 'y')
        else:
            is_active = bool(active_val) if not _is_blank(active_val) else True

        raw_metadata = {
            key: _clean_csv_value(value)
            for key, value in row.items()
        }

        product = {
            "id": p_id,
            "title": title,
            "description": _optional_str(normalized_row.get('description'), MAX_DESCRIPTION_LENGTH),
            "price": price,
            "category": _optional_str(normalized_row.get('category')),
            "brand": _optional_str(normalized_row.get('brand')),
            "image_url": _optional_str(normalized_row.get('image_url')),
            "product_url": _optional_str(normalized_row.get('product_url')),
            "inventory_count": inventory,
            "is_active": is_active,
            "product_metadata": raw_metadata
        }
        products.append(product)
        
    return products


def _clean_csv_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None
    return value


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _optional_str(value: Any, max_length: int | None = None) -> str | None:
    if _is_blank(value):
        return None
    text = str(value).strip()
    if max_length is not None:
        return text[:max_length]
    return text
