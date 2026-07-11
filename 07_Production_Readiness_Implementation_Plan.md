# Velt Production Readiness Implementation Plan

**Version:** 1.0
**Date:** 2026-07-11
**Status:** Proposed
**Target:** Secure public beta for the first 10-50 merchants

## 1. Objective

Move Velt from a functional MVP to a production-ready, multi-tenant semantic search SaaS whose implementation supports this defensible USP:

> Velt gives e-commerce merchants a fast way to add semantic product search, a storefront search widget, and actionable search analytics without building their own AI search infrastructure.

The release must demonstrate four outcomes:

1. Merchant data and actions are isolated by tenant.
2. The storefront widget cannot compromise a merchant website.
3. Search and analytics metrics are technically correct and based on real data.
4. Deployment, migrations, monitoring, backups, and tests support safe operation.

## 2. Scope And Assumptions

### Initial operating assumptions

- 10-50 merchants during public beta.
- Up to 50,000 active products per merchant.
- Up to 10 search requests per second per merchant during normal traffic.
- Search p95 target below 500 ms with hosted embeddings and below 250 ms with local embeddings.
- API availability target of 99.5% during beta. Do not advertise a higher SLA until measured.
- PostgreSQL is the source of truth; ChromaDB is a rebuildable search index.
- Redis is required in production for rate limiting, background jobs, and OAuth state.
- Catalog and query data are retained only as long as required by the merchant-facing analytics policy.

### Out of scope for the public-beta gate

- Billing and automated subscription enforcement.
- Enterprise SSO and complex organization roles.
- Multi-region active-active infrastructure.
- Machine-learned ranking based on clicks.
- Guaranteed 99.9% SLA.

## 3. Recommended Architecture

```text
Merchant Dashboard ---- JWT/session ----> FastAPI API ----> PostgreSQL
                                              |                  |
Storefront Widget ---- public token/domain -->|                  +--> audit/query data
                                              |
                                              +--> Redis/Celery --> ingestion workers
                                              |
                                              +--> ChromaDB (rebuildable per-store index)
                                              |
                                              +--> Shopify APIs/webhooks
```

### Baseline recommendation

- Keep the existing FastAPI, React, PostgreSQL, Redis/Celery, and ChromaDB stack.
- Enforce ownership in PostgreSQL and in every merchant endpoint.
- Serve the widget as a versioned static asset from a controlled domain or CDN.
- Give each storefront a revocable public widget token restricted to search, autocomplete, and click tracking.
- Keep private ingestion API keys server-side and store only their hashes.
- Run migrations as a deployment step; never rely on `create_all()` in production.

### Alternative considered

Replace ChromaDB with PostgreSQL plus `pgvector`. This would simplify backups, tenant filtering, and transactions, but it adds migration effort and is not required for the first 10-50 merchants. Reassess after load testing or if ChromaDB operations become unreliable.

## 4. Delivery Strategy

Estimated duration: **6 weeks for two engineers**, or **8-10 weeks for one engineer**. Security-critical phases must be completed in order. Product polish and observability can run in parallel after the tenancy migration is stable.

| Phase | Focus | Estimate | Release impact |
|---|---|---:|---|
| 0 | Baseline and release controls | 2 days | Establishes reproducible verification |
| 1 | Tenant and data model correction | 5 days | Critical blocker |
| 2 | Authentication and API authorization | 5 days | Critical blocker |
| 3 | Widget and public API security | 5 days | Critical blocker |
| 4 | Shopify and ingestion hardening | 5 days | Critical blocker |
| 5 | Search and analytics correctness | 5 days | USP blocker |
| 6 | Deployment and operations | 5 days | Production blocker |
| 7 | Beta validation and launch | 3-5 days | Final release gate |

## 5. Phase 0: Baseline And Release Controls

### Tasks

