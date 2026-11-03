# SYJ NexusIntel AI — Production Audit Report

**Audit baseline:** `main` at `d2669b9264ed5de189facfcaafd3cd76f26cd965`  
**Audit branch:** `audit/baseline`  
**Date:** 2026-11-01  
**Scope:** Static source, repository tree, README roadmap, available Git history, lockfile metadata and GitHub issues/PRs.  
**Execution limitation:** The audit runner could not clone GitHub because DNS/network access to `github.com` was unavailable. Application commands, dependency installation, runtime tests, frontend build and deployment probes were therefore **NOT RUN**. Runtime outcomes are marked **UNVERIFIED**, not passed.

## Executive summary

**Release verdict: NOT PRODUCTION-READY.** The repository contains a substantial SaaS/CRM foundation, but the code and repository evidence do not support the README's production-grade/live claims as a release decision. There are confirmed critical security defects, no automated test suite or CI workflow in the repository tree, no database migration system, and the current frontend is coupled to a hardcoded Railway API URL.

The highest-risk findings are:

1. **CRITICAL — historical JWT signing key committed in public Git history.** Commit `97d29d73178c44a0efd8da2c3d0e94298734b086` added a literal JWT secret to `backend/app/core/security.py`; commit `827aad3701b3e25843d56804e6ee21e8e2dab55f` later replaced it with `os.getenv("SECRET_KEY")`. The exposed value is intentionally not reproduced here. Rotate any environment that ever used it and invalidate existing tokens. History cleanup is a separate coordinated operation; this audit did not rewrite history.
2. **CRITICAL — login debugging exposes sensitive data.** `frontend/app/login/page.tsx:27-103` contains user-facing `alert()` calls that display the email, API response body and error details. The response body includes the access token on successful login.
3. **CRITICAL — browser token is JavaScript-readable.** `frontend/lib/auth.ts:8-38` and `frontend/app/login/page.tsx:82-83` store the bearer token in a normal cookie without `HttpOnly`, `Secure` or `SameSite` attributes. An XSS flaw or compromised script can extract the token.
4. **CRITICAL — organization administration is not tenant-scoped.** `backend/app/routers/organization.py:37-90` authorizes broad roles but does not constrain create/list/get operations to the caller's organization; `backend/app/services/organization_service.py:56-77` returns all organizations or fetches by arbitrary ID. An organization owner/manager can enumerate other tenants and a non-super-admin owner can create organizations.
5. **HIGH — OSINT/report target is untrusted network input.** `backend/app/routers/osint.py:34-67`, `backend/app/services/osint_service.py:85-123` and `backend/app/services/report_service.py:49-65` make outbound requests based on user-supplied domains and derive a PDF path from the supplied domain. No target allowlist, private/reserved IP rejection, redirect revalidation or safe filename mapping was found in the inspected path. This creates SSRF and path-manipulation risk.
6. **HIGH — schema creation is performed at import/startup.** `backend/app/main.py:124-129` calls `Base.metadata.create_all` and seeds roles at module import. No Alembic migration files/configuration are present in the recursive repository tree.
7. **HIGH — deployment configuration is hardcoded.** `frontend/lib/api.ts:3` and `frontend/lib/auth.ts:1-2` hardcode the Railway API URL; this blocks a clean configurable local/desktop deployment and makes environment separation difficult.
8. **HIGH — no tests or CI are present in the repository tree.** No test files, `.github/workflows`, Dockerfiles, compose files, or CI configuration were found at the audited commit.
9. **HIGH — revenue projections are heuristic and not time-normalized.** `backend/app/services/crm_service.py` derives sales velocity and multiplies current weighted forecast by 3/12 for quarterly/annual projections. These are not date-window forecasts and can mislead commercial decisions.
10. **HIGH — no complete dependency vulnerability or Python license verification was possible.** Frontend lockfile declares licenses for 490 package records; it includes LGPL-3.0-or-later libvips packages and MPL-2.0 packages. Python requirements are pinned mostly by version but have no lock metadata carrying license identifiers; see `DEPENDENCY_LICENSE_INVENTORY.md`.

