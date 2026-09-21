import scripts.verify_deployment as verifier


def test_release_verification_requires_exact_healthy_private_deployment(monkeypatch):
    responses = {
        "/health/live": (
            200,
            {"status": "healthy", "release": "a" * 40, "environment": "production"},
        ),
        "/health/ready": (
            200,
            {
                "status": "healthy",
                "release": "a" * 40,
                "environment": "production",
                "checks": {"database": "healthy", "redis": "healthy", "chroma": "healthy"},
            },
        ),
        "/metrics": (404, {"detail": "Not found"}),
        "/api/v1/openapi.json": (404, {"detail": "Not found"}),
    }
    monkeypatch.setattr(
        verifier,
        "request_json",
        lambda url, timeout: next(value for path, value in responses.items() if url.endswith(path)),
    )

    result = verifier.verify_release_once("https://api.velt.test", "a" * 40, 1)

    assert result["passed"] is True
    assert all(result["checks"].values())


def test_release_verification_rejects_wrong_release_and_public_metrics(monkeypatch):
    responses = {
        "/health/live": (
            200,
            {"status": "healthy", "release": "b" * 40, "environment": "development"},
        ),
        "/health/ready": (
            200,
            {
                "status": "healthy",
                "release": "b" * 40,
                "environment": "development",
                "checks": {"database": "healthy", "redis": "healthy", "chroma": "healthy"},
            },
        ),
        "/metrics": (200, {}),
        "/api/v1/openapi.json": (404, {}),
    }
    monkeypatch.setattr(
        verifier,
        "request_json",
        lambda url, timeout: next(value for path, value in responses.items() if url.endswith(path)),
    )

    result = verifier.verify_release_once("https://api.velt.test", "a" * 40, 1)

    assert result["passed"] is False
    assert result["checks"]["exact_release"] is False
    assert result["checks"]["production_mode"] is False
    assert result["checks"]["public_metrics_blocked"] is False


def test_api_origin_must_be_https_without_a_path():
    assert verifier.validate_origin("https://api.velt.test/") == "https://api.velt.test"

    for invalid in ("http://api.velt.test", "https://api.velt.test/api/v1", "api.velt.test"):
        try:
            verifier.validate_origin(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted invalid origin: {invalid}")
