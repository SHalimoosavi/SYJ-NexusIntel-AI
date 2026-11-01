# Phase 2 Security Hardening — Progress Log

Branch: `feat/security-hardening`  
Baseline: `main` at `d2669b9264ed5de189facfcaafd3cd76f26cd965`  
Rules: branch/PR only; never merge; no production data or credentials; no licensing or packaging.

## Resume state (2026-11-01)

- The requested progress file did not exist on `feat/security-hardening`; this is the first durable resume record.
- Existing branch `feat/security-hardening` exists and contains prior security/auth/tenant/input/rate-limit implementation commits. Latest observed branch head before this progress entry: `e12fd11f1495ce4f48fff93273639d5c08504bee`.
- Existing audit baseline docs are on `audit/baseline`: `AUDIT_REPORT.md`, `DEPENDENCY_LICENSE_INVENTORY.md`, `RELEASE_PLAN.md`, `ROADMAP_STATUS.md`. No Phase 2 progress file was present.
- Open PR #1 remains the Phase 1 audit PR from `audit/baseline` to `main`; no merge was performed.
- Phase 2 work already present on `feat/security-hardening` includes JWT `kid` keyring, active-user/database-derived authorization, organization scoping, domain validation/SSRF controls, cookie/session changes, CORS and basic in-process rate limiting, and several tests. These are code-presence observations, not runtime verification.

## Git-history secret scan ledger

Repository `main` history currently contains 64 commits, oldest `c06218f640b5765746cf98916f3a92792992dfb7`, newest `d2669b9264ed5de189facfcaafd3cd76f26cd965`.

- Previously inspected in the interrupted session: newest 48 commits, range `d2669b9264ed5de189facfcaafd3cd76f26cd965` through `762cb3f143c249313d5456473d0a0691047169c1`. Earlier inspection used 3 groups of 16 rather than the requested groups of 25. Do not rescan these commits.
- Remaining oldest 16 commits: `762cb3f143c249313d5456473d0a0691047169c1` (exclusive boundary) through `c06218f640b5765746cf98916f3a92792992dfb7` (inclusive). The interrupted prior attempt to inspect this remainder did not leave a usable result; record as UNVERIFIED and do not repeat it under the no-repeat rule.
- Total history coverage: 48/64 reviewed previously; 16/64 UNVERIFIED. No commit has been re-reviewed in this resumed session.
- No secret values are recorded here. Only paths, commit IDs, line locations where confirmed, and secret types are permitted.

## Findings confirmed so far

1. **CRITICAL — historical JWT signing secret**: hardcoded in `backend/app/core/security.py` in commit `97d29d73178c44a0efd8da2c3d0e94298734b086`; moved to environment configuration in `827aad3701b3e25843d56804e6ee21e8e2dab55f`. Treat as compromised; rotation/deployment usage is unknown. Never retain this key in any `kid` verification set.
2. **HIGH — token exposure in frontend login history/current baseline**: login debug code historically surfaced response details and token-bearing response fields; current hardening branch has removed alert/debug output from `frontend/app/login/page.tsx` and moved toward HttpOnly cookies. Validate browser integration and cookie topology before release.
3. **Potential exposure classes requiring evidence before final classification**: JWT/session tokens in historical frontend code; database URL and generic deployment secrets referenced in docs/config. A reference to an environment variable is not itself a leaked secret. Do not mark DATABASE_URL, webhook or API credentials as leaked without an actual literal value in tracked history.
4. Earlier broad regex scan matched ordinary variable names, schema/OpenAPI JSON and documentation references. Those are false positives, not proof of secrets. The previous scan output was truncated/over-redacted; exact additional secret findings remain UNVERIFIED.

## Tasks

### Task 1 — secret and API exposure
- [x] Resume branch and audit-doc inventory checked.
- [x] Create this progress log before continuing.
- [x] Publish evidence-based secret register and rotation checklist (one confirmed historical JWT secret; other credential classes not confirmed in reviewed commits; 16 older commits remain UNVERIFIED).
- [x] Add Gitleaks default + targeted high-entropy assignment/JWT/private-key rules and redacted GitHub Actions scan. Scanner execution is pending CI.
- [x] Add pre-commit Gitleaks hook with redacted output.
- [x] Disable /docs, /redoc and /openapi.json by default in production; development enables them.
- [x] Add unit tests for production/prod/dev docs configuration; execution remains pending.

