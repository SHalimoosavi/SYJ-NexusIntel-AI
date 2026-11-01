# Phase 2 Security Hardening — Progress Log

Branch: `feat/security-hardening`  
Baseline: `main` at `d2669b9264ed5de189facfcaafd3cd76f26cd965`  
Constraints: branch/PR only; never merge; no production data or credentials; no licensing or packaging.

## Current resume status

- Phase 1 PR #1 remains open and unmerged: `audit/baseline` → `main`.
- Phase 2 branch exists: `feat/security-hardening`. Current observed head before this progress update: `48d8f1d8ab44cef2cf714b737a1f3223b16095f8`.
- Tasks 1–3 have implementation and documentation committed. CI/runtime execution remains pending.
- Task 4 has started. Tenant service-level regression tests and a route-family isolation matrix are committed. Full HTTP endpoint/RBAC matrix is still pending.
- No production service, production data or production credential has been accessed.

## Git-history secret scan ledger

Repository `main` history contains 64 commits, oldest `c06218f640b5765746cf98916f3a92792992dfb7`, newest `d2669b9264ed5de189facfcaafd3cd76f26cd965`.

- Previously reviewed in the interrupted session: 48 newest commits, range `d2669b9264ed5de189facfcaafd3cd76f26cd965` through `762cb3f143c249313d5456473d0a0691047169c1`. Do not rescan.
- Remaining 16 oldest commits: `762cb3f143c249313d5456473d0a0691047169c1` (exclusive) through `c06218f640b5765746cf98916f3a92792992dfb7` (inclusive). The interrupted attempt did not produce usable findings. Mark UNVERIFIED; do not repeat.
- Coverage: 48/64 reviewed; 16/64 UNVERIFIED. No history scan was repeated in the resumed session.

## Confirmed secret findings

1. CRITICAL — hardcoded JWT signing secret in `backend/app/core/security.py:6`, commit `97d29d73178c44a0efd8da2c3d0e94298734b086`. Later moved to environment config in commit `827aad3701b3e25843d56804e6ee21e8e2dab55f`. Treat as compromised; deployment/reuse status unknown. Never retain in JWT verification keyring.
2. Historical frontend login debug/token handling is a disclosure vulnerability; no literal committed live bearer token was confirmed in the previously inspected history.
3. Environment variable names such as `DATABASE_URL`, `SECRET_KEY`, API keys or webhook secrets are not evidence of literal credential exposure.
4. No secret values are recorded in this file or chat.

## Task 1 — secret and API exposure

- [x] Evidence-based secret register and rotation checklist: `docs/audit/SECRET_EXPOSURE_REGISTER.md`.
- [x] Gitleaks defaults plus targeted literal assignment/JWT/private-key rules: `.gitleaks.toml`.
- [x] Redacted Gitleaks CI workflow: `.github/workflows/secret-scan.yml`.
- [x] Pre-commit Gitleaks hook: `.pre-commit-config.yaml`.
- [x] Production disables `/docs`, `/redoc`, `/openapi.json`; development enables.
- [x] API-doc policy unit tests added.
- [ ] CI scanner and tests executed. The historical JWT exposure may cause a true-positive full-history scan failure; no suppression has been added.

## Task 2 — rate limiting

- [x] Redis atomic sorted-set sliding-window limiter; local/desktop/test in-memory fallback.
- [x] Production fails closed with 503 when Redis is missing/unavailable.
- [x] Per-IP limits on all routes; stricter login/register/password-reset/refresh/invitation policies.
- [x] Per-user (300/minute) and per-organization (1,800/minute) quota buckets.
- [x] Login progressive delays and 15-minute lockout after 5 IP+email failures or 10 account-wide failures; dummy password check for unknown users.
- [x] 429 + Retry-After; rate-limit log entries omit raw IP/email/token.
- [x] Unit tests added for Redis path, fallback, fail-closed behavior, route policy, quota buckets, retry values and lockout.
- [ ] Python test suite and Redis integration executed.

## Task 3 — reverse proxy and network

