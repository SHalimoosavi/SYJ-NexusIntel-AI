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
- [x] Static route contract test added: every documented non-public API route must include get_current_user directly or through RBAC/feature dependencies; all documented API routes must declare response_model.
- [ ] Full HTTP-level two-tenant IDOR/RBAC tests and execution remain pending.

### Response schemas, errors and logging

- [x] Lead routes use explicit `LeadResponse`.
- [x] User/admin, organization, subscription, invitation, activity, note and audit-log routes already use explicit Pydantic response models.
- [x] Report generation no longer returns an absolute server filesystem path; it returns a report ID.
- [x] Explicit response models added across all registered documented API routes, including nested multi-agent, OSINT, analytics, auth and mutation responses. Contract test asserts complete coverage.
- [x] Report generation returns a report ID rather than an absolute filesystem path; legacy JSON bearer-token response schema removed.
- [x] Generic unhandled-exception response added; exception text/stack data suppressed from logs and log messages redacted for bearer/JWT/secret/email/IP/phone patterns.
- [x] Response-model tests assert password hashes, session tokens and tenant IDs are absent from the relevant user/lead contracts.
- [ ] Execute response and log-redaction tests; invitation create response still returns a one-time invitation token to the authorized creator (intentional, documented exception).

### Input, SSRF, JWT and audit

- [x] Source review confirms ORM parameterized queries in reviewed service paths; no raw SQL string construction found in reviewed code.
- [x] Domain validator blocks local/IP literals; outbound HTTPS pins connections to validated public DNS IPs, preserves hostname TLS validation, and manually revalidates redirects.
- [x] PDF output filenames are UUID-derived; HTML text is escaped.
- [x] JWT pins HS256, requires `kid`, issuer/audience, exp/iat/nbf, typed tokens and short access-token lifetime; refresh JTI is single-use; session version is revoked on logout/password change.
- [x] Added JWT tests for tampering, unknown kid, algorithm mismatch, refresh JTI replay and session-version revocation.
- [x] Audit events attribute actors for lead, note, activity, invitation, organization, subscription and AI-usage mutations; user-management mutations already log events.
- [x] SQLAlchemy audit ORM events reject update/delete; PostgreSQL trigger and app-role privilege script supplied.
- [ ] Apply DB role/trigger using DBA identity and test tamper attempts against PostgreSQL; ORM-only hooks are not a DB security boundary.
- [x] Add actor-attributed audit events for sensitive tenant mutations and AI usage; PostgreSQL trigger/role enforcement remains pending DBA application.

### Dependencies and database

- [x] PostgreSQL-only hosted config and TLS `sslmode=require` default are present; local SQLite restricted to local/test modes.
- [x] Added pinned development tooling (`requirements-dev.txt`) and pinned PostgreSQL driver.
- [x] Added weekly pip/npm/GitHub Actions Dependabot updates.
- [x] Added dependency audit workflow for pip-audit and npm audit.
- [x] Documented least-privilege roles, PostgreSQL TLS, backup and isolated restore drill.
- [ ] Execute dependency audit workflow; provision DB roles and run backup/restore drill.

## Task 4 completion record (2026-11-01)

- Added two-tenant service regression coverage for IDOR/guessed IDs across organizations, leads, notes, activities, users, invitations, subscriptions, audit logs, agent memory and dashboards. Added route dependency/response-model contract tests. These are committed but not executed.
- Added explicit Pydantic response models across all documented API routes; added a static contract test to fail if a documented route lacks a response model or database-auth dependency (except explicitly public auth/invitation routes).
- Added generic 500 handler, log redaction, actor-attributed audit events, UUID report identifiers, input size/extra-field constraints and pinned-DNS outbound HTTPS.
- Added PostgreSQL audit trigger SQL, DB operations/backup guide, Dependabot and dependency audit workflow. The SQL is supplied but not applied.
- Task 4 code commits include `7d04bf33b9d7ca1f2463a798892283026dd59d0a`, `48d8f1d8ab44cef2cf714b737a1f3223b16095f8`, `fe5ec1d0e8456bd0822237ef7fbbe989e594d3b7`, `2127c734b07d7a89a03c3d8f922061a264c985df`, `f0d0c9ea2fe6e8d975a5d0a29629fcaeb9a0b8bc`, `dff6dbdea8f3db4649eea6c17f5d136b10369af1`, `48d3db53f17e8aefad81f7f5ff135dfedcb12e4c`, `c4c79933aa265800bb5500695487589b952846e4`, `d59397b4339a6bba248eee4191b4b18be1ea6fa9`, `54d8c8359ed0dfa84ac64d44c9f5a21257c521e7`, `0d1040010ca5caf99a7eb74dcf8ec384446b2a9a`, `cd37ba8234fd0a8ee384798c3c616d1a61fd26d7`.
- Remaining explicit risks: no full HTTP IDOR test run, no PostgreSQL DBA application of trigger/privileges, no egress firewall, no app-level streaming body cap, and no automated backup schedule.

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