### Task 2 — rate limiting
- [x] Redis-backed shared sliding-window limiter with local/desktop/test in-memory fallback; production fails closed if Redis is missing/unavailable.
- [x] Per-IP limits on every route; stricter login/register/password-reset/refresh/invitation-accept policies and baseline limits for all other auth routes.
- [x] Authenticated per-user (300/min) and per-organization (1,800/min) quota buckets.
- [x] Login progressive delay and temporary lockout (5 IP+email failures; 10 account-wide failures) with dummy password verification for unknown users.
- [x] 429 responses include Retry-After; rate-limit logs contain method and route group only, no email/IP/token.
- [x] Tests added for sliding windows, Redis atomic path, local fallback, fail-closed production behavior, route policies, tenant quota buckets, retry values and login lockout. Execution remains pending.

### Task 3 — reverse proxy/network
- [x] Recommend Nginx (built-in request/connection limiting) and add Docker Compose topology.
- [x] Self-hosted Compose backend has no published host port; only Nginx publishes 80/443. Railway split-hosting direct reachability remains a documented limitation.
- [x] Nginx config adds per-IP API/auth rate zones, connection caps, 10 MB body cap, slow-client/upstream timeouts and gzip.
- [x] Self-hosted backend trusts only static Nginx IP; Railway start command disables forwarded-header parsing and trusts loopback only. Spoofing tests remain pending.
- [x] API and frontend security headers, strict HTTPS CORS allowlist, cookie Origin checks, nonce CSP, HSTS and banner suppression configured.
- [x] Vercel/Railway and local/desktop configurations and limitations documented.

### Task 4 — attack/data leak prevention
- [ ] Endpoint-wide tenant/IDOR/RBAC test matrix.
- [ ] Explicit response schemas and production-safe errors.
- [ ] Logging redaction; upload/query/SSRF/XSS/LLM input review.
- [ ] JWT refresh rotation, revocation on logout/password change.
- [ ] pip-audit/npm audit, pinned dependencies, Dependabot.
- [ ] Database least privilege/SSL/backup restore note.
- [ ] Immutable/tenant-independent audit log controls.

### Task 5 — verification
- [ ] Security tests in CI.
- [ ] Isolated attack simulations (no real production data/credentials).
- [ ] `SECURITY_POSTURE.md` with controls, evidence and residual risks.

