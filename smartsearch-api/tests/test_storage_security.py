import pytest

from app.utils.storage import storage_client


def test_local_storage_rejects_path_traversal():
    with pytest.raises(ValueError, match="Invalid storage path"):
        storage_client._safe_local_path("../../outside.csv")