- Add `pyproject.toml` or separate locked production/development requirement files.
- Declare direct dependencies explicitly, including `pydantic-settings`, `bcrypt`, `requests`, `pytest`, `pytest-asyncio`, and security tooling.
- Pin or lock Python and Node dependency versions.
- Add backend commands for formatting, linting, type checking, tests, and dependency audit.
- Add CI for backend tests, frontend build/lint, widget tests, migration checks, and dependency scans.
- Create separate development, test, staging, and production environment templates containing names only.
- Remove committed upload artifacts and add `smartsearch-api/data/uploads/` to `.gitignore`.
- Remove or clearly isolate debug scripts and seeded production-like credentials.
- Change README status from “production-ready” to “MVP under production hardening.”

### Acceptance criteria

- A clean clone installs without relying on undeclared transitive packages.
- CI runs on every pull request and blocks merging on failures.
- Backend tests can execute with one documented command.
- No secrets, generated uploads, local databases, or vector indexes are tracked by Git.

## 6. Phase 1: Tenant And Data Model Correction

### Data model changes

- Add `owner_user_id` to `stores`, referencing `users.id`, non-null after backfill.
- Add `Store.owner` and `User.stores` relationships.
- Change product identity from global `products.id` to a generated internal ID plus a unique constraint on `(store_id, external_id)`.
- Preserve the merchant/platform product identifier in `external_id`.
- Add indexes for `(owner_user_id, created_at)`, `(store_id, external_id)`, search logs by `(store_id, created_at)`, and webhook lookup fields.
- Add the missing `webhook_events` migration.
- Add a unique/idempotency constraint for Shopify webhook identifiers where available.
- Add `public_widget_token_hash`, allowed storefront domains, and token status to the store or a dedicated credential table.
- Add API key prefix, hash, scopes, expiration, and revocation timestamps. Remove plaintext key persistence.

### Migration sequence

1. Add nullable ownership and external-ID fields.
2. Backfill existing stores to an explicit migration owner selected through configuration.
3. Backfill product external IDs and generated internal IDs.
4. Update application reads and writes to use `(store_id, external_id)`.
5. Add constraints only after validation queries report no nulls or duplicates.
6. Create a tested rollback and database backup before production migration.

### Acceptance criteria

- Two stores may contain the same external product ID without collision.
- Every store has exactly one valid owner for beta.
- Migration succeeds against both a fresh database and a copy of existing data.
- Chroma collections can be rebuilt from PostgreSQL after migration.

## 7. Phase 2: Authentication And API Authorization

### Tasks

- Introduce a reusable `get_owned_store(store_id, current_user, db)` dependency.
- Scope all store, product, analytics, key, settings, upload, and Shopify actions to the authenticated owner.
- Remove unscoped service methods such as global product and store listing from merchant routes.
- Reject attempts to set `store_id`, ownership, verification status, webhook secrets, or other privileged fields through public request DTOs.
- Separate create/update request schemas from response schemas.
- Require verified email before creating credentials or connecting Shopify.
- Add login throttling and generic authentication failure responses.
- Add password reset and email verification token flows before general public signup.
- Decide on session strategy:
  - Preferred: short-lived access token in memory plus rotating refresh token in a Secure, HttpOnly, SameSite cookie.
  - Minimum beta fallback: short-lived JWT, no refresh endpoint, strict CSP, and documented session limitations.
- Add JWT issuer, audience, unique token ID, and key rotation support.
- Validate API key expiry, scope, revocation, and constant-time hash comparison.
- Return a private API key only once at creation; list endpoints return prefix and metadata only.
- Add audit events for login, key creation/revocation, store changes, Shopify connection, and deletion.

### Required authorization tests

- User A cannot list, read, update, delete, upload to, or view analytics for User B's store.
- User A cannot create or reveal credentials for User B's store.
- A product identifier from another tenant cannot be read or modified.
- Expired, revoked, malformed, and wrong-scope API keys are rejected.
- Unverified or inactive users cannot perform privileged actions.

### Acceptance criteria

- Every non-public route has an explicit authentication and ownership policy.
- Automated cross-tenant tests cover all merchant resources.
- No API response exposes password hashes, encrypted Shopify tokens, webhook secrets, or full stored API keys.

## 8. Phase 3: Widget And Public API Security

### Widget changes

