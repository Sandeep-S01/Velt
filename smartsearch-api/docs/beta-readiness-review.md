# Beta Readiness Review

Date: 2026-09-20
Decision: Limited private beta only; no public self-serve launch yet.

## USP Validation

Velt now substantially supports the core USP: merchants can connect or ingest a catalog, deploy a storefront widget, run semantic search, and view real search/click analytics without building AI infrastructure themselves.

The implementation now backs that claim with tenant ownership checks, scoped API keys, public widget tokens, safe widget rendering, Shopify OAuth/HMAC validation, ingestion limits, relevance thresholds, immutable analytics events, production config validation, health checks, metrics, and deployment runbooks.

## Release Gate Result

Public beta is not approved yet because several launch gates require a real staging environment and operational proof, not only local code checks.

Approved scope:
- Internal staging.
- Private beta with 2-3 trusted merchants.
- Manual onboarding and monitored operation.

Not approved:
- Public self-serve signup.
- Paid SLA-backed launch.
- Broad merchant onboarding.

## Verified Locally

- Backend lint: `ruff check app tests scripts seed_db.py`
- Backend compile: `compileall`
- Production config tests
- Storage and widget source security tests
- Database integration tests
- Full API workflow integration test
- Shopify OAuth/webhook integration tests
- Widget/upload/analytics integration test
- Relevance tests and evaluator smoke checks
- Dashboard build: `npm run build`
- Backend test suite: 35 passing tests
- Dashboard lint: `npm run lint`
- Desktop/mobile Chromium checks: 18 passing public-route and widget accessibility, security, attribution, and viewport tests
- NPM audit: zero known vulnerabilities
- Alembic head check: single head `f0a2c4e6b810`
- PostgreSQL 16 migration rollback/upgrade and logical `pg_dump`/`pg_restore` round trip
- Docker Compose config validation
- Staging workflow YAML validation, representative search-load gate, and passive OWASP ZAP jobs
- Production release-candidate container build and runtime smoke check (`sha256:727c3a1d3e05`, 564,401,409 bytes)
- Container runs as `velt` (UID/GID 999), imports the application, uses `torch 2.14.0+cpu` with no CUDA runtime packages, and includes fixed `cryptography 50.0.0`
- CI retains commit-scoped container inspection and PostgreSQL recovery evidence artifacts
- Secret pattern scan: no obvious cloud/private-key patterns found

## Known Blockers Before Public Beta

1. Staging validation has not been executed against production-like PostgreSQL, Redis, object storage, Chroma persistence, dashboard hosting, and real HTTPS domains.
2. `pip-audit` reports four explicitly registered Chroma server advisories with no fixed release. Current mitigation is using embedded `PersistentClient` only and prohibiting Chroma HTTP exposure; public launch still requires a fixed release, replacement, or formal topology-specific acceptance.
3. The production container builds and runs locally with CPU-only PyTorch. CI or staging must still build and record the immutable image digest for each release.
4. PostgreSQL migration rollback and logical restore are proven locally and enforced in CI. Managed backup restore and Chroma rebuild still need proof against staging infrastructure.
5. External dynamic security scanning against staging has not been performed.
6. Public dashboard routes and the distributed widget now have automated desktop/mobile accessibility and overflow checks. Authenticated dashboard workflows and a real merchant storefront embed still need manual staging validation on representative browsers.
7. Public privacy, terms, retention, and support/incident routes are implemented. They still require counsel review and deployment verification before public launch.

## Risk Acceptance For Private Beta

Private beta may proceed only if:

- The API, Redis, PostgreSQL, object storage, and Chroma volume are private to the deployment network.
- Chroma HTTP endpoints are not exposed publicly or to merchants.
- `/metrics` is restricted at the reverse proxy or internal network.
- Merchants are onboarded manually and monitored.
- Every production environment variable passes the startup validator.
- Backups are enabled before real merchant catalogs are ingested.

## Final Recommendation

Use the current codebase for staging and a narrow private beta. Do not publish as a public SaaS until the staging gates, operational drills, per-release image evidence, Chroma vulnerability decision, external scan, and legal/support assets are complete.
