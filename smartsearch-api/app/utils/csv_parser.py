"""
CSV parser utility for product ingestion.
"""

import io
import pandas as pd
from typing import List, Dict, Any

def parse_products_csv(csv_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Parse CSV bytes, map headers dynamically to match schema standard, and clean row data.
    """
    content = csv_bytes.decode('utf-8', errors='ignore')
    df = pd.read_csv(io.StringIO(content))
    
    # Mapping table mapping lowercase variants to standardized database columns
    col_map = {}
    for col in df.columns:
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
            
    df = df.rename(columns=col_map)
    
    products = []
    for idx, row in df.iterrows():
        p_id = str(row.get('id', '')).strip()
        if not p_id or pd.isna(p_id):
            p_id = f"row_{idx}"
            
        title = str(row.get('title', '')).strip()
        if not title or pd.isna(title):
            # Skip row if title is completely missing
            continue
            
        price_val = row.get('price')
        price = float(price_val) if pd.notna(price_val) and price_val != "" else None
        
        inventory_val = row.get('inventory_count', 0)
        try:
            inventory = int(float(inventory_val)) if pd.notna(inventory_val) else 0
        except ValueError:
            inventory = 0
            
        active_val = row.get('is_active', True)
        if isinstance(active_val, str):
            is_active = active_val.strip().lower() in ('true', '1', 'yes', 'y')
        else:
            is_active = bool(active_val) if pd.notna(active_val) else True

        # Convert float NaN values from pandas row to None for clean JSON serialization
        raw_metadata = {}
        for k, v in row.to_dict().items():
            raw_metadata[k] = None if pd.isna(v) else v

        product = {
            "id": p_id,
            "title": title,
            "description": str(row.get('description', '')) if pd.notna(row.get('description')) else None,
            "price": price,
            "category": str(row.get('category', '')) if pd.notna(row.get('category')) else None,
            "brand": str(row.get('brand', '')) if pd.notna(row.get('brand')) else None,
            "image_url": str(row.get('image_url', '')) if pd.notna(row.get('image_url')) else None,
            "product_url": str(row.get('product_url', '')) if pd.notna(row.get('product_url')) else None,
            "inventory_count": inventory,
            "is_active": is_active,
            "product_metadata": raw_metadata
        }
        products.append(product)
        
    return products
