#!/usr/bin/env python3
"""Verify that an exact Velt API release is healthy and safely exposed."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse


def validate_origin(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.path not in {"", "/"}:
        raise ValueError("API origin must be an HTTPS origin without a path")
    return value.rstrip("/")


def request_json(url: str, timeout: float) -> tuple[int, dict]:
    request = urllib.request.Request(url, headers={"User-Agent": "velt-release-verifier/1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            payload = json.load(exc)
        except (ValueError, TypeError):
            payload = {}
        return exc.code, payload


def verify_release_once(api_origin: str, expected_release: str, timeout: float) -> dict:
    live_status, live = request_json(f"{api_origin}/health/live", timeout)
    ready_status, ready = request_json(f"{api_origin}/health/ready", timeout)
    metrics_status, _ = request_json(f"{api_origin}/metrics", timeout)
    docs_status, _ = request_json(f"{api_origin}/api/v1/openapi.json", timeout)

    checks = {
        "liveness": live_status == 200 and live.get("status") == "healthy",
        "readiness": ready_status == 200 and ready.get("status") == "healthy",
        "exact_release": (
            live.get("release") == expected_release
            and ready.get("release") == expected_release
        ),
        "production_mode": (
            live.get("environment") == "production"
            and ready.get("environment") == "production"
        ),
        "dependencies": all(
            status == "healthy"
            for status in ready.get("checks", {}).values()
        ) and set(ready.get("checks", {})) == {"database", "redis", "chroma"},
        "public_metrics_blocked": metrics_status in {401, 403, 404},
        "api_docs_blocked": docs_status == 404,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "observed": {
            "live_status": live_status,
            "ready_status": ready_status,
            "metrics_status": metrics_status,
            "docs_status": docs_status,
            "live_release": live.get("release"),
            "ready_release": ready.get("release"),
            "live_environment": live.get("environment"),
            "ready_environment": ready.get("environment"),
            "dependencies": ready.get("checks", {}),
        },
    }


def verify_with_retries(
    api_origin: str,
    expected_release: str,
    timeout: float,
    attempts: int,
    interval: float,
) -> dict:
    started_at = datetime.now(UTC)
    last_result: dict = {"passed": False, "checks": {}, "observed": {}}
    errors: list[str] = []

    for attempt in range(1, attempts + 1):
        try:
            last_result = verify_release_once(api_origin, expected_release, timeout)
            observed = last_result["observed"]
            print(
                f"attempt={attempt} live={observed['live_status']} "
                f"ready={observed['ready_status']} release={observed['live_release']}"
            )
            if last_result["passed"]:
                break
        except (OSError, ValueError, urllib.error.URLError) as exc:
            errors.append(f"attempt {attempt}: {type(exc).__name__}")
            print(f"attempt={attempt} waiting={type(exc).__name__}")
        if attempt < attempts:
            time.sleep(interval)

    return {
        "schema_version": 1,
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(UTC).isoformat(),
        "api_origin": api_origin,
        "expected_release": expected_release,
        "attempts_used": attempt,
        "passed": last_result["passed"],
        "checks": last_result["checks"],
        "observed": last_result["observed"],
        "request_errors": errors[-10:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-origin", required=True)
    parser.add_argument("--expected-release", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--attempts", type=int, default=60)
    parser.add_argument("--interval", type=float, default=15)
    parser.add_argument("--timeout", type=float, default=20)
    args = parser.parse_args()

    try:
        api_origin = validate_origin(args.api_origin)
    except ValueError as exc:
        parser.error(str(exc))
    if args.attempts < 1 or args.interval < 0 or args.timeout <= 0:
        parser.error("attempts and timeout must be positive; interval cannot be negative")
    if len(args.expected_release) != 40 or any(
        character not in "0123456789abcdef" for character in args.expected_release.lower()
    ):
        parser.error("expected release must be a full 40-character Git SHA")

    report = verify_with_retries(
        api_origin,
        args.expected_release,
        args.timeout,
        args.attempts,
        args.interval,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Evidence report: {args.output}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
