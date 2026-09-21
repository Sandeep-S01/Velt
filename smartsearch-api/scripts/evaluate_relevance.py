#!/usr/bin/env python3
"""Run the versioned relevance benchmark against a store's Chroma index."""

import argparse
import json
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.relevance import as_query_evaluation, evaluate_queries
from app.core.query_parser import derive_search_filters
from app.core.search_engine import SemanticSearchEngine


REQUIRED_QUERY_KINDS = {"intent", "exact", "misspelling", "category", "irrelevant"}
MINIMUM_CASES_PER_KIND = 10


def validate_dataset(payload: dict) -> list[dict]:
    cases = payload.get("queries", [])
    if len(cases) < 100:
        raise ValueError("The release benchmark must contain at least 100 labeled queries")

    labeling = payload.get("labeling", {})
    for field in ("reviewed_by", "reviewed_at", "catalog_snapshot"):
        if not str(labeling.get(field, "")).strip():
            raise ValueError(f"Dataset labeling metadata must include {field}")

    kinds = set()
    seen_queries = set()
    for index, case in enumerate(cases, start=1):
        query = str(case.get("query", "")).strip()
        kind = case.get("kind")
        relevant_ids = case.get("relevant_product_ids")
        if not query:
            raise ValueError(f"Query {index} is empty")
        normalized_query = query.casefold()
        if normalized_query in seen_queries:
            raise ValueError(f"Duplicate query at row {index}: {query}")
        seen_queries.add(normalized_query)
        if kind not in REQUIRED_QUERY_KINDS:
            raise ValueError(f"Query {index} has unsupported kind: {kind}")
        if not isinstance(relevant_ids, list):
            raise ValueError(f"Query {index} must include relevant_product_ids")
        if kind == "irrelevant" and relevant_ids:
            raise ValueError(f"Irrelevant query {index} must have no relevant products")
        if kind != "irrelevant" and not relevant_ids:
            raise ValueError(f"Relevant query {index} must have at least one relevant product")
        kinds.add(kind)

    missing_kinds = sorted(REQUIRED_QUERY_KINDS - kinds)
    if missing_kinds:
        raise ValueError("Dataset is missing query kinds: " + ", ".join(missing_kinds))
    kind_counts = Counter(case["kind"] for case in cases)
    underrepresented = sorted(
        kind for kind, count in kind_counts.items() if count < MINIMUM_CASES_PER_KIND
    )
    if underrepresented:
        raise ValueError(
            f"Each query kind requires at least {MINIMUM_CASES_PER_KIND} cases: "
            + ", ".join(underrepresented)
        )
    return cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--store-id", required=True)
    parser.add_argument("--db-path", default="./chroma_db")
    parser.add_argument("--minimum-recall", type=float, default=0.80)
    parser.add_argument("--minimum-mrr", type=float, default=0.65)
    parser.add_argument("--maximum-p95-ms", type=float, default=500.0)
    parser.add_argument("--maximum-relevant-zero-rate", type=float, default=0.05)
    parser.add_argument("--minimum-irrelevant-rejection", type=float, default=0.80)
    parser.add_argument("--min-score", type=float, default=0.25)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.dataset.read_text(encoding="utf-8"))
    cases = validate_dataset(payload)

    engine = SemanticSearchEngine(db_path=args.db_path)
    evaluations = []
    for case in cases:
        started = time.perf_counter()
        results = engine.search_store(
            args.store_id,
            case["query"],
            n_results=5,
            min_score=args.min_score,
            filters=derive_search_filters(case["query"]),
        )
        latency_ms = (time.perf_counter() - started) * 1000
        evaluations.append(
            as_query_evaluation(
                case["relevant_product_ids"],
                [result["metadata"]["external_id"] for result in results],
                latency_ms,
            )
        )

    metrics = evaluate_queries(evaluations)
    passed = (
        metrics["recall_at_5"] >= args.minimum_recall
        and metrics["mrr"] >= args.minimum_mrr
        and metrics["p95_latency_ms"] <= args.maximum_p95_ms
        and metrics["relevant_zero_result_rate"] <= args.maximum_relevant_zero_rate
        and metrics["irrelevant_rejection_rate"] >= args.minimum_irrelevant_rejection
    )
    report = {
        "schema_version": 1,
        "dataset_version": payload.get("version"),
        "catalog_snapshot": payload["labeling"]["catalog_snapshot"],
        "query_kind_counts": dict(sorted(Counter(case["kind"] for case in cases).items())),
        "evaluated_at": datetime.now(UTC).isoformat(),
        "passed": passed,
        "thresholds": {
            "minimum_recall_at_5": args.minimum_recall,
            "minimum_mrr": args.minimum_mrr,
            "maximum_p95_latency_ms": args.maximum_p95_ms,
            "maximum_relevant_zero_result_rate": args.maximum_relevant_zero_rate,
            "minimum_irrelevant_rejection_rate": args.minimum_irrelevant_rejection,
            "minimum_score": args.min_score,
        },
        "metrics": metrics,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    print(rendered, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