The README documents a phased roadmap, but roadmap completion percentages and deployment-live badges are self-reported and were not independently verified. The repository currently has one branch (`main`), zero pull requests and zero issues returned by GitHub for this repository.

## Area scores

Severity is the highest material finding in each area, not a numeric maturity percentage.

| Area | Severity | Assessment |
|---|---|---|
| Security | **CRITICAL** | Historical JWT key exposure, readable token cookie, debug credential/token alerts, tenant administration boundary failure, SSRF/path risk |
| Backend | **HIGH** | Synchronous SQLAlchemy in FastAPI handlers, import-time schema mutation, no migrations, health endpoint does not check DB, weak operational safeguards |
| Frontend | **CRITICAL** | Login debug alerts expose sensitive response content; token stored in script-readable cookie; API origin hardcoded |
| AI / revenue intelligence | **HIGH** | Current scoring/agent path is predominantly deterministic heuristics; forecasts are simplistic and not validated against historical outcomes |
| Testing | **CRITICAL** | No test suite or test command found in repository tree; no evidence of automated integration/e2e coverage |
| DevOps | **HIGH** | No CI, Docker packaging, environment templates, backup/restore runbooks or observability configuration found |
| Licensing hygiene | **HIGH** | No formal LICENSE file; Python license metadata unverified; LGPL/MPL dependencies require notice/compliance review before binary distribution |

## 1. Architecture map

### Repository layout

The recursive tree at baseline commit contains root `.gitignore`, `README.md`, `backend/` and `frontend/`. The backend is divided into:

- `app/core/`: JWT/security, authentication dependencies, tenant helpers, RBAC and feature guards.
- `app/database/`: SQLAlchemy engine/session setup.
- `app/models/`: User, Organization, Role, Permission, Subscription, FeatureFlag, Lead, LeadNote, Activity, AuditLog, Invitation, AIUsage, AgentMemory and OSINTReport.
- `app/schemas/`: Pydantic request/response models.
- `app/routers/`: auth, users, organizations, invitations, leads, CRM, executive intelligence, OSINT, reports, activities, opportunities, agent memory, sales/multi-agent and related APIs.
- `app/services/`: business logic for users, organizations, subscriptions, feature flags, CRM, lead scoring, intelligence, OSINT, reports, memory, sales and agent orchestration.

The frontend uses Next.js App Router pages and React components under `frontend/app/` and `frontend/components/`, with API/auth helpers under `frontend/lib/`.

### Request/data flow

1. Browser loads the Next.js UI.
2. Next middleware checks whether a `token` cookie exists for selected protected routes. This is a presence check, not server-side JWT validation.
3. Client-side helpers read that cookie and attach `Authorization: Bearer <token>` to API requests.
4. FastAPI `/auth/login` authenticates email/password and issues a signed JWT containing `sub`, `user_id`, `organization_id` and `role_id`.
5. API dependencies decode the JWT and downstream routers/services use its organization claim to filter tenant records.
6. SQLAlchemy maps models to SQLite or PostgreSQL depending on `DATABASE_URL`.

Evidence: `frontend/middleware.ts:4-25`; `frontend/lib/auth.ts:8-38`; `backend/app/routers/auth.py:27-51`; `backend/app/core/dependencies.py:19-42`; `backend/app/database/database.py:7-31`.

### Multi-tenancy model

- `Organization` is the tenant root.
- `User.organization_id` and `Lead.organization_id` are foreign keys; the Lead tenant field is nullable.
- The JWT carries the tenant ID.
- Lead service and CRM analytics apply organization filters.
- A helper `tenant_filter` applies `model.organization_id == organization_id`.

This is **partial** tenant isolation, not a verified complete boundary. Organization CRUD is not tenant-scoped. The code also has more than one current-user dependency implementation: `app/core/auth.py` returns a database User object, while `app/core/dependencies.py` returns decoded JWT claims. Routers generally rely on the claims dictionary. Role lookup is based on the token's `role_id`; active-user status is not reloaded/checked by this dependency.

