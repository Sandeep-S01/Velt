# Data Retention Policy Draft

This draft is not legal advice. Review with counsel before publishing.

## Default Retention

- Merchant account data: retained while the account is active.
- Catalog data: retained while the store is active.
- Search query logs: retain for the merchant analytics window, default 180 days.
- Click events: retain for the merchant analytics window, default 180 days.
- Raw uploaded files: delete or quarantine after ingestion, default 30 days.
- Integration credentials: retained while the integration is active.
- Backups: retain according to the infrastructure backup schedule, default 30 days.

## Deletion

When a merchant requests deletion, remove account-owned stores, products, API keys, widget tokens, integration tokens, query logs, click events, and derived Chroma collections. Backups expire through the backup lifecycle unless immediate backup deletion is legally required and operationally supported.

## Minimization

Do not store unnecessary shopper personal data in query logs. Avoid logging full payloads or secrets. Store only analytics fields needed to provide merchant-facing reports.

## Review

Review retention settings quarterly and before expanding beyond private beta.
