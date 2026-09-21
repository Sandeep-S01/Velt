#!/usr/bin/env python3
"""Run destructive synthetic smoke checks against a deployed Velt staging stack."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
import secrets
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

import requests


@dataclass
class CheckResult:
    name: str
    status: str
    duration_ms: float
    detail: str


@dataclass
class CheckedValue:
    value: object
    detail: str


class SmokeFailure(RuntimeError):
    pass


class StagingSmoke:
    def __init__(
        self,
        api_base_url: str,
        dashboard_base_url: str,
        invite_code: str,
        timeout: float,
        load_requests: int = 50,
        load_concurrency: int = 5,
        max_p95_ms: float = 500.0,
        max_error_rate: float = 0.01,
    ):
        self.api_base_url = api_base_url.rstrip("/")
        self.api_origin = self.api_base_url.removesuffix("/api/v1")
        self.dashboard_base_url = dashboard_base_url.rstrip("/")
        self.invite_code = invite_code
        self.timeout = timeout
        self.load_requests = load_requests
        self.load_concurrency = load_concurrency
        self.max_p95_ms = max_p95_ms
        self.max_error_rate = max_error_rate
        self.session = requests.Session()
        self.results: list[CheckResult] = []
        self.accounts: list[tuple[str, str, str]] = []

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.request(method, url, **kwargs)
        return response

    def check(self, name: str, action) -> object | None:
        started = time.perf_counter()
        try:
            result = action()
            if isinstance(result, CheckedValue):
                value = result.value
                detail = result.detail
            else:
                value = result
                detail = str(result or "ok")
            self.results.append(CheckResult(
                name=name,
                status="passed",
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
                detail=detail,
            ))
            return value
        except Exception as exc:
            self.results.append(CheckResult(
                name=name,
                status="failed",
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
                detail=str(exc)[:500],
            ))
            raise

    @staticmethod
    def expect(response: requests.Response, statuses: set[int], label: str) -> requests.Response:
        if response.status_code not in statuses:
            raise SmokeFailure(f"{label}: expected {sorted(statuses)}, received {response.status_code}")
        return response

    def register(self, email: str, password: str, invite_code: str) -> None:
        response = self.request(
            "POST",
            f"{self.api_base_url}/auth/register",
            json={
                "email": email,
                "full_name": "Velt Staging Smoke",
                "password": password,
                "invite_code": invite_code,
                "accept_terms": True,
            },
        )
        self.expect(response, {200}, "registration")

    def login(self, email: str, password: str) -> str:
        response = self.request(
            "POST",
            f"{self.api_base_url}/auth/token",
            data={"username": email, "password": password},
        )
        self.expect(response, {200}, "login")
        token = response.json().get("access_token")
        if not token:
            raise SmokeFailure("login did not return an access token")
        return token

    @staticmethod
    def bearer(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    def create_account(self, suffix: str) -> tuple[str, str, str]:
        email = f"velt-smoke+{suffix}-{secrets.token_hex(4)}@example.com"
        password = f"Smoke-{secrets.token_urlsafe(20)}"
        self.register(email, password, self.invite_code)
        token = self.login(email, password)
        self.accounts.append((email, password, token))
        return email, password, token

    def cleanup_accounts(self) -> None:
        for email, password, token in reversed(self.accounts):
            response = self.request(
                "DELETE",
                f"{self.api_base_url}/auth/me",
                headers=self.bearer(token),
                json={"password": password},
            )
            if response.status_code not in {200, 401, 404}:
                self.results.append(CheckResult(
                    name=f"cleanup account {email}",
                    status="failed",
                    duration_ms=0,
                    detail=f"cleanup returned {response.status_code}",
                ))

    def run(self) -> None:
        self.check(
            "liveness",
            lambda: self.expect(self.request("GET", f"{self.api_origin}/health/live"), {200}, "liveness").json().get("status"),
        )
        self.check(
            "readiness",
            lambda: self.expect(self.request("GET", f"{self.api_origin}/health/ready"), {200}, "readiness").json().get("status"),
        )
        self.check(
            "public metrics blocked",
            lambda: self.expect(self.request("GET", f"{self.api_origin}/metrics"), {401, 403, 404}, "public metrics").status_code,
        )

        for route in ("privacy", "terms", "data-retention", "support"):
            self.check(
                f"dashboard /{route}",
                lambda route=route: self.expect(
                    self.request("GET", f"{self.dashboard_base_url}/{route}"), {200}, f"dashboard /{route}"
                ).status_code,
            )

        rejected_email = f"velt-smoke-rejected-{secrets.token_hex(4)}@example.com"
        rejected_password = f"Smoke-{secrets.token_urlsafe(20)}"
        self.check(
            "invalid invite rejected",
            lambda: self.expect(
                self.request(
                    "POST",
                    f"{self.api_base_url}/auth/register",
                    json={
                        "email": rejected_email,
                        "full_name": "Rejected Smoke User",
                        "password": rejected_password,
                        "invite_code": "invalid-staging-invite",
                        "accept_terms": True,
                    },
                ),
                {403},
                "invalid invite",
            ).status_code,
        )

        _, _, owner_token = self.check(
            "merchant A registration and login",
            lambda: CheckedValue(self.create_account("a"), "synthetic merchant created"),
        )
        _, _, other_token = self.check(
            "merchant B registration and login",
            lambda: CheckedValue(self.create_account("b"), "synthetic merchant created"),
        )
        owner_headers = self.bearer(owner_token)
        other_headers = self.bearer(other_token)

        store_response = self.check(
            "create synthetic store",
            lambda: CheckedValue(
                self.expect(
                    self.request(
                        "POST",
                        f"{self.api_base_url}/stores/",
                        headers=owner_headers,
                        json={"name": f"Staging Smoke {secrets.token_hex(3)}", "platform": "custom"},
                    ),
                    {200},
                    "store creation",
                ).json(),
                "synthetic store created",
            ),
        )
        store_id = store_response["id"]
        widget_token = store_response["widget_token"]

        self.check(
            "cross-tenant store access blocked",
            lambda: self.expect(
                self.request("GET", f"{self.api_base_url}/stores/{store_id}", headers=other_headers),
                {404},
                "cross-tenant read",
            ).status_code,
        )

        key_payload = self.check(
            "create one-time API key",
            lambda: CheckedValue(
                self.expect(
                    self.request(
                        "POST",
                        f"{self.api_base_url}/stores/{store_id}/keys",
                        headers=owner_headers,
                        json={"name": "staging-smoke", "scopes": ["search", "ingest"]},
                    ),
                    {200},
                    "API key creation",
                ).json(),
                "secret revealed once",
            ),
        )
        api_key = key_payload.get("key")
        if not api_key:
            raise SmokeFailure("API key was not revealed at creation")

        def verify_key_listing() -> str:
            response = self.expect(
                self.request("GET", f"{self.api_base_url}/stores/{store_id}/keys", headers=owner_headers),
                {200},
                "API key listing",
            )
            if any("key" in entry for entry in response.json()):
                raise SmokeFailure("listed API key metadata exposed a secret key")
            return "secret omitted"

        self.check("API key hidden after creation", verify_key_listing)

        products = [
            {
                "id": "staging-smoke-bottle",
                "title": "Insulated Trail Water Bottle",
                "description": "Vacuum insulated stainless steel bottle for cold drinks and hiking.",
                "price": 29.0,
                "category": "Outdoors",
                "inventory_count": 25,
                "product_url": "https://example.com/products/staging-smoke-bottle",
            },
            {
                "id": "staging-smoke-chair",
                "title": "Ergonomic Office Chair",
                "description": "Adjustable desk chair with lumbar support.",
                "price": 180.0,
                "category": "Furniture",
                "inventory_count": 10,
                "product_url": "https://example.com/products/staging-smoke-chair",
            },
        ]
        self.check(
            "JSON catalog ingestion",
            lambda: self.expect(
                self.request(
                    "POST",
                    f"{self.api_base_url}/ingest",
                    headers={"X-API-Key": api_key},
                    json={"store_id": store_id, "products": products},
                ),
                {200},
                "catalog ingestion",
            ).json().get("processed"),
        )

        search_response = self.check(
            "public widget search",
            lambda: self.expect(
                self.request(
                    "POST",
                    f"{self.api_base_url}/widget/search",
                    headers={"X-Widget-Token": widget_token},
                    json={"store_id": store_id, "query": "cold water bottle for hiking", "limit": 5},
                ),
                {200},
                "widget search",
            ),
        )
        search_results = search_response.json()
        if not search_results:
            raise SmokeFailure("widget search returned no results for the synthetic catalog")
        event_token = search_response.headers.get("X-Query-Event-Token")
        if not event_token:
            raise SmokeFailure("widget search did not expose a query event token")

        def verify_search_load() -> str:
            metrics = run_search_load(
                f"{self.api_base_url}/widget/search",
                {"X-Widget-Token": widget_token},
                {"store_id": store_id, "query": "cold water bottle for hiking", "limit": 5},
                self.load_requests,
                self.load_concurrency,
                self.timeout,
            )
            if metrics["p95_ms"] > self.max_p95_ms:
                raise SmokeFailure(
                    f"search p95 {metrics['p95_ms']}ms exceeded {self.max_p95_ms}ms"
                )
            if metrics["error_rate"] > self.max_error_rate:
                raise SmokeFailure(
                    f"search error rate {metrics['error_rate']:.4f} exceeded {self.max_error_rate:.4f}"
                )
            return (
                f"requests={metrics['requests']}, p95_ms={metrics['p95_ms']}, "
                f"error_rate={metrics['error_rate']:.4f}"
            )

        self.check("representative widget search load", verify_search_load)

        self.check(
            "widget click attribution",
            lambda: self.expect(
                self.request(
                    "POST",
                    f"{self.api_base_url}/analytics/click",
                    json={"query_event_token": event_token, "clicked_product_id": search_results[0]["id"]},
                ),
                {200},
                "click attribution",
            ).status_code,
        )
        self.check(
            "widget token cannot ingest",
            lambda: self.expect(
                self.request(
                    "POST",
                    f"{self.api_base_url}/ingest",
                    headers={"X-Widget-Token": widget_token},
                    json={"store_id": store_id, "products": products},
                ),
                {401, 403},
                "widget token ingest attempt",
            ).status_code,
        )

        def verify_analytics() -> str:
            response = self.expect(
                self.request("GET", f"{self.api_base_url}/analytics/{store_id}", headers=owner_headers),
                {200},
                "analytics",
            )
            analytics = response.json()
            if analytics.get("total_searches", 0) < 1 or analytics.get("click_through_rate", 0) <= 0:
                raise SmokeFailure("analytics did not reconcile the synthetic search and click")
            return f"searches={analytics['total_searches']}, ctr={analytics['click_through_rate']}"

        self.check("analytics reconciliation", verify_analytics)


def validate_https_url(value: str, name: str, allow_http: bool) -> str:
    parsed = urlparse(value)
    allowed_schemes = {"https"} | ({"http"} if allow_http else set())
    if parsed.scheme not in allowed_schemes or not parsed.netloc:
        raise ValueError(f"{name} must be an {'HTTP(S)' if allow_http else 'HTTPS'} URL")
    return value.rstrip("/")


def run_search_load(
    url: str,
    headers: dict[str, str],
    payload: dict,
    request_count: int,
    concurrency: int,
    timeout: float,
    requester=None,
) -> dict[str, float | int]:
    """Issue concurrent searches and return sanitized latency/error metrics."""
    requester = requester or requests.post

    def execute() -> tuple[float, bool]:
        started = time.perf_counter()
        try:
            response = requester(url, headers=headers, json=payload, timeout=timeout)
            success = response.status_code == 200
        except requests.RequestException:
            success = False
        return (time.perf_counter() - started) * 1000, success

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        samples = list(executor.map(lambda _: execute(), range(request_count)))

    latencies = sorted(sample[0] for sample in samples)
    errors = sum(not sample[1] for sample in samples)
    p95_index = max(0, math.ceil(len(latencies) * 0.95) - 1)
    return {
        "requests": request_count,
        "concurrency": concurrency,
        "p50_ms": round(latencies[len(latencies) // 2], 2),
        "p95_ms": round(latencies[p95_index], 2),
        "error_rate": errors / request_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base-url", default=os.getenv("STAGING_API_BASE_URL", ""))
    parser.add_argument("--dashboard-base-url", default=os.getenv("STAGING_DASHBOARD_BASE_URL", ""))
    parser.add_argument("--invite-code-env", default="BETA_INVITE_CODE")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--load-requests", type=int, default=50)
    parser.add_argument("--load-concurrency", type=int, default=5)
    parser.add_argument("--max-p95-ms", type=float, default=500.0)
    parser.add_argument("--max-error-rate", type=float, default=0.01)
    parser.add_argument("--allow-http", action="store_true", help="Permit HTTP only for local validation")
    parser.add_argument("--confirm-destructive-staging", action="store_true")
    args = parser.parse_args()

    if not args.confirm_destructive_staging:
        parser.error("--confirm-destructive-staging is required because synthetic accounts and stores are created")

    try:
        api_url = validate_https_url(args.api_base_url, "API base URL", args.allow_http)
        dashboard_url = validate_https_url(args.dashboard_base_url, "dashboard base URL", args.allow_http)
    except ValueError as exc:
        parser.error(str(exc))

    invite_code = os.getenv(args.invite_code_env, "")
    if len(invite_code) < 16:
        parser.error(f"{args.invite_code_env} must contain the staging beta invitation")
    if args.load_requests < 1 or args.load_requests > 90:
        parser.error("--load-requests must be between 1 and 90 to stay within widget rate limits")
    if args.load_concurrency < 1 or args.load_concurrency > 20:
        parser.error("--load-concurrency must be between 1 and 20")

    started_at = datetime.now(UTC)
    smoke = StagingSmoke(
        api_url,
        dashboard_url,
        invite_code,
        args.timeout,
        args.load_requests,
        args.load_concurrency,
        args.max_p95_ms,
        args.max_error_rate,
    )
    exit_code = 0
    try:
        smoke.run()
    except Exception as exc:
        exit_code = 1
        print(f"Staging smoke failed: {exc}", file=sys.stderr)
    finally:
        smoke.cleanup_accounts()

    finished_at = datetime.now(UTC)
    report = {
        "schema_version": 1,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "api_origin": smoke.api_origin,
        "dashboard_origin": smoke.dashboard_base_url,
        "passed": exit_code == 0 and all(item.status == "passed" for item in smoke.results),
        "checks": [asdict(item) for item in smoke.results],
    }
    output = args.output or Path("artifacts") / f"staging-validation-{started_at:%Y%m%dT%H%M%SZ}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Evidence report: {output}")
    print(f"Passed checks: {sum(item.status == 'passed' for item in smoke.results)}/{len(smoke.results)}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
