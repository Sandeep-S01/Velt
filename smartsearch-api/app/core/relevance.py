from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import mean
from typing import Iterable, Sequence


@dataclass(frozen=True)
class QueryEvaluation:
    relevant_ids: frozenset[str]
    returned_ids: tuple[str, ...]
    latency_ms: float


def evaluate_queries(
    evaluations: Iterable[QueryEvaluation],
    *,
    k: int = 5,
) -> dict[str, float | int]:
    """Calculate ranking metrics from human-labeled query results."""
    rows = list(evaluations)
    if not rows:
        raise ValueError("At least one labeled query is required")
    if k < 1:
        raise ValueError("k must be at least 1")

    relevant_rows = [row for row in rows if row.relevant_ids]
    irrelevant_rows = [row for row in rows if not row.relevant_ids]
    if not relevant_rows:
        raise ValueError("At least one query with relevant products is required")

    recalls: list[float] = []
    precisions: list[float] = []
    reciprocal_ranks: list[float] = []

    for row in relevant_rows:
        top_k = row.returned_ids[:k]
        hits = sum(product_id in row.relevant_ids for product_id in top_k)
        recalls.append(hits / len(row.relevant_ids))
        precisions.append(hits / k)
        reciprocal_ranks.append(
            next(
                (1 / rank for rank, product_id in enumerate(top_k, start=1)
                 if product_id in row.relevant_ids),
                0.0,
            )
        )

    latencies = sorted(row.latency_ms for row in rows)
    p95_index = max(0, math.ceil(len(latencies) * 0.95) - 1)
    return {
        "query_count": len(rows),
        "relevant_query_count": len(relevant_rows),
        "irrelevant_query_count": len(irrelevant_rows),
        f"recall_at_{k}": mean(recalls),
        f"precision_at_{k}": mean(precisions),
        "mrr": mean(reciprocal_ranks),
        "zero_result_rate": sum(not row.returned_ids for row in rows) / len(rows),
        "relevant_zero_result_rate": (
            sum(not row.returned_ids for row in relevant_rows) / len(relevant_rows)
        ),
        "irrelevant_rejection_rate": (
            sum(not row.returned_ids for row in irrelevant_rows) / len(irrelevant_rows)
            if irrelevant_rows
            else 1.0
        ),
        "average_latency_ms": mean(latencies),
        "p95_latency_ms": latencies[p95_index],
        "max_latency_ms": latencies[-1],
    }


def as_query_evaluation(
    relevant_ids: Sequence[str], returned_ids: Sequence[str], latency_ms: float
) -> QueryEvaluation:
    return QueryEvaluation(frozenset(relevant_ids), tuple(returned_ids), latency_ms)