Evidence: `backend/app/core/tenant.py`; `backend/app/models/user.py`; `backend/app/models/lead.py`; `backend/app/core/dependencies.py:19-42`; `backend/app/routers/organization.py:37-90`; `backend/app/services/organization_service.py:56-77`.

### Authentication and authorization

- Password hashing: Passlib PBKDF2-SHA256.
- JWT: python-jose, HS256, 1,440-minute expiry.
- Backend expects an HTTP bearer token.
- Role guard resolves Role by `role_id` and compares role name.
- Feature guard checks organization feature flags.
- Frontend cookie is not HttpOnly and can be read by JavaScript.

No refresh-token rotation, server-side session revocation, MFA, login throttling or brute-force control was identified in the inspected implementation. Inactive-user revocation is not enforced by the claims-only dependency.

Evidence: `backend/app/core/security.py:7-62`; `backend/app/core/dependencies.py:19-42`; `backend/app/core/rbac.py`; `frontend/lib/auth.ts:8-38`.

### Database and migrations

SQLAlchemy declarative models are created through `Base.metadata.create_all(bind=engine)` during application module import. The database URL defaults to `sqlite:///./nexusintel.db` and accepts PostgreSQL URLs. No Alembic package, `alembic.ini`, migration directory, migration scripts, schema version table or upgrade/downgrade workflow appears in the recursive tree. `create_all` is not a substitute for production schema migrations.

Evidence: `backend/app/database/database.py:7-31`; `backend/app/main.py:124-129`; `backend/requirements.txt`; baseline recursive tree.

### Environment variables and external services

| Variable / endpoint | Purpose | Evidence / status |
|---|---|---|
| `SECRET_KEY` | HS256 JWT signing key; required at import | `backend/app/core/security.py:7-15` |
| `DATABASE_URL` | SQLite default or PostgreSQL connection | `backend/app/database/database.py:7-27` |
| `AI_LIMIT_BYPASS` | Bypasses AI usage quota when set to the literal string `true` | `backend/app/services/ai_usage_service.py` (environment switch in `enforce_ai_limit`); production must enforce this is unset/false |
| Railway API URL | Hardcoded frontend API origin | `frontend/lib/api.ts:3`, `frontend/lib/auth.ts:1-2` |
| Vercel origin | Explicit CORS allow-origin | `backend/app/main.py:144-148` |
| Google DNS / Cloudflare DNS | External DNS resolution | `backend/app/services/osint_service.py` |
| Target website HTTPS | WHOIS, DNS, TLS, headers, SEO and technology checks | `backend/app/services/osint_service.py`, `technology_service.py` |

No configurable LLM provider or model integration is evident in the dependency list or inspected intelligence services. Current "agent" orchestration composes deterministic local functions; it should not be marketed as autonomous LLM agents without further implementation and evidence.

## 2. Security findings