## Task 1 completion record (2026-11-01)\n\n- Confirmed hardcoded JWT signing key location: `backend/app/core/security.py:6` in commit `97d29d73178c44a0efd8da2c3d0e94298734b086`. No value recorded.\n- Added `docs/audit/SECRET_EXPOSURE_REGISTER.md` with rotation actions and explicit UNVERIFIED coverage boundary.\n- Added `.gitleaks.toml`, `.github/workflows/secret-scan.yml`, `.pre-commit-config.yaml`. Prior naive keyword scan was over-broad; the new custom rule requires a literal assignment and minimum length/entropy; Gitleaks default rules remain enabled. CI scans full Git history and is expected to flag the known historical key until the exposure is addressed through a separately approved history policy. Output is configured redacted.\n- Added `backend/app/core/api_docs.py` and wired it into `backend/app/main.py`; production/prod disables docs, ReDoc and OpenAPI schema. Added `backend/tests/test_api_docs.py`.\n- Commits for Task 1: `ab8123bb02942537fa4666fa3891b856b4e4f690`, `7a8060e920f45caf3066f4019a7aaf6b8f957014`, `e883b3a34dce1acc3181132410af67161060e5c1`, `c1531664e5a41505f15050a5e9b24d0c65d2ffbb`, `08f19f6bd17019049d4327663aa271169ed2df77`, `896bfbaab88d6e16c9e82a20ec644d9621203e56`, `6727a39970143706041086871e24afe342d77946`, `520e562a248ac6a8fae1c8d976d69178fe9740d5`.\n- Tests have been authored but not executed. Gitleaks CI has not yet run.\n\n## Task 2 completion record (2026-11-01)\n\n- Replaced the process-only limiter with Redis sorted-set sliding windows using an atomic Lua script. Redis keys are SHA-256 hashed; no raw IP, email, user or organization identifier is written to Redis key names.\n- In-memory fallback is allowed only for APP_ENV development/dev/local/desktop/test. Production without a working REDIS_URL returns 503 rather than silently using process-local counters. Production deployment must provision Redis before enabling this branch.\n- Every request is rate-limited by IP (default 120/minute). Auth endpoints have stricter path budgets; login is 10/15 minutes, register and password-reset 3/hour, refresh 10/minute, invitation accept 5/hour; all other /auth routes 20/minute.\n- Authenticated requests additionally consume 300/user/minute and 1,800/organization/minute buckets. Quota responses use 429 + Retry-After.\n- Login failures use per-IP+email and account-hash counters, progressive delays capped at 2 seconds, and 15-minute lockout after 5 same-IP/email failures or 10 account-wide failures. Unknown accounts perform a dummy password hash check to reduce timing-based enumeration.\n- Added pinned `redis==5.2.1`. Added/expanded rate-limit and auth dependency tests.\n- Relevant implementation commits: `752a77651aa0b47451467617bf2d58c0104de0db`, `d22578b7e1a5d135c54e13b2f3f44153fbdcb635`, `dbf152c2472dd27f2bdf2a5f039a3cca3e3ad633`, `41a012403eb81c7d7ef0747ce1a27cb980fa4197`, `b781ae9ef89778737e930b191522886b5bc0a04e`, `486297c6eebe07f91cea3a6c7db4e9fe7fa992e0`, `f8adfdc800b06da0c2cf483d6974c7af6818c7e1`, `260cf6f4b9c9a5cb687518ba1a30685905b54c86`, `18eff044e39f759989ab439ca6e85b6a8a9ebe78`, `d9789c5ee1768f65941116c59ccdbff40d68c350`, `56b6546a9e71ce25a82d14dc1129795468746ac2`, `71d42c286ea9d14d927b2aa76f3cbd22a880e6d2`.\n- Static source review caught and corrected escaped newline syntax in `main.py` and `rate_limit.py`, and corrected auth policy precedence. Python test suite and Redis integration remain UNVERIFIED because no isolated runtime/Redis service has been started.\n\n## Task 3 completion record (2026-11-01)\n\n- Selected Nginx because the standard build provides built-in per-IP request and connection limits; Certbot sidecar handles ACME issuance/renewal. Added bootstrap and TLS listener profiles.\n- Added `docker-compose.yml`, backend/frontend multi-stage Dockerfiles, per-context `.dockerignore` files, Nginx TLS/bootstrap templates and proxy parameters. Backend has no published port; Redis is internal-only. Nginx has the only public ports.\n- Self-hosted proxy uses fixed Nginx IP `172.30.0.2`; backend trusted proxy list is exactly that IP. Nginx overwrites client forwarding headers. Uvicorn command disables its own broad proxy-header wrapper; app middleware applies the explicit list.\n- Railway Procfile and railway.json now disable forwarded-header parsing and the Uvicorn server banner. This intentionally avoids trusting Railway's dynamic edge peer or private-network supplied headers. Per-IP quotas on Railway may see a shared edge address.\n- Railway public networking docs describe edge request headers; a Railway support clarification says peer addresses are not stable and private-network callers bypass edge header rewriting. Therefore the split Vercel/Railway backend remains network reachable directly; this cannot be safely solved by CORS or a guessed proxy CIDR. The limitation and a private-only alternative are documented in `NETWORK_HARDENING.md`.\n- Added strict production CORS origin validation, API response headers, Origin checks on login/logout and cookie-authenticated unsafe requests, Next.js 16 `proxy.ts` nonce CSP, and frontend security headers. Script CSP does not allow `unsafe-inline`; style attributes retain a narrow `unsafe-inline` exception for current Framer Motion usage.\n- Added `.env.example` files and deployment guide with TLS bootstrap, renewals, Vercel/Railway and local/desktop guidance.\n- Main commits: `7f14e0fffe6f0ef0df6ce9bfaa08a4cd20ece975`, `b948a98a9b1b0d3c12f3a3768bab8f34a46dc9b6`, `454957028a0cf2e43b740e76f8f78e0cc36d08c9`, `63bdd3e77097590c9ef7a02ea3d68d617f49f7db`, `89fe27c8a66befe8a2fc3ca901e0a75e2fa2edc4`, `0ca51cfca567a68eb90ac571a603f1f3ff149194`, `1954085042029c20d9ed834986e2e7d50b0c2391`, `6c7dc063c2a0086f36ad8f57bdc153dd3e3a9d2f`, `142152c201529a5f24236b3dde2f862916c0c159`, `8c610e378cff14e137e1879508e0dc6172373e98`.\n- JSON validity of `backend/railway.json` was checked. Docker Compose/Nginx syntax, image builds, TLS, browser CSP and proxy spoof behavior were not run; all remain UNVERIFIED pending isolated test infrastructure.\n\n## Validation status

No app runtime, production service, production data, or production credentials have been used in this resumed session. Runtime tests and attack simulations remain UNVERIFIED until run in an isolated test environment. Never claim full security.
