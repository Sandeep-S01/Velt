from starlette.requests import Request

from app.core.middleware import RateLimitMiddleware


class FakeRedis:
    def __init__(self):
        self.values = {}

    def set(self, key, value, ex=None, nx=False):
        if nx and key in self.values:
            return False
        self.values[key] = int(value)
        return True

    def incr(self, key):
        self.values[key] += 1
        return self.values[key]

    def get(self, key):
        return self.values.get(key)


def make_request(headers=None):
    encoded_headers = [
        (key.lower().encode(), value.encode())
        for key, value in (headers or {}).items()
    ]
    return Request({
        "type": "http",
        "method": "GET",
        "path": "/api/v1/demo/search",
        "headers": encoded_headers,
        "client": ("203.0.113.10", 1234),
        "scheme": "https",
        "server": ("api.example.com", 443),
        "query_string": b"",
    })


def test_client_identity_does_not_trust_forwarded_header():
    middleware = RateLimitMiddleware(lambda scope, receive, send: None)
    request = make_request({"X-Forwarded-For": "198.51.100.20"})

    assert middleware._get_client_id(request) == "ip:203.0.113.10"


def test_rate_limit_counter_blocks_only_after_limit(monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr("app.core.middleware.get_redis", lambda: fake_redis)
    middleware = RateLimitMiddleware(
        lambda scope, receive, send: None,
        rate_limit=2,
        window_seconds=60,
    )

    assert middleware._is_rate_limited("ip:test") is False
    assert middleware._is_rate_limited("ip:test") is False
    assert middleware._is_rate_limited("ip:test") is True
