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
- Run `alembic upgrade head` as a one-off migration job.
- Start one worker process.
- Start one API instance with one Uvicorn worker while Chroma is embedded.
- Confirm `/health/live` and `/health/ready` both return `200`.

## 5. Validate Staging

- Run the full `docs/staging-validation-plan.md`.
- Confirm dashboard login, store creation, catalog ingestion, widget search, click analytics, and Shopify development-store sync.
- Capture evidence links/screenshots for each required check.

## Exit Gate

Do not start public beta until staging validation, backup restore, Chroma rebuild, and credential rotation drills are complete.