- Replace catalog-driven `innerHTML` templates with DOM construction and `textContent`.
- Validate URLs with `new URL()` and permit only `https:` plus an explicit development exception.
- Set links and image properties through DOM APIs; reject `javascript:`, `data:`, and malformed URLs.
- Validate colors, positions, booleans, and placeholder length before storing and rendering widget configuration.
- Isolate widget styles in a Shadow DOM to prevent storefront conflicts and reduce injection surface.
- Add an instance-specific root instead of global IDs so multiple widgets cannot collide.
- Version the widget asset, for example `/widget/v1/widget.js`, and define a cache/rollback policy.
- Keep `widget/widget.js` and `dashboard/public/widget.js` generated from one source to prevent drift.

### Public endpoint changes

- Require a revocable public widget token tied to one store.
- Optionally enforce an allowed-domain list using `Origin`/`Referer` as an abuse control, not as the sole authentication control.
- Apply stricter search/autocomplete limits by widget token and IP.
- Validate query length, normalize whitespace, cap result limits, and reject oversized bodies.
- Replace sequential query-log IDs exposed to clients with opaque event tokens.
- Validate that a click belongs to the same store, query event, and returned product.
- Make click recording idempotent and prevent arbitrary analytics manipulation.
- Add a restrictive CSP recommendation and Subresource Integrity guidance for merchants where deployment permits it.

### Security tests

- Product and config payloads containing HTML, quotes, event handlers, CSS escapes, and script URLs render as harmless text.
- Cross-store click tokens and forged product IDs are rejected.
- Search abuse receives `429`; normal storefront traffic remains functional.
- Widget works on desktop and mobile without changing host-page styles.

### Acceptance criteria

- Automated XSS tests pass against product titles, descriptions, URLs, suggestions, and configuration.
- A leaked public widget token cannot ingest data, access analytics, or manage the store.
- The widget has a tested rollback path to the previous version.

## 9. Phase 4: Shopify And Ingestion Hardening

### Shopify OAuth

- Require the authenticated user; derive `user_id` server-side instead of accepting it in the query string.
- Validate shop domains strictly against `^[a-z0-9][a-z0-9-]*\.myshopify\.com$`.
- Store opaque, random OAuth state in Redis with user and shop metadata; fail closed if Redis is unavailable.
- Verify the Shopify callback HMAC before exchanging the authorization code.
- Bind state to both user and shop and consume it exactly once.
- Remove all production mock bypasses or guard them behind an explicit test-only dependency override.
- Use the Shopify app client secret for webhook HMAC verification.
- Use a currently supported Shopify API version from configuration and define an upgrade schedule.
- Handle reauthorization, token revocation, uninstall, and data-erasure webhooks.

### Webhooks and sync

- Verify HMAC before parsing or storing payloads.
- Enforce maximum body size and supported topic allowlists.
- Use webhook IDs for deduplication and idempotent processing.
- Return quickly after durable enqueueing; retry workers with exponential backoff and dead-letter handling.
- Record sanitized errors without storing unnecessary sensitive payload fields.
- Reconcile deletions and products removed from a full Shopify sync.

### File and API ingestion

- Enforce upload size on the server while streaming; do not read the entire file into memory.
- Generate server-side object names and discard path components from client filenames.
- Validate MIME type and content, not only filename extension.
- Set product count, field length, nesting, and metadata-size limits.
- Reject invalid prices, identifiers, URLs, and inventory values consistently.
- Make batch writes transactional and record job-level processed/failed counts.
- Quarantine failed files and delete raw uploads according to a retention policy.
- Configure S3/MinIO TLS verification correctly; never use `verify=False` in production.

### Acceptance criteria

- OAuth fails closed for invalid state, HMAC, shop, user, or Redis availability.
- Duplicate webhooks and ingestion retries do not duplicate products or analytics.
- Path traversal, oversized files, malformed files, and cross-store product IDs are rejected.
- A full sync leaves PostgreSQL and ChromaDB consistent or reports a recoverable failed state.

## 10. Phase 5: Search And Analytics Correctness

### Search quality