## Task 4 implementation record (2026-11-01)

- Added tenant A/B fixture coverage for organizations, leads, users, notes, activities, agent memory, invitations, subscriptions and audit logs; API-level guessed-ID tests exercise leads, notes, activities, users, organizations and subscriptions.
- Added recursive FastAPI dependency inventory asserting every non-public API route depends on the current-user dependency. Added analytics-service tests and owner role-escalation/super-admin route tests. Full endpoint coverage limits are explicit in `TENANT_BOUNDARY_MATRIX.md`.
- Added explicit response models/constraints for leads and agent memory; activity/note response schemas are constrained; existing dashboard, CRM, OSINT, technology, intelligence, sales, audit, user, invitation, subscription and report response models were reviewed. Removed tenant/actor foreign keys from user/invitation/audit responses and removed absolute PDF path from report response. Invitation creation still returns a one-time opaque invitation bearer token to the authorized creator; list responses omit it.
- Added `RedactingLogFilter` and generic 500 handling in `backend/app/main.py`; redaction covers email, phone, bearer/JWT and credential assignments. No exception trace is emitted to client or application log.
- Added AST guard against f-string/format-built SQL, static upload endpoint guard, frontend raw-HTML injection guard, and SSRF tests for private DNS and redirects. Source review shows deterministic multi-agent orchestration and no current external LLM SDK integration; future LLM safety requirements and DNS-rebinding risk are in `AI_INPUT_SECURITY.md`.
- Added JWT lifecycle route tests for logout revocation, refresh-token replay detection and password-change revocation; added brute-force lockout and generic unknown/wrong credential response tests.
- Added `backend/sql/audit_log_immutability.sql` and `docs/audit/DATABASE_OPERATIONS.md`. ORM tests reject audit-log update/delete; the PostgreSQL trigger, runtime grants, database role separation, backup schedule and restore drill are operator actions and remain unverified.
- Added `backend/tests/test_tenant_isolation.py`, `test_auth_sessions.py`, `test_jwt_rotation.py`, `test_response_models.py`, `test_security_controls.py`, `test_static_security.py`, `test_log_redaction.py`, and expanded `test_input_validation.py`. Sensitive AI usage, organization/subscription creation, invitation, lead, note, activity, login/logout and password-change events now carry actor attribution where applicable.
- Added `.github/workflows/security-ci.yml`, `.github/workflows/dependency-audit.yml` (already present on branch), `.github/dependabot.yml`, and pinned test dependencies. Python and npm dependency audits run separately to avoid duplicate CI work.
- Added `docs/audit/TENANT_BOUNDARY_MATRIX.md`, `docs/audit/AI_INPUT_SECURITY.md`, and `docs/audit/DATABASE_OPERATIONS.md`.
- No backend test suite, Docker/Nginx deployment, Redis integration, PostgreSQL role/trigger, or real attack simulation has been executed locally. GitHub Actions runs were observed queued/in progress; final outcomes are pending.

## Repository policy incident

Two helper files were accidentally created on `main` because the branch argument was omitted on one GitHub file-create operation. They were immediately deleted in compensating commits. The current `main` tree has those files removed, but its history contains these four commits:
- Added `backend/app/core/logging_security.py`: `f9d78ce69f579e6a63468321b12dee1be8dd3ed6`
- Added `backend/tests/test_log_redaction.py`: `346819a75bfb8baccf137972a218ffdcd6b94935`
- Deleted helper module: `010a17619991f9162b2ccac73a821aa9d4115a53`
- Deleted test file: `e51373d276b443581367f2c19aa291ebf2a042d3`

This violated the branch-only constraint. No application behavior remains changed on `main` from those files; the commit history is not rewritten. No further writes to `main` will be made. All subsequent changes are explicitly targeted to `feat/security-hardening`.

## Latest CI observation

At the time of this update, the branch had active/queued Security CI, Dependency Audit and Secret Scan runs. The earlier diff-only Gitleaks action reported success, which is not sufficient evidence that the historic key was scanned. The secret workflow now also runs pinned Gitleaks CLI against the complete Git history with redacted reporting; expect it to flag the known historical JWT key. Full-history scan result is pending.

