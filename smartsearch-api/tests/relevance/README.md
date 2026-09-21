# Relevance release dataset

Create `queries.v1.json` from a real beta merchant catalog. It must contain at
least 100 human-labeled queries; do not use generated labels for a release gate.

```json
{
  "version": "1.0",
  "labeling": {
    "reviewed_by": "merchant-reviewer-id",
    "reviewed_at": "2026-09-21T00:00:00Z",
    "catalog_snapshot": "catalog-export-version-or-checksum"
  },
  "queries": [
    {
      "query": "waterproof trail shoes",
      "kind": "intent",
      "relevant_product_ids": ["merchant-product-id"]
    }
  ]
}
```

Include intent, exact title/SKU, misspelling, category, and deliberately
irrelevant queries. Irrelevant cases must use an empty `relevant_product_ids`
list; every other kind must contain at least one merchant-confirmed product ID.
The evaluator rejects duplicate queries, incomplete labeling metadata, fewer
than 10 cases for any query kind, and datasets smaller than 100 cases. Run:

```powershell
python scripts/evaluate_relevance.py tests/relevance/queries.v1.json --store-id STORE_ID --output artifacts/relevance-v1.json
```

The command exits non-zero when Recall@5 is below 0.80, MRR is below 0.65,
relevant-query zero results exceed 5%, irrelevant-query rejection is below 80%,
or p95 latency exceeds 500 ms. The dataset itself is merchant-specific and
intentionally not fabricated or committed with sample labels.
