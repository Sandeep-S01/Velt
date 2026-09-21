from app.models.database import Product, Store
from app.services.index_rebuild import rebuild_store_index


class FakeCollection:
    def __init__(self, engine, store_id):
        self.engine = engine
        self.store_id = store_id

    def count(self):
        return len(self.engine.indexed.get(self.store_id, []))


class FakeSearchEngine:
    def __init__(self):
        self.indexed = {}
        self.deleted = []

    def delete_store_index(self, store_id):
        self.deleted.append(store_id)
        self.indexed[store_id] = []

    def index_store_products(self, store_id, products):
        self.indexed.setdefault(store_id, []).extend(products)

    def _get_store_collection(self, store_id):
        return FakeCollection(self, store_id)


def test_rebuild_uses_only_active_postgres_products(db_session):
    store = Store(name="Rebuild Store", platform="custom")
    db_session.add(store)
    db_session.flush()
    db_session.add_all([
        Product(store_id=store.id, external_id="active", title="Active Product", is_active=True),
        Product(store_id=store.id, external_id="inactive", title="Inactive Product", is_active=False),
    ])
    db_session.commit()
    engine = FakeSearchEngine()

    result = rebuild_store_index(db_session, engine, store.id, batch_size=1)

    assert result.source_products == 1
    assert result.indexed_products == 1
    assert engine.deleted == [store.id]
    assert [product["id"] for product in engine.indexed[store.id]] == ["active"]
