# Staging Deployment Next Steps

Use this checklist after merging production-readiness changes and before public launch.

## 1. Provision Staging Infrastructure

- PostgreSQL with TLS, automated backups, and a non-shared staging database.
- Redis with TLS, reachable only by API and worker services.
- S3-compatible object storage with TLS and a private uploads bucket.
- Persistent Chroma volume mounted at `/data/chroma`.
- HTTPS domains for API and dashboard.
- Reverse proxy that blocks public access to `/metrics`.

## 2. Prepare Secrets

- Copy `smartsearch-api/.env.staging.example` to the deployment secret store.
- Replace every placeholder value.
- Generate `SECRET_KEY` with at least 32 random characters.
- Generate a random `BETA_INVITE_CODE` with at least 16 characters and share it only with approved merchants.
- Generate `SHOPIFY_ENCRYPTION_KEY` with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

- Copy `dashboard/.env.staging.example` into the dashboard deployment environment.

## 3. Run Preflight

From `smartsearch-api`:

```bash
python scripts/preflight_production_env.py --env-file .env.production
```

Do not deploy until the preflight passes.

## 4. Deploy API And Worker

- Build one immutable API image from `main`.
- Download the matching `container-image-evidence-<commit>`, `postgres-recovery-evidence-<commit>`, and `dashboard-browser-report-<commit>` CI artifacts and attach them to the release record.
- Run `alembic upgrade head` as a one-off migration job.
- Start one worker process.
- Start one API instance with one Uvicorn worker while Chroma is embedded.
- Confirm `/health/live` and `/health/ready` both return `200`.

## 5. Validate Staging

- Run the full `docs/staging-validation-plan.md`.
- Configure the GitHub `staging` environment with a `BETA_INVITE_CODE` secret, then run the **Staging validation** workflow with the deployed API and dashboard URLs.
- Download and retain the `staging-validation-evidence`, `zap-dashboard-report`, and `zap-api-report` artifacts with the release record. They contain sanitized functional/load outcomes and passive security findings.
- Confirm dashboard login, store creation, catalog ingestion, widget search, click analytics, and Shopify development-store sync.
- Confirm uninvited registration is rejected and an approved beta invite can create an account after accepting the published terms.
- Confirm `/privacy`, `/terms`, `/data-retention`, and `/support` load from the deployed dashboard domain.
- Confirm password-verified account deletion removes owned stores and their derived Chroma collections.
- Capture evidence links/screenshots for each required check.

## Exit Gate

Do not start public beta until staging validation, backup restore, Chroma rebuild, and credential rotation drills are complete.
