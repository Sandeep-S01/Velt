import pytest

from scripts.evaluate_relevance import validate_dataset


def release_dataset() -> dict:
    kinds = ("intent", "exact", "misspelling", "category", "irrelevant")
    queries = []
    for index in range(100):
        kind = kinds[index % len(kinds)]
        queries.append({
            "query": f"merchant query {index}",
            "kind": kind,
            "relevant_product_ids": [] if kind == "irrelevant" else [f"product-{index}"],
        })
    return {
        "version": "1.0",
        "labeling": {
            "reviewed_by": "merchant-reviewer",
            "reviewed_at": "2026-09-21T00:00:00Z",
            "catalog_snapshot": "catalog-sha256",
        },
        "queries": queries,
    }


def test_release_dataset_requires_reviewed_balanced_labels():
    payload = release_dataset()

    assert len(validate_dataset(payload)) == 100

    payload["queries"][0]["relevant_product_ids"] = []
    with pytest.raises(ValueError, match="at least one relevant product"):
        validate_dataset(payload)


def test_release_dataset_rejects_duplicates_and_missing_review_metadata():
    payload = release_dataset()
    payload["queries"][1]["query"] = payload["queries"][0]["query"].upper()
    with pytest.raises(ValueError, match="Duplicate query"):
        validate_dataset(payload)

    payload = release_dataset()
    payload["labeling"]["reviewed_by"] = ""
    with pytest.raises(ValueError, match="reviewed_by"):
        validate_dataset(payload)


def test_release_dataset_requires_enough_cases_per_query_kind():
    payload = release_dataset()
    for case in payload["queries"]:
        if case["kind"] == "misspelling":
            case["kind"] = "intent"

    with pytest.raises(ValueError, match="missing query kinds: misspelling"):
        validate_dataset(payload)
