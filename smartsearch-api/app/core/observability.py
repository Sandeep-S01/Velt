import json
import logging
from datetime import UTC, datetime

from prometheus_client import Counter, Histogram


REQUEST_COUNT = Counter(
    "velt_http_requests_total", "HTTP requests", ("method", "route", "status")
)
REQUEST_LATENCY = Histogram(
    "velt_http_request_duration_seconds", "HTTP request latency", ("method", "route")
)
RATE_LIMIT_COUNT = Counter("velt_rate_limit_total", "Rate-limited HTTP requests")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


def configure_logging(environment: str) -> None:
    handler = logging.StreamHandler()
    if environment.lower() == "production":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
