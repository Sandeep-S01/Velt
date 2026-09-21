import pytest
from pydantic import ValidationError

from app.core.query_parser import derive_search_filters
from app.models.schemas import SearchFilters, StoreUpdate


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("black office shoes under $100", {"price_max": 100.0}),
        ("desk chair at least 250", {"price_min": 250.0}),
        ("wireless headphones in stock", {"in_stock": True}),
    ],
)
def test_query_constraints_are_extracted(query, expected):
    assert derive_search_filters(query) == expected


def test_explicit_filters_take_precedence_over_query_constraints():
    assert derive_search_filters(
        "shoes under 100",
        {"price_max": 75.0, "category": "Footwear"},
    ) == {"price_max": 75.0, "category": "Footwear"}


def test_invalid_price_range_is_rejected():
    with pytest.raises(ValueError, match="price_min"):
        SearchFilters(price_min=100, price_max=50)


def test_store_search_configuration_is_validated():
    with pytest.raises(ValidationError):
        StoreUpdate(search_config={"min_score_threshold": 1.5})
    with pytest.raises(ValidationError):
        StoreUpdate(search_config={"enable_synonyms": True})