- Define `score` consistently as cosine similarity and display `score * 100` in the widget.
- Add a configurable relevance threshold and return no result below it.
- Filter inactive and non-searchable products in vector queries and database fallback reads.
- Add deterministic tie-breaking and maximum result limits.
- Use title, description, category, brand, and selected attributes in the indexed document with documented weights or preprocessing.
- Add index version metadata and a reindex command for model/schema changes.
- Ensure product update/delete operations update PostgreSQL and ChromaDB through a recoverable job or outbox flow.

### Relevance evaluation

- Build a versioned test set of at least 100 representative catalog queries.
- Label relevant products and track Recall@5, Precision@5, MRR, zero-result rate, and latency.
- Include spelling errors, intent queries, exact SKU/title queries, irrelevant queries, and multiple catalog categories.
- Define a minimum beta gate, for example Recall@5 >= 0.80 on the agreed test set.

### Analytics correctness

- Add real time-range filters and aggregate query counts by date.
- Return clicks per top query from the API.
- Return actual zero-result query groups, not only the total count.
- Track immutable search and click events instead of overwriting one click field.
- Remove fabricated timelines, growth percentages, latency, uptime, recommendations, and index-rebalancing statements.
- Instrument actual request latency and uptime before displaying them.
- Add data-retention controls and query anonymization guidance for merchant privacy.

### Acceptance criteria

- Match percentages increase with similarity and are covered by tests.
- Irrelevant queries can produce genuine zero-result events.
- Dashboard values can be reconciled against raw database events.
- No metric or recommendation is displayed unless produced from real stored or monitored data.

## 11. Phase 6: Deployment, Reliability, And Operations

### Application configuration

- Reject default JWT, Shopify, database, Redis, encryption, and storage secrets at production startup.
- Replace wildcard CORS with explicit dashboard and approved storefront origins.
- Enable trusted-host validation and configure proxy trust explicitly.
- Disable or protect OpenAPI documentation in production.
- Add security headers: HSTS at the edge, CSP for the dashboard, `X-Content-Type-Options`, frame restrictions, and a referrer policy.
- Remove detailed internal exceptions from client responses while preserving trace IDs.
- Do not silently fall back from PostgreSQL to SQLite or from secure object storage to local files in production.
- Fail closed or enter a clearly degraded mode when Redis-dependent security controls are unavailable.

### Deployment assets

- Add a backend Dockerfile with a non-root user, health check, pinned runtime, and production server settings.
- Add separate API and Celery worker deployment definitions.
- Run `alembic upgrade head` as a controlled release step.
- Use a managed secret store or platform environment secrets.
- Use managed PostgreSQL with TLS, automated backups, and tested point-in-time restore.
- Persist or externally host ChromaDB; do not use ephemeral application storage.
- Configure dashboard routing without swallowing `/api` or widget asset requests.

### Observability

- Add structured JSON logs with request, tenant, job, and trace IDs; never log tokens or full query payloads by default.
- Add error reporting for API, dashboard, and worker failures.
- Measure request count, error rate, p50/p95 latency, rate-limit events, queue depth, sync duration, index failures, and search zero-result rate.
- Split liveness and readiness endpoints. Readiness must fail when required dependencies are unavailable.
- Alert on elevated 5xx rates, database failures, queue backlog, webhook failures, and backup failures.

### Runbooks

- Database restore and migration rollback.
- ChromaDB rebuild from PostgreSQL.
- Compromised API/widget key rotation.
- Shopify credential revocation and reconnect.
- Failed or stuck ingestion job recovery.
- Widget rollback and storefront incident response.

### Acceptance criteria

- Staging deploys from CI using the same artifacts intended for production.
- Backup restore and vector-index rebuild are tested successfully.
- Readiness fails when PostgreSQL is unavailable; liveness remains useful for orchestration.
- A load test meets the beta latency and error-rate targets without data leakage.

## 12. Phase 7: Beta Validation And Launch

### Pre-launch validation