| ID | Severity | Finding | Evidence |
|---|---|---|---|
| SEC-01 | **CRITICAL** | Historical hardcoded JWT signing key in public Git history. Rotate any reused key, revoke tokens and plan history cleanup. | Commit `97d29d73178c44a0efd8da2c3d0e94298734b086`; removed in `827aad3701b3e25843d56804e6ee21e8e2dab55f` |
| SEC-02 | **CRITICAL** | Login debug alerts print email, response JSON and error details; success response contains bearer token. | `frontend/app/login/page.tsx:27-103` |
| SEC-03 | **CRITICAL** | JWT cookie is script-readable and lacks HttpOnly/Secure/SameSite flags. XSS or malicious browser script can steal bearer token. | `frontend/lib/auth.ts:8-38`; `frontend/app/login/page.tsx:82-83` |
| SEC-04 | **CRITICAL** | Organization create/list/get operations are not scoped to the authenticated tenant; arbitrary organization ID lookup is possible to allowed roles. | `backend/app/routers/organization.py:37-90`; `backend/app/services/organization_service.py:56-77` |
| SEC-05 | **HIGH** | OSINT requests accept a user-supplied domain and make outbound network requests without visible allowlist/private-address/redirect validation. | `backend/app/routers/osint.py:34-67`; `backend/app/services/osint_service.py:85-123` |
| SEC-06 | **HIGH** | PDF output filename is constructed from user-supplied domain. Validate host syntax and use a generated safe identifier; store outside web/static roots. | `backend/app/services/report_service.py:49-65` |
| SEC-07 | **HIGH** | JWT claim dependency does not reload User or reject `is_active=False`; token remains valid until expiry unless signing key is rotated. | `backend/app/core/dependencies.py:19-42`; `backend/app/models/user.py` |
| SEC-08 | **HIGH** | No rate limiter/login throttling is evident in routes or dependencies; OSINT and report endpoints can trigger expensive outbound work. | `backend/app/routers/auth.py:27-51`; `backend/app/routers/osint.py:34-67`; no limiter in dependency list |
| SEC-09 | **HIGH** | `AI_LIMIT_BYPASS=true` disables AI request quota enforcement. Add production startup guard and config validation. | `backend/app/services/ai_usage_service.py` |
| SEC-10 | **MEDIUM** | CORS uses wildcard methods and headers with a fixed origin allowlist; tighten methods/headers to required values. | `backend/app/main.py:144-148` |
| SEC-11 | **MEDIUM** | No secret-scanning workflow or verified repository-wide secret scan is present. The historical JWT leak demonstrates why this gate is required. | Baseline tree has no `.github/workflows`; historical commit above |
| SEC-12 | **UNVERIFIED** | SQL injection and XSS across every route/component were not exhaustively dynamically tested. ORM usage was seen in inspected paths; no proof of global safety. | Static-only scope |
| SEC-13 | **UNVERIFIED** | Dependency CVE status was not scanned because dependency resolution/network was unavailable. | `backend/requirements.txt`, `frontend/package-lock.json` |

### SQL injection, XSS and CSRF

The inspected service paths use SQLAlchemy ORM filters, not hand-built SQL strings. This is a positive observation, not a repository-wide proof. The frontend login debug output is an information disclosure issue. Token exposure through JavaScript-readable cookies increases the impact of any XSS. Since API requests attach a bearer header manually, classic ambient-cookie CSRF is less directly applicable to those API calls; however, the current cookie/middleware design is not a secure session architecture and needs redesign rather than a narrow CSRF patch.

### Prompt injection

No actual external LLM SDK/provider integration was identified in `backend/requirements.txt` or the inspected AI/revenue services. Therefore current prompt-injection exposure is **not applicable to the inspected implementation**. If LLM-based agents are added, external website content, OSINT results, lead notes and CRM text must be treated as untrusted data and isolated from system/developer instructions and tool permissions.

## 3. Backend and data findings

- **HIGH:** `Base.metadata.create_all` executes on import/startup; no migration history or controlled upgrade path.
- **HIGH:** synchronous SQLAlchemy engine/session and synchronous ORM calls are used in FastAPI route/service paths. This can block the event loop if converted to async endpoints without moving DB I/O to a threadpool or adopting async SQLAlchemy.
- **HIGH:** health route reports success without checking database connectivity; no readiness/liveness split.
- **HIGH:** `AI_LIMIT_BYPASS=true` skips subscription AI usage enforcement; ensure production configuration cannot enable this accidentally and add a startup guard/alert.
- **MEDIUM:** no structured logging, request correlation IDs, metrics, tracing, retry policy or background job queue found.
- **MEDIUM:** lead service commits lead and activity separately; partial failure can leave lead created without activity log. Use transaction boundaries.
- **MEDIUM:** nullable tenant IDs on some records and absent global tenant enforcement increase the risk of orphaned/unscoped data.
- **UNVERIFIED:** N+1 queries and index sufficiency were not measured against production data. Lead organization index exists; broader index coverage requires query plans and data volume.

Evidence: `backend/app/main.py:124-129`; `backend/app/database/database.py:7-31`; `backend/app/models/lead.py`; `backend/app/services/lead_service.py:97-151`; `backend/app/main.py` health handler.

## 4. Frontend findings

