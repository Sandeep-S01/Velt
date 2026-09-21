"""Rebuild derived vector indexes from PostgreSQL source-of-truth products."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.search_engine import SemanticSearchEngine
from app.models.database import Product, Store


@dataclass(frozen=True)
class IndexRebuildResult:
    store_id: str
    source_products: int
    indexed_products: int


def rebuild_store_index(
    db: Session,
    search_engine: SemanticSearchEngine,
    store_id: str,
    batch_size: int = 500,
) -> IndexRebuildResult:
    """Replace one store index using active products from PostgreSQL."""
    if db.query(Store.id).filter(Store.id == store_id).first() is None:
        raise ValueError(f"Store not found: {store_id}")

    source_count = db.query(Product).filter(
        Product.store_id == store_id,
        Product.is_active == True,
    ).count()
    search_engine.delete_store_index(store_id)

    for offset in range(0, source_count, batch_size):
        products = db.query(Product).filter(
            Product.store_id == store_id,
            Product.is_active == True,
        ).order_by(Product.id).offset(offset).limit(batch_size).all()
        search_engine.index_store_products(
            store_id,
            [
                {
                    "id": product.external_id,
                    "external_id": product.external_id,
                    "title": product.title,
                    "description": product.description or "",
                    "price": float(product.price) if product.price is not None else None,
                    "category": product.category or "",
                    "brand": product.brand or "",
                    "image_url": product.image_url or "",
                    "product_url": product.product_url or "",
                    "inventory_count": product.inventory_count,
                    "is_active": True,
                }
                for product in products
            ],
        )

    indexed_count = search_engine._get_store_collection(store_id).count()
    if indexed_count != source_count:
        raise RuntimeError(
            f"Index count mismatch for store {store_id}: PostgreSQL={source_count}, Chroma={indexed_count}"
        )
    return IndexRebuildResult(store_id, source_count, indexed_count)
