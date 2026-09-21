"""Deterministic extraction of supported commerce constraints from shopper queries."""

import re
from typing import Any


PRICE_MAX_PATTERN = re.compile(
    r"\b(?:under|below|less\s+than|up\s+to|max(?:imum)?)\s*\$?\s*(\d+(?:\.\d{1,2})?)\b",
    re.IGNORECASE,
)
PRICE_MIN_PATTERN = re.compile(
    r"\b(?:over|above|more\s+than|at\s+least|min(?:imum)?)\s*\$?\s*(\d+(?:\.\d{1,2})?)\b",
    re.IGNORECASE,
)


def derive_search_filters(query: str, explicit: dict[str, Any] | None = None) -> dict[str, Any]:
    """Merge explicit filters with unambiguous constraints expressed in a query."""
    filters = {key: value for key, value in (explicit or {}).items() if value is not None}

    if "price_max" not in filters:
        match = PRICE_MAX_PATTERN.search(query)
        if match:
            filters["price_max"] = float(match.group(1))

    if "price_min" not in filters:
        match = PRICE_MIN_PATTERN.search(query)
        if match:
            filters["price_min"] = float(match.group(1))

    if "in_stock" not in filters and re.search(r"\bin[ -]?stock\b", query, re.IGNORECASE):
        filters["in_stock"] = True

    return filters
