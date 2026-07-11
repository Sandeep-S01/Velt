# Staging Validation Plan

Run this plan before public launch and after every production-like infrastructure change.

## Environment

- PostgreSQL with TLS enabled and automated backups.
- Redis reachable only from API and worker services; production uses `rediss://`.
- Object storage with TLS enabled and local fallback disabled.
- Persistent Chroma volume or private vector service.
- Dashboard and API served over HTTPS on real staging domains.
- Reverse proxy restricts `/metrics` to internal networks.
- OpenAPI docs disabled unless protected by authentication.

## Required Checks

1. Run `alembic upgrade head` against an empty staging database.
2. Restore a masked database backup into staging and run `alembic upgrade head`.
3. Start API and worker from the same image artifact intended for production.
4. Confirm `/health/live` returns `200`.
5. Confirm `/health/ready` returns `200` with healthy database, Redis, and Chroma checks.
6. Confirm readiness returns non-`200` when PostgreSQL is unavailable.
7. Confirm readiness returns non-`200` when Redis is unavailable.
8. Confirm default/unsafe production environment variables fail startup.
9. Confirm `/metrics` is inaccessible publicly and accessible from monitoring.
10. Run frontend dashboard build artifact against the staging API.

## Functional Flows

1. Register two merchant users.
2. Create one store per merchant.
3. Confirm each merchant cannot list, read, update, upload, or view analytics for the other store.
4. Generate a private API key and confirm it is shown once.
5. Confirm listed keys expose only metadata and prefix.
6. Ingest valid CSV and JSON catalogs.
7. Reject malformed, oversized, duplicate, and malicious catalog files.
8. Search by API key and public widget token.
9. Confirm widget token cannot ingest, manage store settings, or read analytics.
10. Record a widget click and reconcile analytics against raw query/click rows.
11. Run Shopify install, callback, first sync, webhook update, webhook delete, reconnect, uninstall, and data-erasure webhooks against a Shopify development store.

## Recovery Drills

1. Restore PostgreSQL from backup into isolated staging.
2. Rebuild Chroma collections from PostgreSQL source-of-truth products.
3. Roll forward a failed migration with a patch migration.
4. Rotate JWT, private API key, public widget token, and Shopify credentials.
5. Simulate failed ingestion and verify retry/dead-letter handling.
6. Roll back widget asset by serving the previous versioned artifact.

## Exit Criteria

- No critical or high security findings remain unmitigated.
- All staging checks pass with evidence links or screenshots.
- p95 search latency is below the beta target under representative load.
- Backup restore and Chroma rebuild are proven.
- Legal, support, incident, and data-retention pages are published.