- **CRITICAL:** debug alerts in login disclose email and full API response.
- **CRITICAL:** token cookie lacks HttpOnly/Secure/SameSite.
- **HIGH:** API base URL is hardcoded to Railway; no `NEXT_PUBLIC_API_BASE_URL` or runtime config.
- **HIGH:** API helpers throw generic errors; some executive API methods return `response.json()` without checking `response.ok`.
- **MEDIUM:** no dedicated test script, accessibility test tooling or bundle analyzer is declared.
- **UNVERIFIED:** actual build, type-check, lint and accessibility results because dependencies could not be installed/run in this audit environment.

Evidence: `frontend/app/login/page.tsx:27-103`; `frontend/lib/auth.ts:8-38`; `frontend/lib/api.ts:3, 267-285`; `frontend/package.json`.

## 5. AI and revenue-intelligence correctness

The code currently implements deterministic heuristics rather than a verifiable LLM agent runtime:

- Lead score uses hardcoded industry/company-size/value thresholds (`backend/app/services/lead_service.py`).
- Intelligence score is a weighted combination of TLS/security headers and SEO metadata (`backend/app/services/intelligence_service.py`).
- Sales priority and suggested follow-up are static rule tables (`backend/app/services/sales_agent_service.py`).
- Multi-agent service sequentially calls intelligence/opportunity/sales functions and stores serialized output (`backend/app/services/multi_agent_service.py`).
- CRM forecast multiplies current weighted pipeline by 3 or 12 and computes velocity from aggregate counts; it does not use historical conversion, time windows, seasonality or calibration (`backend/app/services/crm_service.py`).
- OSINT scans use third-party DNS and arbitrary HTTPS targets, with network failures converted to error dictionaries.

**Assessment:** useful prototype logic, not validated decision-grade revenue intelligence. Add deterministic test fixtures, historical backtesting, confidence intervals, source timestamps, explicit missing-data handling and a clear distinction between measured facts and heuristics.

## 6. Testing and CI

The recursive tree contains no tests directory/files, no pytest configuration, no frontend test script, no Playwright/Cypress configuration and no GitHub Actions workflow. `frontend/package.json` scripts are `dev`, `build`, `start`, `lint`; `backend/requirements.txt` does not declare pytest, HTTPX test client or coverage tooling.

**Test coverage: NOT ESTABLISHED.** No tests were run. A missing test suite is not a zero-percent measurement; it means coverage is unknown and there is no checked-in automated verification gate.

## 7. DevOps and deployability

### Repository evidence

- Backend has `Procfile` and `railway.json`.
- Frontend has Next.js config and a package lock.
- README describes Vercel + Railway, but that is documentation, not current live deployment evidence.
- No Dockerfile, compose file, CI workflow, environment example, backup/restore script, migration workflow or monitoring configuration was found.
- Frontend API URL is hardcoded to Railway, so local UI cannot be configured to target a local API without source modification.

### Exact local commands to attempt

Backend (Linux/macOS shell; run from repository root):

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export DATABASE_URL="sqlite:///./nexusintel.db"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend (second terminal):

```bash
cd frontend
npm ci
npm run lint
npm run build
npm run start
```

Expected static prerequisites: backend requires `SECRET_KEY` at import; `DATABASE_URL` defaults to SQLite; frontend scripts are defined. The frontend will still call the hardcoded Railway URL unless code is changed, so a locally started backend will not automatically be used.

### Execution result

**NOT RUN / UNVERIFIED.** This audit environment failed to resolve `github.com` during clone (`Could not resolve host: github.com`). This is an audit-runner network limitation, not an application build failure. I cannot honestly report build success or an application-specific build failure without running the commands in a network-enabled environment. Provider-side Vercel/Railway status is also **UNVERIFIED**; no provider credentials or live health checks were available.

## 8. Licensing hygiene