- Run unit, integration, authorization, migration, widget browser, and end-to-end tests.
- Run static analysis, secret scanning, Python and npm dependency audits, and an external dynamic security scan against staging.
- Perform manual cross-tenant testing with at least two users and two stores.
- Test Shopify install, callback, first sync, webhook update/delete, reconnect, and uninstall.
- Test CSV and JSON ingestion with valid, malformed, oversized, duplicate, and malicious files.
- Test widget installation on at least Shopify plus one generic storefront.
- Complete accessibility and mobile-browser checks for the widget and dashboard.
- Publish privacy policy, terms, data-retention policy, support contact, and incident process.

### Controlled rollout

1. Internal staging with synthetic catalogs.
2. Private beta with 2-3 trusted merchants and manual onboarding.
3. Review two weeks of security, latency, relevance, and sync metrics.
4. Expand to 10-50 merchants only after all release gates remain green.

## 13. Release Gates

Public beta is **No-Go** if any of these conditions remain:

- Any authenticated user can access another tenant's resources.
- Any catalog or configuration value can execute HTML, CSS, or JavaScript in the widget.
- Shopify OAuth or webhooks can bypass state/HMAC validation.
- Private API keys are stored or returned in plaintext after creation.
- Upload size, filename, and content controls are missing.
- Product identity can collide between stores.
- Migrations cannot build the complete schema from an empty database.
- Backend, frontend, widget, and migration tests do not run in CI.
- Analytics displays fabricated or unreconciled production metrics.
- Production can start with default secrets or silently fall back to insecure dependencies.

Public beta is **Go** only when:

- All critical and high security findings are fixed and regression-tested.
- Cross-tenant tests pass for every merchant resource.
- Search relevance and latency meet documented beta targets.
- Shopify and file-ingestion end-to-end tests pass in staging.
- Monitoring, alerting, backups, restore, rollback, and incident runbooks are operational.
- Product claims match measured functionality and published service targets.

## 14. Suggested Work Breakdown

### Epic A: Tenant isolation

- A1 Store ownership migration
- A2 Composite product identity migration
- A3 Ownership-aware repository/service methods
- A4 Route authorization dependency
- A5 Cross-tenant regression suite

### Epic B: Credential security

- B1 Hashed and scoped API keys
- B2 One-time key reveal and rotation
- B3 Session/refresh-token design
- B4 Login throttling and audit trail
- B5 Production secret validation

### Epic C: Safe storefront widget

- C1 DOM-safe rendering
- C2 URL/config validation
- C3 Shadow DOM isolation
- C4 Public widget credential and domain controls
- C5 XSS and browser compatibility suite

### Epic D: Secure ingestion and Shopify

- D1 OAuth state and callback HMAC
- D2 Correct webhook verification and idempotency
- D3 Streaming upload limits and safe storage keys
- D4 Transactional ingestion jobs
- D5 Sync reconciliation and failure recovery

### Epic E: Search and analytics truthfulness

- E1 Score semantics and relevance threshold
- E2 Active-product filtering and index consistency
- E3 Relevance benchmark suite
- E4 Immutable event analytics
- E5 Real dashboard metrics and removal of mock claims

### Epic F: Production operations

- F1 Locked dependencies and CI
- F2 Container and worker deployment
- F3 Readiness, metrics, logging, and alerts
- F4 Backup/restore and index-rebuild runbooks
- F5 Staging security and load validation

## 15. Definition Of Done For Every Ticket

- Code is reviewed and tenant impact is documented.
- Request and response validation is explicit.
- Unit tests cover success and failure behavior.
- Integration tests cover database and external-service boundaries.
- Security-sensitive changes include abuse and cross-tenant tests.
- Database changes include forward migration, validation, and rollback notes.
- Logs and metrics are added without exposing sensitive data.
- Documentation and environment templates are updated.
- CI is green and staging verification is recorded.

## 16. Immediate First Sprint

The first sprint should contain only foundational release blockers:

1. Establish CI and a reproducible backend test environment.
2. Add store ownership and product external-ID migrations.
3. Implement ownership-aware dependencies and cross-tenant tests.
4. Convert API keys to hashed, scoped, one-time-reveal credentials.
5. Remove widget `innerHTML` rendering for all untrusted data and add XSS tests.
6. Remove production mock bypasses and default-secret acceptance.

Do not begin billing, advanced ranking, or broad customer onboarding until this sprint and its migration tests are complete.
