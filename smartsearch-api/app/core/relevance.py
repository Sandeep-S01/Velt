from __future__ import annotations

from dataclasses import dataclass
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

    recalls: list[float] = []
    precisions: list[float] = []
    reciprocal_ranks: list[float] = []

    for row in rows:
        top_k = row.returned_ids[:k]
        hits = sum(product_id in row.relevant_ids for product_id in top_k)
        recalls.append(hits / len(row.relevant_ids) if row.relevant_ids else 1.0)
        precisions.append(hits / k)
        reciprocal_ranks.append(
            next(
                (1 / rank for rank, product_id in enumerate(top_k, start=1)
                 if product_id in row.relevant_ids),
                0.0,
            )
        )

    return {
        "query_count": len(rows),
        f"recall_at_{k}": mean(recalls),
        f"precision_at_{k}": mean(precisions),
        "mrr": mean(reciprocal_ranks),
        "zero_result_rate": sum(not row.returned_ids for row in rows) / len(rows),
        "average_latency_ms": mean(row.latency_ms for row in rows),
    }


def as_query_evaluation(
    relevant_ids: Sequence[str], returned_ids: Sequence[str], latency_ms: float
) -> QueryEvaluation:
    return QueryEvaluation(frozenset(relevant_ids), tuple(returned_ids), latency_ms)
