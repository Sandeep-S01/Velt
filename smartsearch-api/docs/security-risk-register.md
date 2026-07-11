# Security Risk Register

Date: 2026-07-11

## Open Risks

### `PYSEC-2026-311` - ChromaDB pre-auth code injection advisory

- Package: `chromadb==1.5.9`
- Status: Accepted for private beta only
- Fixed version: None available at review time
- Application usage: embedded `chromadb.PersistentClient`
- Exposure decision: Chroma HTTP server must not be exposed publicly, to merchants, or to the dashboard network.
- Required controls:
  - Keep Chroma bound to local process or private volume only.
  - Do not run `chroma run` or expose Chroma API ports in production.
  - Keep API and worker containers as the only processes allowed to access the Chroma data path.
  - Restrict `/metrics` and runtime admin endpoints at the reverse proxy.
  - Re-run `pip-audit` weekly and remove the CI ignore once a fixed version is available.
- Public launch condition: either upgrade to a non-vulnerable Chroma release, replace Chroma with a managed/private vector service, or complete a formal risk acceptance for the exact deployment topology.

## Closed Risks

### `python-jose` transitive `ecdsa` advisory

- Previous risk: `ecdsa==0.19.2` timing-side-channel advisory with no planned fix.
- Resolution: replaced `python-jose` with `PyJWT==2.13.0` because Velt uses HS256 JWTs and does not need ECDSA support.
- Verification: backend auth workflow tests pass and `pip-audit` no longer reports `ecdsa`.

### `pytest` advisory

- Resolution: upgraded development dependency to `pytest==9.0.3`.

### `pip` advisory in local tooling

- Resolution: local venv upgraded to `pip==26.1.2`; CI runner should install the latest pip before dependency install.