- No root `LICENSE` file is present in the baseline tree. README has a copyright/rights-reserved statement, but that is not a complete software license instrument.
- Frontend `package-lock.json` contains **490 package records** with a declared `license` field. Summary: MIT 387; Apache-2.0 31; LGPL-3.0-or-later 10; MPL-2.0 13; ISC 29; BSD-2-Clause 7; BSD-3-Clause 3; plus BlueOak-1.0.0, Python-2.0, CC-BY-4.0, CC0-1.0, 0BSD and compound expressions. Full package/version/license inventory is in `DEPENDENCY_LICENSE_INVENTORY.md`.
- LGPL-3.0-or-later is declared for `@img/sharp-libvips-*` platform packages; compound LGPL expressions appear for `@img/sharp-wasm32` and `@img/sharp-win32-*`. These are not automatically a prohibition on proprietary distribution, but they require legal review and compliance planning for shipped binaries.
- MPL-2.0 is declared for `axe-core` and `lightningcss` platform packages. Preserve required notices and review source-disclosure obligations for modifications to MPL-covered files.
- Python direct dependencies in `backend/requirements.txt` have no lockfile metadata here that establishes exact SPDX licenses. They are all listed as **UNVERIFIED** in the inventory. Do not assume permissive licensing until verified against the exact distributions and their license texts.
- No GPL/AGPL package was observed in the frontend lockfile's declared license fields; this is not a full legal conclusion. Transitive and runtime/bundled artifacts must be re-scanned during packaging.

## 9. Prioritized fix list

| Priority | Work | Why | Effort |
|---|---|---|---|
| P0 | Rotate historical JWT secret wherever reused; invalidate sessions; audit all environments | Public history contains signing key | S |
| P0 | Remove login debug alerts and ensure tokens/responses are never logged or displayed | Direct credential disclosure | S |
| P0 | Replace JS-readable token cookie with secure HttpOnly session strategy; add server-side session validation/revocation | Token theft and inactive-user access | M |
| P0 | Enforce tenant boundary for every organization/user/lead/CRM/feature/invitation/report route; add cross-tenant tests | Cross-tenant disclosure and unauthorized tenant creation | L |
| P0 | Validate OSINT targets, reject private/reserved/link-local addresses, revalidate redirects/DNS, constrain outbound network and use safe report IDs | SSRF and path manipulation | M |
| P0 | Add automated security, unit and integration test gate for P0 fixes | No regression evidence | L |
| P1 | Add Alembic migrations; remove import-time schema mutation; add startup/readiness checks | Safe upgrades and deployability | M |
| P1 | Add env schema/example and configurable frontend API origin | Environment separation/local mode | S |
| P1 | Add rate limiting, request size/timeouts, structured logs and correlation IDs | Abuse resistance and operability | M |
| P1 | Backtest revenue forecasts; separate heuristic estimates from measured metrics | Commercial correctness | L |
| P1 | Add CI: lint, type-check, unit/integration, secret scan, dependency audit, build | Repeatable releases | M |
| P1 | Verify Python dependency licenses and generate complete notices; review LGPL/MPL distribution duties | Proprietary distribution hygiene | M |
| P2 | Add accessibility/e2e tests, bundle analysis and UX error/empty states | Product quality | M |
| P2 | Add backups/restore drills, metrics/tracing, alerting and operational runbooks | Production operations | M |
| P2 | Prepare local database abstraction and desktop/mobile packaging architecture | Commercial installability | L |

## 10. Limitations and unverified items

- No runtime test/build/install was executed; commands above are a reproducible test plan only.
- No live Vercel/Railway status, database, production logs, environment configuration or backup was accessed.
- No database dump was available to validate actual schema, data volume, indexes or tenant contamination.
- No authenticated dynamic cross-tenant test was run.
- No complete CVE scan or SBOM generation was run.
- Historical key exposure is confirmed from the commit patch; whether that exact key remains deployed or was reused elsewhere is **UNVERIFIED**.
- Full Python license texts and package provenance require a dependency resolution/SBOM step in a network-enabled environment.
- Legal interpretation of third-party licenses and commercial EULA terms requires qualified legal review.

## Final verdict

The codebase is a **feature-rich prototype / early SaaS foundation**, not a release-ready commercial product. The most important blockers are security boundaries and reproducible verification, not desktop packaging. Do not ship this build or onboard paying customers until all P0 items are fixed and proven by tests. Phase 1 is documentation-only; no application code or dependencies were changed.
