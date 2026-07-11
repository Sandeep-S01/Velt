import pytest

from app.core.relevance import as_query_evaluation, evaluate_queries


def test_relevance_metrics_are_calculated_from_ranked_results():
    metrics = evaluate_queries(
        [
            as_query_evaluation(["a", "b"], ["a", "x", "b"], 20),
            as_query_evaluation(["c"], [], 40),
        ]
    )

    assert metrics["query_count"] == 2
    assert metrics["recall_at_5"] == pytest.approx(0.5)
    assert metrics["precision_at_5"] == pytest.approx(0.2)
    assert metrics["mrr"] == pytest.approx(0.5)
    assert metrics["zero_result_rate"] == pytest.approx(0.5)
    assert metrics["average_latency_ms"] == pytest.approx(30)


def test_relevance_metrics_require_labeled_queries():
    with pytest.raises(ValueError, match="At least one"):
        evaluate_queries([])
