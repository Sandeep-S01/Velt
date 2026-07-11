# Production Operations Runbook

## Release

1. Build one immutable API image and scan it before deployment.
2. Back up PostgreSQL and record the current Alembic revision.
3. Run `alembic upgrade head` as a one-off job. Do not start the API if it fails.
4. Start workers, then API instances, and require `/health/ready` to return 200.
5. Verify `/metrics`, a widget search, authenticated dashboard access, and one ingestion job.
6. Keep the embedded Chroma runtime to one API worker and one writer process per shared volume. Scale horizontally only after moving vector storage to a service that supports concurrent writers safely.

## Database Restore And Migration Rollback

- Target beta RPO: 24 hours. Target RTO: 4 hours. Configure managed PostgreSQL daily backups and point-in-time recovery where available.
- Restore into an isolated database, run validation queries, then update the application secret to the restored endpoint.
- Prefer a forward-fix migration. Use `alembic downgrade <revision>` only when the migration includes a tested downgrade and no newer writes are incompatible.

## Vector Index Rebuild

- Stop catalog mutation workers, retain PostgreSQL as source of truth, and move the affected Chroma collection aside.
- Reindex active and searchable products store-by-store using the current index version.
- Run the merchant relevance benchmark and compare product counts before switching traffic.

## Credential Incident

- Private API key: revoke its database record, issue a replacement once, and inspect audit and ingestion events.
- Widget token: rotate the store token, update the merchant embed, and inspect search/click abuse metrics.
- Shopify: revoke the token in Shopify, clear the encrypted token, rotate app credentials if exposed, and require reconnect.
- JWT key: deploy a new signing secret, invalidate existing sessions, and review authentication events.

## Failed Ingestion

- Identify the job and store from structured logs without logging raw credentials or full payloads.
- Retry only idempotent jobs. Quarantine malformed source files and reconcile PostgreSQL product counts against Chroma.
- Alert when queue depth grows continuously, a job exhausts retries, or index updates fail.

## Widget Rollback

- Keep the previous versioned widget asset available. Change the stable CDN alias to the previous tested artifact.
- Purge CDN cache, verify a merchant storefront, and preserve the failed artifact and trace IDs for investigation.

## Alerts

- Page on readiness failure, PostgreSQL failure, sustained 5xx rate, backup failure, or webhook authentication failures.
- Warn on p95 latency above 500 ms, queue backlog, elevated zero-result rate, rate-limit spikes, and failed syncs.
- Protect `/metrics` at the internal network or reverse proxy; it is not intended as a public endpoint.
