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
- [ ] Redis-backed shared limiter with local in-memory fallback.
- [ ] Per-IP limits for all routes; stricter auth limits.
- [ ] Per-user and per-organization quotas.
- [ ] Login progressive delay/temporary lockout without user enumeration.
- [ ] 429 + Retry-After and safe audit logging.
- [ ] Tests for all policies.

### Task 3 — reverse proxy/network
- [ ] Recommend and configure Caddy/Nginx + compose.
- [ ] Internal/loopback-only backend listener.
- [ ] Proxy rate/connection/body/time limits and compression.
- [ ] Explicit trusted proxy IPs and spoofing tests.
- [ ] Security headers, banner removal, strict CORS and CSRF.
- [ ] Vercel/Railway and local/desktop equivalent guidance.

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

## Task 1 completion record (2026-11-01)\n\n- Confirmed hardcoded JWT signing key location: `backend/app/core/security.py:6` in commit `97d29d73178c44a0efd8da2c3d0e94298734b086`. No value recorded.\n- Added `docs/audit/SECRET_EXPOSURE_REGISTER.md` with rotation actions and explicit UNVERIFIED coverage boundary.\n- Added `.gitleaks.toml`, `.github/workflows/secret-scan.yml`, `.pre-commit-config.yaml`. Prior naive keyword scan was over-broad; the new custom rule requires a literal assignment and minimum length/entropy; Gitleaks default rules remain enabled. CI scans full Git history and is expected to flag the known historical key until the exposure is addressed through a separately approved history policy. Output is configured redacted.\n- Added `backend/app/core/api_docs.py` and wired it into `backend/app/main.py`; production/prod disables docs, ReDoc and OpenAPI schema. Added `backend/tests/test_api_docs.py`.\n- Commits for Task 1: `ab8123bb02942537fa4666fa3891b856b4e4f690`, `7a8060e920f45caf3066f4019a7aaf6b8f957014`, `e883b3a34dce1acc3181132410af67161060e5c1`, `c1531664e5a41505f15050a5e9b24d0c65d2ffbb`, `08f19f6bd17019049d4327663aa271169ed2df77`, `896bfbaab88d6e16c9e82a20ec644d9621203e56`, `6727a39970143706041086871e24afe342d77946`, `520e562a248ac6a8fae1c8d976d69178fe9740d5`.\n- Tests have been authored but not executed. Gitleaks CI has not yet run.\n\n## Validation status

No app runtime, production service, production data, or production credentials have been used in this resumed session. Runtime tests and attack simulations remain UNVERIFIED until run in an isolated test environment. Never claim full security.
