#!/usr/bin/env python3
"""Run the versioned relevance benchmark against a store's Chroma index."""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.relevance import as_query_evaluation, evaluate_queries
from app.core.search_engine import SemanticSearchEngine


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--store-id", required=True)
    parser.add_argument("--db-path", default="./chroma_db")
    parser.add_argument("--minimum-recall", type=float, default=0.80)
    parser.add_argument("--min-score", type=float, default=0.25)
    args = parser.parse_args()

    payload = json.loads(args.dataset.read_text(encoding="utf-8"))
    cases = payload.get("queries", [])
    if len(cases) < 100:
        raise ValueError("The release benchmark must contain at least 100 labeled queries")

    engine = SemanticSearchEngine(db_path=args.db_path)
    evaluations = []
    for case in cases:
        started = time.perf_counter()
        results = engine.search_store(
            args.store_id, case["query"], n_results=5, min_score=args.min_score
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
    print(json.dumps({"dataset_version": payload.get("version"), **metrics}, indent=2))
    return 0 if metrics["recall_at_5"] >= args.minimum_recall else 1


if __name__ == "__main__":
    raise SystemExit(main())
