import pytest

from scripts.staging_smoke import CheckedValue, StagingSmoke, run_search_load, validate_https_url


def test_checked_value_keeps_secrets_out_of_evidence_details():
    smoke = StagingSmoke(
        "https://api.staging.velt.test/api/v1",
        "https://dashboard.staging.velt.test",
        "private-beta-invite-code",
        5,
    )
    secret_value = {"access_token": "must-not-appear", "key": "also-secret"}

    returned = smoke.check(
        "secret-producing check",
        lambda: CheckedValue(secret_value, "credential created"),
    )

    assert returned == secret_value
    assert smoke.results[0].detail == "credential created"
    assert "must-not-appear" not in str(smoke.results)
    assert "also-secret" not in str(smoke.results)


def test_staging_urls_require_https_unless_local_override_is_explicit():
    assert validate_https_url("https://api.staging.velt.test/api/v1", "API", False).startswith("https://")
    with pytest.raises(ValueError, match="HTTPS"):
        validate_https_url("http://api.staging.velt.test/api/v1", "API", False)
    assert validate_https_url("http://127.0.0.1:8000/api/v1", "API", True).startswith("http://")


def test_search_load_calculates_error_rate_without_exposing_responses():
    class Response:
        def __init__(self, status_code):
            self.status_code = status_code

    statuses = iter([200, 200, 500, 200])

    metrics = run_search_load(
        "https://api.staging.velt.test/api/v1/widget/search",
        {"X-Widget-Token": "secret-token"},
        {"store_id": "store", "query": "bottle"},
        request_count=4,
        concurrency=1,
        timeout=1,
        requester=lambda *args, **kwargs: Response(next(statuses)),
    )

    assert metrics["requests"] == 4
    assert metrics["error_rate"] == 0.25
    assert "secret-token" not in str(metrics)
