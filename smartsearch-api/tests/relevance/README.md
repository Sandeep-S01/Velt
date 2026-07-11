# Relevance release dataset

Create `queries.v1.json` from a real beta merchant catalog. It must contain at
least 100 human-labeled queries; do not use generated labels for a release gate.

```json
{
  "version": "1.0",
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
irrelevant queries. Run:

```powershell
python scripts/evaluate_relevance.py tests/relevance/queries.v1.json --store-id STORE_ID
```

The command exits non-zero when Recall@5 is below 0.80. The dataset itself is
merchant-specific and intentionally not fabricated or committed with sample
labels.
