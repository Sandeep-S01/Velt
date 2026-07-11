# Public Launch Checklist

## Product Claims

- Landing page says "private beta" until staging gates are complete.
- Do not claim 99.9% SLA, automatic ranking optimization, or guaranteed relevance.
- Publish measured latency and availability only after monitoring records them.

## Security

- Production startup rejects default secrets.
- CORS and trusted hosts use explicit domains only.
- Dashboard served over HTTPS with edge HSTS and CSP.
- API docs disabled or protected.
- `/metrics` is private.
- Chroma HTTP server is not exposed.
- Private API keys are hashed, scoped, revocable, and shown once.
- Public widget tokens are revocable and restricted to public widget/search endpoints.
- Shopify OAuth state and webhook HMAC checks are enabled.

## Operations

- CI is green.
- Docker image builds successfully from CI.
- Migrations are run as a release job.
- PostgreSQL backups and restore drills are complete.
- Chroma rebuild drill is complete.
- Alerting covers readiness, 5xx rate, DB failures, Redis failures, queue backlog, webhook failures, and backup failures.
- Runbooks are published and tested.

## Legal And Support

- Privacy policy published.
- Terms of service published.
- Data-retention policy published.
- Support contact published.
- Incident response process published.
- Merchant data deletion process tested.

## Launch Decision

Public launch is approved only after every checklist item is complete and recorded with evidence.