- [x] Nginx selected for built-in request/connection limiting; Certbot for ACME TLS lifecycle.
- [x] Docker Compose, backend/frontend Dockerfiles, Nginx templates and proxy parameters added.
- [x] Self-hosted topology publishes only Nginx 80/443; backend has no host-published port; Redis is internal-only.
- [x] Explicit self-hosted trusted proxy IP `172.30.0.2`; Nginx overwrites forwarding headers.
- [x] Railway Uvicorn disables forwarded-header parsing rather than trusting wildcard/dynamic proxy IPs.
- [x] Strict CORS origin validation, Origin checks on cookie-authenticated unsafe operations, API/frontend headers, nonce CSP and HSTS configured.
- [x] Vercel/Railway and local/desktop deployment guidance in `docs/audit/NETWORK_HARDENING.md`.
- [ ] Docker/Nginx syntax, image build, TLS, browser CSP and spoofing tests executed.
- **Known limitation:** split Vercel/Railway backend still requires public ingress and remains directly reachable at the network layer. Not represented as private.

## Task 4 — attack and data-leak prevention

### Tenant isolation and IDOR

- [x] Source review of registered router families and their auth/tenant dependencies.
- [x] `docs/audit/TENANT_ISOLATION_MATRIX.md` documents route families, scoping controls, test status and residual concerns.
- [x] `backend/tests/test_tenant_isolation_services.py` adds isolated two-tenant SQLite tests for guessed organization, lead, note, activity, user, subscription, invitation and audit IDs; cross-tenant create/update/delete/read behavior; memory history; dashboard counts; and ORM audit-log immutability.
- [ ] Full HTTP endpoint/RBAC matrix tests across every registered route.
- [ ] Execute service and endpoint tests.

### Response schemas, errors and logging

- [x] Lead routes use explicit `LeadResponse`.
- [x] User/admin, organization, subscription, invitation, activity, note and audit-log routes already use explicit Pydantic response models.
- [x] Report generation no longer returns an absolute server filesystem path; it returns a report ID.
- [ ] Add explicit response models to remaining analytics/AI endpoints; inspect nested payloads for sensitive fields.
- [ ] Add generic production exception handler and application-wide log redaction.
- [ ] Verify no stack traces, password hashes, tokens, or PII in API responses/logs.

### Input, SSRF, JWT and audit

- [x] Source review confirms ORM parameterized queries in reviewed service paths; no raw SQL string construction found in reviewed code.
- [x] Domain validator blocks local/IP literals; outbound helper validates DNS answers and every redirect, limits redirects and disables automatic redirect following.
- [x] PDF output filenames are UUID-derived; HTML text is escaped.
- [x] JWT pins HS256, requires `kid`, issuer/audience, exp/iat/nbf, typed tokens and short access-token lifetime; refresh JTI is single-use; session version is revoked on logout/password change.
- [x] Audit ORM events reject update/delete; service descriptions are redacted and failure logs emit exception type only.
- [ ] Verify file-upload surface and LLM prompt-injection/data-exfiltration paths; network egress protections for DNS rebinding.
- [ ] Enforce audit-table DB role restrictions or DB-level append-only trigger/external sink.
- [ ] Add immutable audit event coverage for all sensitive mutations.

### Dependencies and database

- [x] PostgreSQL-only hosted config and TLS `sslmode=require` default are present; local SQLite restricted to local/test modes.
- [ ] Add pinned dev/security audit dependencies and run `pip-audit`, `npm audit`.
- [ ] Add Dependabot configuration.
- [ ] Document least-privilege DB role and backup/restore procedure.

## Task 5 — verification

- [ ] Add all security tests to CI.
- [ ] Run isolated brute-force, token tampering, IDOR, oversized payload and forwarded-header spoof simulations.
- [ ] Produce `docs/audit/SECURITY_POSTURE.md` with evidence and residual risks.

## Recent Task 4 commits

- Tenant service tests: `7d04bf33b9d7ca1f2463a798892283026dd59d0a`.
- Tenant route matrix: `48d8f1d8ab44cef2cf714b737a1f3223b16095f8`.
- Lead response schema: `ddae9d689941e45c677fb39f4ab2af4f3c8326bf`, import correction `74fe36ff9e9384f6112bbd3456af2c674209e7f8`.
- Report path disclosure fix/schema: `295e18ac21dcb70550171543efd1624d5c2014a6`, `31078fe4f9e91b72fd223d70cd0eceb4759fcd8b`, route/import `60325804442d050fada09fa0940866c4c324daed`, `abd2b6144b63548e839894fe15dc7b8482514e98`.

## Validation status

All Task 4 tests and source changes are authored but have not been executed. Docker, Redis, database and attack simulation runtime validation remains UNVERIFIED. Never claim fully secure.
