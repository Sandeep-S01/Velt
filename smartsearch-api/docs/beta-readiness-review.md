# Beta Readiness Review

Date: 2026-07-11
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

- Backend lint: `ruff check app tests`
- Backend compile: `compileall`
- Production config tests
- Storage and widget source security tests
- Database integration tests
- Full API workflow integration test
- Shopify OAuth/webhook integration tests
- Widget/upload/analytics integration test
- Relevance tests and evaluator smoke checks
- Dashboard build: `npm run build`
- Dashboard lint: `npm run lint` with existing warnings only
- NPM production audit: zero high vulnerabilities
- Alembic head check: single head `d9b5f2a7e160`
- Docker Compose config validation
- Secret pattern scan: no obvious cloud/private-key patterns found

## Known Blockers Before Public Beta

1. Staging validation has not been executed against production-like PostgreSQL, Redis, object storage, Chroma persistence, dashboard hosting, and real HTTPS domains.
2. `pip-audit` still reports `chromadb 1.5.9` as `PYSEC-2026-311`. There is no fixed Chroma release available at review time. Current mitigation is not exposing Chroma's HTTP server and using embedded `PersistentClient` only.
3. Local Docker image build did not complete within 20 minutes because of the Python ML dependency chain. CI includes the Docker build gate, but the production image still needs a successful build in CI or staging.
4. Backup restore, Chroma rebuild, and migration rollback have runbooks but have not been proven against staging data.
5. External dynamic security scanning against staging has not been performed.
6. Accessibility/mobile browser checks for the widget and dashboard need manual validation.
7. Public legal/support assets are still required: privacy policy, terms, data-retention policy, support contact, and incident process.

## Risk Acceptance For Private Beta

Private beta may proceed only if:

- The API, Redis, PostgreSQL, object storage, and Chroma volume are private to the deployment network.
- Chroma HTTP endpoints are not exposed publicly or to merchants.
- `/metrics` is restricted at the reverse proxy or internal network.
- Merchants are onboarded manually and monitored.
- Every production environment variable passes the startup validator.
- Backups are enabled before real merchant catalogs are ingested.

## Final Recommendation

Use the current codebase for staging and a narrow private beta. Do not publish as a public SaaS until the staging gates, operational drills, Docker build, Chroma vulnerability decision, external scan, and legal/support assets are complete.
