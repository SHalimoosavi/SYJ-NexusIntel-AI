# Phase 2 Security Hardening — Progress Log

**Updated:** 2026-11-01  
**Repository:** SHalimoosavi/SYJ-NexusIntel-AI  
**Active branch:** feat/security-hardening  
**Scope of this checkpoint:** approved merge of main into the feature branch and the requested secret-hygiene work only.

## Authoritative checkpoint

- main remains at e51373d276b443581367f2c19aa291ebf2a042d3; no commit was made to main.
- main was merged into feat/security-hardening with a normal merge commit: 5418ae47489777208f8de430f719d9bf9d1c4610.
- Merge PR #3: https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/pull/3 — merged. GitHub reported zero changed files after refresh; no conflicts or conflict resolutions occurred. Both merge parents are preserved.
- feat/security-hardening is synchronized with main at 0 commits behind; the merge base is main at e51373d276b443581367f2c19aa291ebf2a042d3. The ahead count is intentionally omitted because each audit checkpoint commit itself increments it.
- audit/baseline was not changed. No branch or tag was deleted. No rebase, squash, force-push, cherry-pick or history rewrite was performed.
- Final review PR #4 from feat/security-hardening to main is open and unmerged: https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/pull/4. GitHub reports mergeable=true. It must remain unmerged.

## Step A — secret exposure and hygiene

### Confirmed findings and actions

| Finding | Classification | Required action |
|---|---|---|
| Historical JWT signing key | Confirmed exposure: backend/app/core/security.py:6, introduced by c06218f640b5765746cf98916f3a92792992dfb7, last present in 97d29d73178c44a0efd8da2c3d0e94298734b086, removed by 827aad3701b3e25843d56804e6ee21e8e2dab55f; recoverable in all 24 inspected tags | Mandatory owner rotation and invalidation of outstanding tokens/sessions. Owner status **UNVERIFIED**. |
| Historical PostgreSQL URL | Credential-bearing URL at .env.example:4, introduced by c0e2705da78d2568dcb38181728fa0701b48e4ed; provisioning/reuse **UNVERIFIED** | Treat as compromised; rotate/retire unless owner confirms synthetic and never reused. |
| Gitleaks match in audit document | False positive at docs/audit/AUDIT_REPORT.md:199, commit 6b66d83191f99fce235aa7262c0863e8a17e5077, rule syj-legacy-jwt-secret-assignment; dynamic Python key-generation command, not a static secret | No rotation. Rule narrowed to static literals in 28e0b81126ad1eadeca5a89e606cacefc6998a6d. |
| Other secret classes | No additional Gitleaks findings after full-history rescan; provider-side use/reuse and undetectable formats remain **UNVERIFIED** | Owner should privately review provider inventories; rotate any value found in Git or reused. |

The full findings, evidence, limitations and rotation actions are in docs/audit/SECRET_FINDINGS.md. Values are masked as ****; no full secret is printed or committed.

### Hygiene commits

- 7cce933b47d201f6c651c2596cdfb301a3b58e1e: root PostgreSQL example replaced with postgresql://USER:PASSWORD@HOST:5432/DBNAME; .gitignore now blocks .env, .env.*, keys/certificates and local DB files while allowing .env.example; root/backend/frontend Docker ignore files exclude secret files and local artifacts.
- bdbd2357de809df0e58f82cc583b92c0906eb69d: JWT startup validation requires configured keys, minimum 32 UTF-8 bytes, and rejects known placeholder/default and obvious low-entropy values; added docs/audit/KEY_ROTATION.md.
- df66adfee6a33614e87a8c02aca9c8fb02af5064 and 4198d384e64be43210771f7eb0548ae122964fc8: test key fixtures corrected; CI now creates an ephemeral test signing key.
- 7043f58b48d164f09904946d35f754969257ca0c: Gitleaks configuration with path-and-exact-placeholder allowlist, pre-commit hook, diff scan and full-history metadata workflow.
- 28e0b81126ad1eadeca5a89e606cacefc6998a6d: Gitleaks legacy JWT rule narrowed to static literals; this removed the dynamic shell key-generation false positive.

### Gitleaks historical rescan

- Full-history metadata workflow run 41334988672 initially reported two matches. The second was identified from repository evidence as the dynamic command in docs/audit/AUDIT_REPORT.md:199, commit 6b66d83191f99fce235aa7262c0863e8a17e5077, rule syj-legacy-jwt-secret-assignment; it was not a credential literal.
- After narrowing the rule, run 41335108048 completed successfully and reported one finding only: the confirmed historical JWT key at backend/app/core/security.py:6, commit c06218f640b5765746cf98916f3a92792992dfb7. Final-branch run 41335412531 repeated this result on head 7cb814a454d6e708e550f1da10a34ba93803a5ac.
- Final full-history Gitleaks run 41335412531 passed and reported one historical finding (the JWT key above). Diff Gitleaks push run 41335412600 and PR run 41335433831 both passed.
- No credential was tested against a live service. No history purge was performed or approved.

## Rotation status — owner action required

The owner-provided status fields were not filled in. Therefore:
- JWT key rotation: **UNVERIFIED / not confirmed**.
- PostgreSQL credential rotation or synthetic confirmation: **UNVERIFIED / not confirmed**.
- Other secrets: no additional Gitleaks findings; owner-side inventory is **UNVERIFIED**.

Follow docs/audit/KEY_ROTATION.md. Never paste keys/passwords into ChatGPT, GitHub issues, commits or logs. A history purge is a separate decision and remains **NOT APPROVED**.

## Verification status

Final code CI on PR #4 code checkpoint 7cb814a454d6e708e550f1da10a34ba93803a5ac passed. Subsequent commits only refreshed audit documentation:

- Backend security regression suite: **104 passed, 209 warnings in 2.66s** (push run 41335412532; PR run 41335433884 passed).
- Frontend ESLint: **passed** (push run 41335412532; PR run 41335433884 passed).
- Frontend Next.js production build / TypeScript build validation: **passed** (same runs).
- Dependency audit: **passed** (push run 41335412509; PR run 41335433890 passed).
- Diff Gitleaks scan: **passed** (push run 41335412600; PR run 41335433831 passed).
- Full-history Gitleaks metadata audit: **passed as a workflow**; one expected historical JWT finding remains (run 41335412531).
- Backend lint/type-check: **UNVERIFIED** — the repository does not define a backend lint/type-check command or pinned backend lint/type-check tools.
- Explicit frontend tsc --noEmit: not configured separately; Next.js production build passed and is the existing TypeScript validation path.

An earlier run 41335108080 failed because a static fixture was inadvertently included in the negative test set. The test fixture and CI key setup were corrected in commit 4198d384e64be43210771f7eb0548ae122964fc8; the final push and PR test runs passed.

Vercel's automated PR comment reported a preview deployment error. The cause was not investigated as part of this approval and remains **UNVERIFIED**; it is separate from the passing GitHub Actions test/build workflow.

## Other pre-existing Phase 2 work — paused

The feature branch already contains earlier implementation work for rate limiting, reverse-proxy/network controls, tenant isolation, RBAC, response schemas, logging and audit controls. Those workstreams are not part of this approval and no new work was started on them in this task. Their outstanding integration/deployment verification remains as recorded in the existing tests and audit matrices.

## Hard constraints still in force

- No changes to main.
- No rate limiting, reverse proxy, CSRF or other new implementation work.
- No production credential tests or secret-store access.
- No full secret values in output, files, commits or logs.
- No history rewrite, force-push, rebase, cherry-pick, branch/tag deletion or purge.
- After opening the final feature-to-main PR and reporting CI/evidence, stop and wait for owner approval. Do not merge that PR.

## Phase 1 — PR #4 review findings (implementation branch)

**Branch:** `fix/phase1-auth-proxy-rbac`  
**Base:** `feat/security-hardening` at the Phase 1 branch point `4f457e170256790cc51676e86eead73a21098054`  
**Status:** Implementation committed; CI verification pending; no merge performed.

### P1 — refresh-token concurrency

- Added browser-side single-flight refresh coordination in `frontend/lib/auth-refresh.mjs`, using an in-tab shared promise and Web Locks with a short cross-tab completion marker.
- Logout cancels pending refresh state; successful login/invitation acceptance re-enables refresh coordination.
- Added a Redis Lua atomic claim for refresh JTIs, with a short idempotency result cache. A parallel duplicate receives the same replacement cookie pair; a replay after the grace window revokes the session family. A request still in progress returns 503 rather than revoking a legitimate session.
- Added regression coverage for parallel refresh claims, duplicate cookie-pair reuse, later replay revocation, backend unavailability, logout invalidation, frontend parallel calls, refresh failure, and logout during refresh.
- Implementation commits include `cd8a21f`, `186673e`, `c32115f`, `9b022d2`, `cf73a87`, `42f4219`, `4bec95d`, `8714d1e`, `e3cb319`, and `c36da7b`.

### P2 — trusted proxy client IP

- Removed Uvicorn's implicit proxy-header middleware from the application.
- Added `TRUSTED_PROXIES`, defaulting to trust nothing; only a socket peer matching an explicitly configured IP/CIDR may supply `X-Forwarded-For`.
- Resolver walks the chain from right to left and selects the first untrusted address; malformed headers fall back to the immediate peer.
- Login abuse controls and global/route rate limits use the resolved client IP.
- Docker's Nginx peer is explicitly configured as `172.30.0.2`; Uvicorn proxy-header parsing remains disabled and forwarded-allow-ips is explicitly empty in the service commands.
- Added tests for spoofed headers, trusted proxy chains, IPv6, malformed values and trust-none default.
- Implementation commits include `a96e1b4`, `72f51fd`, `f6ab89c`, `5416105`, `57b0c8e`, `8979bf6`, `c911691`, `fe711dc`, `80ddeab`, and `25adb44`.

### P2 — SUPER_ADMIN role propagation and protection

- User status and delete routes now pass the authenticated actor role to their services.
- Non-SUPER_ADMIN actors cannot change/delete SUPER_ADMIN targets.
- The last active SUPER_ADMIN cannot be disabled or deleted.
- Existing self-modification prevention and organization-scoped user lookup remain in place.
- Added regression tests for SUPER_ADMIN operations, ADMIN denial, self-escalation prevention, last-SUPER_ADMIN protection and cross-tenant isolation.
- Implementation commits include `ee63de9`, `465cd02`, and `409c7fc`.

### Verification and outstanding owner actions

- Backend security regression suite: **121 passed, 241 warnings** (CI run [41370540099](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41370540099)).
- Frontend regression suite: **4 passed, 0 failed**; ESLint and Next.js production build passed (same CI run).
- Dependency audit passed ([41370552138](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41370552138)).
- Secret scan passed ([41370552036](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41370552036)).
- Frontend ESLint reported two `window.location.assign()` warnings; these are existing navigation warnings in `frontend/lib/auth.ts`, not test failures.
- The 241 backend warnings are not suppressed; warning triage remains Phase 2 work. The earlier baseline was 209 warnings, with 27 warnings now attributed to the new user-management regression tests and 5 additional warnings in auth-session tests; exact warning-class triage remains open.
- PR #4 remains open and unmerged. This Phase 1 branch is intended to open a stacked PR into `feat/security-hardening`; no merge into `feat/security-hardening` or `main` is authorized.
- JWT rotation status: **UNVERIFIED** (owner status field not supplied).
- PostgreSQL credential rotation/synthetic status: **UNVERIFIED** (owner status field not supplied).
- Vercel disconnection status: **UNVERIFIED** (owner status field not supplied).
- No live credential tests or history purge performed.


## 2026-11-03 — Phase 1 regression-gap recheck (Step B)

Reviewed the current PR #5 head 048ed9209b827b424ffa754ff7a3aaa30b1cac20 and these files: backend/app/core/client_ip.py, backend/app/core/rate_limit.py, backend/app/services/user_management_service.py, backend/tests/test_auth_sessions.py, backend/tests/test_proxy_header_trust.py, backend/tests/test_user_management_security.py, frontend/lib/auth-refresh.test.mjs, and frontend/lib/api.ts.

### Existing implementation and regression evidence

- Refresh rotation: atomic Redis Lua claim/completion scripts and a locked in-memory fallback are present. The auth-session test covers duplicate refresh returning the same cookie, replay after the grace window, session-family revocation, and fail-closed backend outage. Real Redis Lua integration/concurrency remains UNVERIFIED; tests exercise the in-memory manager.
- Frontend refresh: module-level single-flight and Web Locks coordination are present. Existing tests cover same-tab coalescing, failure, logout cancellation, and invocation of the Web Lock API. Independent-tab contention, fallback coordination without Web Locks, and queued apiFetch 401 replay are NOT COVERED / UNVERIFIED.
- Proxy trust: TRUSTED_PROXIES defaults to empty; resolver rejects malformed chains and ignores forwarded headers from an untrusted peer. Unit tests cover spoofing, rightmost untrusted hop, IPv6, malformed values and the empty default. Actual middleware-to-rate-limit-key integration is NOT COVERED / UNVERIFIED.
- RBAC: tests cover ADMIN denial when disabling/deleting a SUPER_ADMIN, cross-tenant target denial, self-role escalation denial, and protection of the last active SUPER_ADMIN. These are present in the current PR #5 tree; no RBAC behavior change was made in this checkpoint.

### Step B disposition

The requested negative behaviors have existing regression tests for refresh-token replay, ADMIN-to-SUPER_ADMIN protection, cross-tenant target access, and spoofed forwarded-for at the resolver boundary. The remaining integration/concurrency gaps above require executable regression tests. No auth-sensitive code or test changes were committed in this checkpoint because this GitHub connection does not provide a repository checkout or command runner to demonstrate that new tests fail before and pass after the change; no unexecuted tests are being represented as verified. Step B is therefore INCOMPLETE pending an executable test environment or CI-backed patch workflow that can establish the required before/after evidence.


## 2026-11-03 — Historical auth-sensitive commit mapping

- Created `docs/audit/AUTH_SENSITIVE_CHANGES.md` in commit `41955f65ba5d536e757e27080b5fc549227208c5` on `fix/phase1-auth-proxy-rbac`.
- Method: enumerated PR #5 (35 commits) and PR #6 (86 commits), inspected commit-level file lists/patches for auth, JWT, refresh, tenant, RBAC, rate-limit and proxy-IP paths/content, and inspected PR #6's aggregate base-to-head diff (49 files). PR #6 introduces no auth-sensitive behavior change; the relevant behavior implementation is in PR #5.
- The document maps identified behavior and test/configuration commits, names tests, distinguishes tests added later, records the historical prefix/test-first limitation, and lists uncovered areas. The table is included in PR descriptions for owner review.
- Historical limitation: **Convention not followed before `cd8a21f1c18c0b89ff271ea47005b5e9787839d9`: not retroactively fixable without history rewrite.** No history was changed.
- Audit completion is limited to inspected patches; see the document's explicit search method and completeness limits. Remaining gaps must be covered with test-first commits.


## 2026-11-03 — Step 3 regression and integration coverage update

- Auth-sensitive mapping updated in `docs/audit/AUTH_SENSITIVE_CHANGES.md`; PR #5 and PR #6 descriptions now contain the same owner-review table.
- New characterization/integration tests and commits: `a1d1f5b` API replay contract tests; `7028db3` independent browser-context refresh; `0881fb4` real Redis refresh rotation; `4b0194f` ASGI rate-limit/client-IP integration; `1dcbec7` missing refresh-result fail-closed; `2b9abbc` trusted login IP key; `c49b7c2` proxy launch flags. API helper extraction commits are `a41e61f` and `0fc30c9`, both prefixed `AUTH-SENSITIVE:` and intended to preserve existing behavior.
- Existing SUPER_ADMIN and cross-tenant tests remain covered by PR #5 run [41549229425](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41549229425).
- New integration tests for browser contexts, API replay, Redis atomicity and middleware client-IP were green on [41561425429](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41561425429): backend 123 passed, 0 failed, 0 skipped, 241 warnings; frontend checks passed. Later added missing-result/login-IP/launch-config tests are awaiting the latest PR #5 CI.
- Ruff/Mypy CI was enabled for PR #5. First run exposed 88 legacy Ruff diagnostics; matching the existing PR #6 Ruff policy and removing real unused/duplicate imports reduced the count to 26, then targeted non-behavior cleanup was committed. Latest run [41562235297](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41562235297) was queued at the time of this update; Step 3 is not formally complete until latest tests are green.
- Latest known PR #5 code head before this documentation update: `6c8121d1af2da9a81586c316c184578662ded856`; documentation commit for this update follows. PR #5 remains open/unmerged.

## 2026-11-03 — Step 5 verification evidence on PR #6

- PR #6 head: `86121487d509a302e60bcaf76d1c122d18a55f10`. All required checks completed successfully on that exact head:
  - Security Tests / backend-quality: [41557633460](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41557633460) — Ruff passed; Mypy 0 errors in 118 source files; backend 118 passed, 0 failed, 0 skipped, 2 warnings; frontend lint completed with 0 errors and 2 warnings; production build completed successfully.
  - Dependency audits: [41557633335](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41557633335) — npm and Python audits passed, 0 known vulnerabilities each.
  - Gitleaks diff: [41557633307](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41557633307) — passed.
  - Gitleaks full history: [41557626920](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41557626920) — 584 commits scanned, one historical JWT finding remains unsuppressed and unbaselined. Current `backend/app/core/security.py` does not contain the legacy hardcoded key assignment.
- Backend warning count is 2 versus the earlier 209 baseline (207 fewer). This comparison is based on the current PR #6 backend test run.
- SSL typing resolution uses the helper plus the one owner-authorized `arg-type` ignore at `osint_service.py:118`; Python 3.12.15 typeshed Protocol mismatch comment and runtime guard are recorded in code. Mypy reports 0 errors. TLS verification remains enabled.
- JWT signing-key rotation and PostgreSQL credential rotation remain **UNVERIFIED**. No baseline/suppression was added. Docker Step 6 remains **NOT STARTED** pending Step 3 completion and formal Step 5 gate closure.


## 2026-11-03 — Step 3 completed; Step 5 branch-scope decision required

### Step 3 — COMPLETE on PR #5

- PR #5 head at verification: f532646265bf6eb6ca843a5e607c658659d48421.
- [Security Tests run 41562583720](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41562583720): backend **126 passed, 0 failed, 0 skipped, 243 warnings**; frontend Node tests **8 passed, 0 failed, 0 skipped**; frontend lint **0 errors, 2 warnings**; production build completed successfully.
- The new Redis-backed atomic rotation/reuse test, independent browser-context refresh test, API replay characterization tests, middleware IP bucket integration, missing cached-result fail-closed test, trusted login IP-key test and proxy launch configuration test are all included in the passing backend/frontend runs.
- Existing SUPER_ADMIN and cross-tenant tests are included in the 126 passing backend tests. Existing refresh-token single-flight, atomic rotation, reuse detection and proxy resolver unit tests remain in the same suite.
- New tests that exercise already-existing behavior are explicitly characterization tests; no new auth policy behavior was introduced. Historical behavior commits remain documented as accepted, non-retroactively-fixable deviations.

### Step 5 — PR #6 COMPLETE; PR #5 has a separate legacy Mypy baseline

- PR #6 head: 86121487d509a302e60bcaf76d1c122d18a55f10. Its complete Step 5 suite is green on that exact head:
  - [Security Tests / backend-quality 41557633460](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41557633460): Ruff passed; Mypy **0 errors** in 118 files; backend **118 passed, 0 failed, 0 skipped, 2 warnings**; frontend lint **0 errors, 2 warnings**; production build finished successfully.
  - [Dependency audits 41557633335](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41557633335): npm and Python audits passed; 0 known vulnerabilities each.
  - [Gitleaks diff 41557633307](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41557633307): passed.
  - [Gitleaks full history 41557626920](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41557626920): 584 commits scanned; exactly one historical JWT finding remains visible and unsuppressed.
- PR #5 received a separate quality job to verify its own head. Ruff now passes, but Mypy reports **60 pre-existing typing diagnostics across 18 files** on PR #5. This is the legacy typing baseline that PR #6's separate Phase 2 type-hardening work addressed. PR #5's backend tests and frontend checks are green, but the additional PR #5 quality job is red; do not represent PR #5 as fully green.
- The PR #5 Mypy failure is not a new auth regression. Fixing it safely requires porting the Phase 2 typing remediation across 18 files, some of which overlap auth-sensitive code. No broad copy, permission change, type ignore, or config weakening has been applied.

### Step 6 — NOT STARTED

Docker self-hosted install remains gated. Do not start until owner confirms whether Step 5 is scoped to PR #6 (green) or the 60 PR #5 baseline typing errors must also be remediated on PR #5.

### Still open

- JWT signing-key rotation: **UNVERIFIED**.
- PostgreSQL credential rotation: **UNVERIFIED**.
- Historical Gitleaks JWT finding: visible, unsuppressed, unbaselined.
- No merge, no main changes, no history rewrite, no branch/tag deletion.


## 2026-11-03 — Final PR #5 Step 3 verification refresh

- Added coordinator-resume characterization test in commit 5fb05398a89e8023d3f50936c9b435bc7702d791: frontend test verifies refresh can resume after cancellation. Existing auth.ts calls resumeAuthRefresh only after successful login and invitation acceptance.
- Latest completed PR #5 Security Tests run [41563015472](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41563015472): backend **126 passed, 0 failed, 0 skipped, 243 warnings**; frontend Node tests **9 passed, 0 failed, 0 skipped**; frontend lint 0 errors / 2 warnings; production build finished.
- Ruff passed on the PR #5 quality job. Mypy remains red with **60 pre-existing diagnostics across 18 files**, not an auth regression. Do not call PR #5 fully green.
- PR #5 dependency audit [41563015478](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41563015478) passed; Gitleaks diff [41563015482](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41563015482) passed; full-history audit [41563011717](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41563011717) completed with the single historical JWT finding.
- Step 3 is complete for the requested refresh, proxy-IP, SUPER_ADMIN and cross-tenant coverage. Historical prefix/test-first deviations remain documented and accepted.
- Step 5 is green on PR #6 head 86121487d509a302e60bcaf76d1c122d18a55f10; PR #5's additional Mypy gate remains red. Step 6 remains NOT STARTED pending owner decision on whether to port the 60 Phase 2 typing diagnostics' remediation into PR #5 or scope Step 5 strictly to PR #6.


## 2026-11-04 — Pre-port immutable backup refs

- Created `backup/2026-11-04/pr5-pre-typing-port` at exact PR #5 pre-port head `02b7379b3e04f484555bfb7e814ea238980789a8`.
- Created `backup/2026-11-04/pr6-pre-sync` at exact PR #6 pre-sync head `86121487d509a302e60bcaf76d1c122d18a55f10`.
- Both refs were read back from GitHub and their full SHAs verified. These are new refs; no existing ref was moved or deleted.
- Step 1 of the approved typing port may proceed only after a file-by-file diff review. No typing changes have yet been ported.


## 2026-11-04 — PR #6 typing-only port applied to PR #5

- Ported only type-oriented changes to PR #5. New commits preserve existing SQLAlchemy `Column(...)` expressions; model attributes now use `Mapped[...] ` annotations for scalar instance typing.
- Added a `TypedDict` for API docs configuration while preserving the prior environment-selection expression; typed the Redis client through a `Protocol` and `cast` while preserving Redis calls, arguments, keys, thresholds, grace periods and TTLs.
- Used type-only narrowing for DNS getaddrinfo tuple values and preserved the existing HTTP response body assignment behavior through `setattr`; annotated numeric accumulators and audit summary dictionaries.
- Narrowed the existing decoded certificate result with `cast` only. No SSL context, certificate verification, expiration behavior, output contract or socket call was changed in this port.
- Files changed: `backend/app/models/{user,organization,activity,ai_usage,invitation,lead,lead_note,subscription,audit_log,feature_flag}.py`; `backend/app/core/{api_docs,safe_http,rate_limit}.py`; `backend/app/services/{audit_dashboard_service,revenue_forecast_service,crm_service,osint_service}.py`.
- Explicitly excluded PR #6 workflow, hosting, dependency automation, Ruff-only cleanup, Redis argument coercion, HTTP response-body refactor, SQLAlchemy `mapped_column` substitutions, and the SSL helper runtime change.
- PR #5 port head: `5aa15fdaf6e94dc3789ba766e9fc582a4635ab9d`. Actions were triggered for this head; do not mark the port green until its finished backend-quality, backend tests, and frontend jobs are inspected.
- PR #5 and PR #6 remain sibling branches targeting `feat/security-hardening`; no merge/sync commit is applicable under the owner's conditional stacking rule.


## 2026-11-04 — PR #5 model annotation correction after CI failure

- Finished Security Tests run [41726490100](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41726490100) passed Ruff, backend security tests and frontend checks/build, but backend-quality Mypy failed with 12 assignment errors across the 10 model files listed below.
- Root cause: `Mapped[T]` declarations were paired with existing SQLAlchemy `Column(...)` assignments. Corrected only the static annotations to `Column[T]` and removed the unused `Mapped` imports; the `Column(...)` expressions and all runtime behavior remain unchanged.
- Files: `backend/app/models/user.py`, `backend/app/models/subscription.py`, `backend/app/models/organization.py`, `backend/app/models/lead_note.py`, `backend/app/models/lead.py`, `backend/app/models/invitation.py`, `backend/app/models/feature_flag.py`, `backend/app/models/audit_log.py`, `backend/app/models/ai_usage.py`, `backend/app/models/activity.py`.
- No auth, JWT, refresh, RBAC, tenant isolation, rate-limit keying or proxy-IP implementation was changed. No check was weakened, no ignore added, and no test removed.
- This is one bounded correction attempt. CI must verify Mypy 0 errors and unchanged-or-higher test counts before this gate can close.


## 2026-11-04 — audit matrix and PR description visibility

- Updated `docs/audit/AUTH_SENSITIVE_CHANGES.md` in commit `ae35fa149d47a78be122f75be72092e397031be0` to record the type-only PR #6-to-PR #5 port, its 10-file `Mapped[T]` to `Column[T]` correction, the affected file set, and the explicit absence of auth/JWT/refresh/RBAC/tenant-isolation/rate-limit-keying/proxy-IP behavior changes.
- Updated PR #5 and PR #6 descriptions with the exact SSL `type: ignore[arg-type]` line at `backend/app/services/osint_service.py:118`. A runtime `isinstance(sock, ssl.SSLSocket)` guard alone does not resolve the overloaded `getpeercert`/single-method Protocol mismatch; suppression retained, no TLS verification change.
- PR #5 head is now `ae35fa149d47a78be122f75be72092e397031be0`; PR #6 head remains `86121487d509a302e60bcaf76d1c122d18a55f10`. PRs are siblings targeting `feat/security-hardening`; no sync merge is applicable.
- CI on the updated PR #5 head is required before the verification gate can close. Docker Phase 3 remains blocked until every Section 3 item is finished and green.


## Deferred, not blocking

Owner approved all four items as non-blocking and explicitly excluded them from this typing/hygiene/Docker stack. No remediation code or dependency changes are authorized here.

| Item | Why it matters | Earliest affected version / break point | Proposed follow-up |
|---|---|---|---|
| Passlib 1.7.4 deprecated `crypt` module | Python removes the stdlib `crypt` module; Passlib is unmaintained, increasing compatibility risk on Python upgrades. | Python 3.13 removes `crypt`. | Separate AUTH-SENSITIVE PR migrating to `argon2-cffi` or `pwdlib`, with rehash-on-login and password-hash migration/regression tests. Do not start now. [Issue #7](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/issues/7). |
| Starlette TestClient / httpx deprecation | Current pinned test stack warns about the legacy TestClient integration. | Pinned Starlette 1.3.1 + httpx 0.28.1 already emits the warning. The warning does not specify a removal release; no future break version can be responsibly asserted. | Migrate test dependencies only when pinned Starlette/httpx versions permit the supported replacement, retaining the test contract. [Issue #8](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/issues/8). |
| Frontend internal navigation via `window.location.assign()` (`frontend/app/login/page.tsx:33`, `frontend/lib/auth.ts:19`) | Next.js warns that internal navigation should use its router; replacing it may alter authentication navigation behavior. | Pinned Next.js / eslint-config-next 16.4.3 already emits the lint warning; the warning does not specify a removal release. | Separate PR using Next.js router navigation with explicit login-flow tests. [Issue #9](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/issues/9). |
| PR #5 historical backend warning baseline (243 warnings) | High warning volume reduces signal and makes regressions harder to identify; owner accepts the existing baseline. | No single Python/library break version; this is a recorded baseline, not a specific runtime compatibility failure. | Preserve the baseline in this stack; reassess only in a separately approved maintenance task. [Issue #10](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/issues/10). |

### Phase 3 Python image pin constraint

- When Phase 3 is authorized by the completed Section 3 gate, pin the backend image to Python **3.12.15** (the exact Python patch version used by the CI runner evidence) rather than any floating `python:3` or `latest` tag.
- Add an explanatory Dockerfile comment and repeat the rationale in the Phase 3 PR description: Passlib 1.7.4 currently depends on the stdlib `crypt` module, which Python 3.13 removes. The deferred Passlib migration must not be started in Phase 3.

### PR #5 CI correction attempt 1 — diagnosis and repair

- Finished run [41729011812](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41729011812) failed because the earlier correction removed the `Mapped` import but did not replace square-bracket `Mapped[T]` annotations. Ruff reported 12 `F821 Undefined name Mapped` errors; Mypy was skipped. Backend collection reported 11 errors; the first was `NameError: name 'Mapped' is not defined` from `app/models/user.py:16`, cascading through test imports.
- Corrected only the annotations in the same 10 model files from `Mapped[T]` to `Column[T]`; no `Column(...)` assignment, default, constraint, or runtime expression was changed. Correction commits: `b9f9cb0171c69a8574068b5f2b2dd41f93e85818`, `d96dbc2fe479ec4648872236993d91c34e9e6599`, `53e10cf2d963764c48be16ec82a30db316b47e5e`, `30638b682a3b516e75e8661cdbd57dbf34b61f54`, `882722e595c3f88f03fc496a7aa05740df2bde31`, `64a8dc42223b80cdefd0ff4729a15520aa03e130`, `f21080b43c969d222624041f8b836206d177c281`, `1f277a042e9f78697a23d9c770409706d8d7e7f8`, `7c814ca14e2a8eb5ccd944e8770584311d491923`, `1ddeb2566a7fecccb772699cf1aa83758b6ff932`.
- The 243-warning baseline remains the last complete comparable PR #5 backend test result (126 passed, 243 warnings). The failed collection attempt emitted 2 warnings before abort; that partial count is not comparable. Verify exact warning count on the next complete test run and ensure it does not exceed 243.
- Deferred warnings are not to be fixed in this stack.


- CI revalidation trigger after annotation correction and deferred-warning bookkeeping: documentation-only empty-effect checkpoint; no application behavior change.

## 2026-11-04 — Pre-runtime-revert backup

- Created new ref `backup/2026-11-04/pr5-before-runtime-revert` at exact commit `1c4a4b53d97d5b91f0d562195128d04fd47db023` before any runtime revert or model import correction.
- Ref creation succeeded as a new branch; no existing ref was moved or deleted.
- Backup ref is immutable for this recovery sequence.

## 2026-11-04 — Owner correction: backup, model typing blocker, refresh-claim dependency

### Section 0 — backup
- Created `backup/2026-11-04/pr5-before-runtime-revert` at exact SHA `1c4a4b53d97d5b91f0d562195128d04fd47db023`.
- Recorded the ref in this file in commit `b36c1397f6591a0ef9dbd37bad25dadb32420f6b`. No existing ref was moved or deleted.

### Section 1 — Ruff root-cause diagnosis; not yet closed
- Finished run [41729011812](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41729011812) reports exactly 12 Ruff errors, all rule `F821 Undefined name Mapped`: activity.py:15, ai_usage.py:15, audit_log.py:35, feature_flag.py:33, invitation.py:16, lead.py:15, lead_note.py:15, organization.py:14, subscription.py:15, user.py:16, user.py:33, user.py:38.
- The later model correction replaced the `Mapped[T]` annotations with `Column[T]` and removed the `Mapped` imports. This avoids the Ruff names but does not follow the owner's explicit instruction to restore the imports and keep the `Mapped[T]` annotations.
- Finished run [41726490100](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41726490100) shows that restoring `Mapped[T]` while retaining `Column(...)` assignments causes 12 Mypy `[assignment]` errors across the same 10 files. A type-safe correction that satisfies both gates needs an owner decision; no further model code was changed in this section.

### Section 2 — refresh runtime revert; STOPPED before code change
- Compared `backend/app/core/rate_limit.py` on the immutable pre-port ref `backup/2026-11-04/pr5-pre-typing-port` (SHA `02b7379b3e04f484555bfb7e814ea238980789a8`) with the current PR #5 branch. The pre-port file already contains `_REFRESH_CLAIM_SCRIPT`, `_REFRESH_COMPLETE_SCRIPT`, the refresh in-flight/result state, and `begin_refresh_rotation`, `complete_refresh_rotation`, and `get_refresh_rotation_result`. The current file's diff from pre-port is limited to the Redis Protocol/type declarations and casts; no refresh-claim runtime feature was introduced by the typing port.
- Therefore no runtime revert commit was made. Removing the scripts/methods would regress pre-port behavior and break existing callers/tests; owner requested STOP if such dependencies exist.
- Direct callers in `backend/app/routers/auth.py`: `begin_refresh_rotation` line 199, `get_refresh_rotation_result` line 223, `complete_refresh_rotation` line 239.
- Dependent tests: `backend/tests/test_rate_limit.py::test_refresh_rotation_claim_is_atomic_and_duplicate_is_idempotent`; `backend/tests/test_auth_sessions.py::test_refresh_rotation_rejects_reuse_and_revokes_session_family`, `::test_refresh_fails_closed_when_session_backend_is_unavailable`, `::test_refresh_missing_cached_result_fails_closed`; and `backend/tests/test_redis_refresh_rotation.py::test_redis_refresh_rotation_is_atomic_idempotent_and_detects_reuse`.
- PR #5 runtime-revert step remains BLOCKED pending owner decision; no refresh/auth code or tests were modified.

### Section 4 — refresh atomicity evidence (analysis only; no implementation)
- PR #5 uses the Redis Lua claim in `backend/app/core/rate_limit.py`; Redis executes the script atomically. It returns 1 for the first claim, 2 for a duplicate while in-flight/result grace state exists, and 0 for replay after grace. Duplicate requests retrieve the same replacement tokens; replay revokes the user session family.
- PR #6 at reviewed head `86121487d509a302e60bcaf76d1c122d18a55f10` uses Redis `SET ... NX EX` in `consume_refresh_jti` and the auth route at `backend/app/routers/auth.py:184`. This is an atomic one-time consume; only one simultaneous request can win, while a duplicate is rejected and triggers session-family revocation. PR #6 has no PR #5-style idempotent duplicate result cache.
- PR #5 default refresh-token TTL is 7 days (`REFRESH_TOKEN_EXPIRE_DAYS`, configurable); consumed-JTI TTL uses that token TTL. In-flight and replacement-result keys use a 5-second grace TTL by default. Production Redis failures raise `RateLimitBackendUnavailable` and the auth route returns 503 with `Retry-After`; process-local fallback is restricted to local/test modes.
- PR #5 tests include an in-memory concurrency/idempotency test, a Redis-backed CI integration test, and auth-session tests for reuse, backend outage, and missing cached result. PR #6 has the one-time consume unit test but no equivalent Redis refresh integration test in the reviewed file set.
- Recommendation is deferred: do not choose or implement a replacement until owner decides between retaining the tested Redis Lua idempotency protocol (with explicit AUTH-SENSITIVE test-first commits) or migrating to a database atomic conditional update.

## 2026-11-04 — Owner correction: Redis refresh protocol predates typing port

- **Correction / withdrawal:** the earlier assistant finding that the typing port introduced refresh-claim runtime behavior in `backend/app/core/rate_limit.py` was wrong. The immutable pre-port backup already contains `_REFRESH_CLAIM_SCRIPT`, `_REFRESH_COMPLETE_SCRIPT`, the in-flight/result state, and all three refresh methods. The alleged runtime violation for this file is withdrawn. No revert is authorized or performed.
- Original introducing commit on the reviewed feature lineage: [`cd8a21f1c18c0b89ff271ea47005b5e9787839d9`](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/commit/cd8a21f1c18c0b89ff271ea47005b5e9787839d9), message `fix(auth): make refresh rotation claims atomic and idempotent`. Its parent is `4f457e170256790cc51676e86eead73a21098054`; the parent version of `rate_limit.py` has neither script nor `begin_refresh_rotation`, and the commit patch adds both scripts and the associated state/methods. The GitHub connector does not expose a shell, so literal `git log -S` was not executed; parent-tree absence plus the introducing commit's patch is the available history proof.
- Later script evolution: `42f4219f4267ec393f94327972c0f3264710a030` added result-key duplicate handling and the third key; `4bec95dca2719bb842b66d9d7658de33e10d9579` corrected the Lua key count from 2 to 3.
- Diff from immutable pre-port backup `02b7379b3e04f484555bfb7e814ea238980789a8` to current PR #5: both Lua script bodies are byte-for-byte unchanged; `backend/app/routers/auth.py` is byte-for-byte unchanged, including callers at lines 199, 223 and 239. The only `rate_limit.py` differences are the Redis protocol/type annotations and casts. Runtime behavior in this file was not altered by the typing port.
- Covering tests: `backend/tests/test_rate_limit.py::test_refresh_rotation_claim_is_atomic_and_duplicate_is_idempotent`; `backend/tests/test_auth_sessions.py::test_refresh_rotation_rejects_reuse_and_revokes_session_family`; `::test_refresh_fails_closed_when_session_backend_is_unavailable`; `::test_refresh_missing_cached_result_fails_closed`; `backend/tests/test_redis_refresh_rotation.py::test_redis_refresh_rotation_is_atomic_idempotent_and_detects_reuse`.
- Finished CI evidence with the Redis integration test present: [Security Tests run 41561425429](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41561425429), jobs `backend-security-tests` and `frontend-checks` both passed; backend summary was 123 passed, 0 failed, 0 skipped, 241 warnings. The run head was `40406633eb03f6aeb91d4072b799455ae10b5c9b`, and the Redis integration test file was present at that head.
- Historical convention: **convention not followed: historical**. The original implementation predates the AUTH-SENSITIVE prefix/test-first convention. Do not rewrite history.
- Production Redis outage handling is fail-closed in code: `_redis()` pings Redis and raises `RateLimitBackendUnavailable` for production when missing/unreachable; the auth route catches that and returns HTTP 503. `test_refresh_fails_closed_when_session_backend_is_unavailable` verifies the route rejects an injected backend-unavailable exception. A live socket-outage integration test is not present; that specific end-to-end outage simulation remains UNVERIFIED.
- Local/dev/test fallback is process-local and protected by a per-process lock. It is not correct for coordinating refreshes across multiple backend worker processes; multi-worker local mode is a known limitation. Production mode does not use this fallback.
- Crash window: if a worker crashes after claim but before publishing the result, the consumed-JTI key remains for the refresh-token TTL (default 7 days), while the in-flight marker expires after the 5-second grace. A duplicate during the grace gets state 2 but cannot fetch a result and returns 503; after the marker expires, a retry is treated as replay (state 0) and the auth route revokes the session family. This is fail-closed but can force reauthentication after a worker crash.
- Redis Cluster note: all keys touched by one Lua script must hash to the same Redis Cluster slot. The current SHA-256-derived key names do not use a shared hash tag, so this protocol is supported by the single Redis node in the Compose design but is not cluster-ready without a deliberate key-slot design.

## 2026-11-04 — Refresh protocol record and SQLAlchemy model typing correction

### Refresh protocol record completed
- Original script introduction is commit `cd8a21f1c18c0b89ff271ea47005b5e9787839d9`; parent `4f457e170256790cc51676e86eead73a21098054` lacks both scripts and the claim method. Later refinements are `42f4219f4267ec393f94327972c0f3264710a030` and `4bec95dca2719bb842b66d9d7658de33e10d9579`.
- Both script bodies and the complete auth route caller file compare byte-for-byte equal between the immutable pre-port backup and the current PR #5 branch. The typing port did not change refresh runtime behavior in `rate_limit.py`; prior violation finding withdrawn.
- Added `docs/audit/REFRESH_PROTOCOL.md`; corrected the protocol row and historical convention in `docs/audit/AUTH_SENSITIVE_CHANGES.md`; updated both PR descriptions with commit, behavior, test names, finished run URL and “convention not followed: historical”.
- Docs commits: progress correction `cb383013ee43313d94e7bb5bac94dcc4ba771f7a`; design note `72e4340736108528be242b6b3155e893b88f0770`; auth audit `eed471aa29f42b1c6407b7380e9c9ceeb1943877`; PR descriptions updated in place (no repository commit).
- Fail-closed code path and route test confirmed: production `_redis()` pings Redis and raises `RateLimitBackendUnavailable`; refresh route returns 503. `test_refresh_fails_closed_when_session_backend_is_unavailable` asserts 503 for an injected outage. Live socket-outage integration remains UNVERIFIED. Local fallback is per-process and not multi-worker safe. Current key hashing is not Redis Cluster slot-compatible; documented.
- Historical Redis integration proof: [run 41561425429](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41561425429), `backend-security-tests` and `frontend-checks` passed; 123 passed, 0 failed, 0 skipped, 241 warnings. Redis integration test file existed at that run head.

### Model typing root-cause correction
- Before correction, finished run [41726490100](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41726490100) reported 12 Mypy `[assignment]` errors: `Column[T]` assignment expression incompatible with SQLAlchemy `Mapped[T]` variable across 10 models. Exact diagnostics were shown to the owner before any cast; no cast was used.
- Replaced the 12 model declarations with SQLAlchemy 2.0 `Mapped[T] = mapped_column(...)` and imported `Mapped, mapped_column` in each affected model. Files: activity.py (1), ai_usage.py (1), audit_log.py (1), feature_flag.py (1), invitation.py (1), lead.py (1), lead_note.py (1), organization.py (1), subscription.py (1), user.py (3).
- The `User` id, password hash and organization_id fields use direct `Mapped`/ `mapped_column` declarations; no casts, ignores or behavior suppressions were used. Feature flag remains optional (`Mapped[bool | None]`); no explicit nullability or database constraint was added/removed.
- Per-file commits: `013a036fa11731491fd3a5709def551a825fd8ba`, `f014289133b8c64b5ad728b041baecf823dc0c64`, `e047c29908e491ec1d85c8253a81ba4d68290e15`, `e67bf363abebc81066cf2a12146a848a8cde65b8`, `cd2c6d0a51ad073deaf3d02990972e35d614277e`, `b3f6af6617c989e67fa5e05193b1817754e9ebe6`, `07df9e348634c7d795c0b6ea05a93a3d3ea72821`, `29ff92de94000d0c0d4ae56f6ace0e8f11ecc58d`, `4f08f7be2b6101a0d74e8d64bf374df6c52d2029`, `d1985658a2a504aaa283e8351ffe8624c4314075`.
- No Ruff/Mypy suppression, ignore, configuration weakening, test removal or cast was added. Fresh finished CI on the final documentation-updated head is required before declaring this correction green.

## 2026-11-04 — Full port diff audit against immutable pre-port backup

Compared PR #5 branch against `backup/2026-11-04/pr5-pre-typing-port` (SHA `02b7379b3e04f484555bfb7e814ea238980789a8`). GitHub compare reports 17 changed code files plus the three audit documents listed below. Each code hunk was inspected against the pre-port file.

| File | Classification | Evidence |
|---|---|---|
| `backend/app/core/api_docs.py` | Annotation only | Added `ApiDocsConfig(TypedDict)`, return annotation and no-op `cast(str, ...)`; docs URL values and production/development branches are unchanged. |
| `backend/app/core/rate_limit.py` | Annotation only | Added `RedisClient(Protocol)`, attribute/return annotations and no-op casts. Both Lua scripts, key construction, TTL arguments, fallback branches, claim/complete/result method bodies and rate-limit policies are unchanged. |
| `backend/app/core/safe_http.py` | Annotation only | Added no-op casts around socket address typing and response.data assignment; same address normalization, response body assignment, TLS verification, request and redirect behavior. |
| `backend/app/models/activity.py` | Annotation only | `id` uses `Mapped[int] = mapped_column(...)`; same Integer primary key/index config. All other columns unchanged. |
| `backend/app/models/ai_usage.py` | Annotation only | `id` uses `Mapped[int] = mapped_column(...)`; same Integer primary key/index config. All other columns unchanged. |
| `backend/app/models/audit_log.py` | Annotation only | `event_type` uses `Mapped[str] = mapped_column(...)`; same String, nullable and index settings. |
| `backend/app/models/feature_flag.py` | Annotation only | `is_enabled` uses `Mapped[bool | None] = mapped_column(...)`; same Boolean/default=False and inferred nullable behavior. |
| `backend/app/models/invitation.py` | Annotation only | `id` uses `Mapped[int] = mapped_column(...)`; same Integer primary key/index config. |
| `backend/app/models/lead.py` | Annotation only | `id` uses `Mapped[int] = mapped_column(...)`; same Integer primary key/index config. |
| `backend/app/models/lead_note.py` | Annotation only | `id` uses `Mapped[int] = mapped_column(...)`; same Integer primary key/index config. |
| `backend/app/models/organization.py` | Annotation only | `id` uses `Mapped[int] = mapped_column(...)`; same Integer primary key/index config. |
| `backend/app/models/subscription.py` | Annotation only | `id` uses `Mapped[int] = mapped_column(...)`; same Integer primary key/index config. |
| `backend/app/models/user.py` | Annotation only | `id`, credential-digest attribute, and nullable tenant reference use SQLAlchemy 2.0 `Mapped`/ `mapped_column`; primary-key, String/not-null, Integer/FK/nullable settings unchanged. `role_id`, `is_active`, and other fields unchanged. No cast used. |
| `backend/app/services/audit_dashboard_service.py` | Annotation only | Added `dict[str, int]` annotation to existing empty summary dictionary; same object and accumulation logic. |
| `backend/app/services/crm_service.py` | Annotation only | Added float annotations to close_rate/win_rate. Corrected the temporary `0.0` initializers back to original integer `0`, preserving zero-case JSON numeric representation. |
| `backend/app/services/osint_service.py` | Annotation only | Added a no-op cast for the certificate dictionary; same socket call and output logic. |
| `backend/app/services/revenue_forecast_service.py` | Annotation only | Added float/int annotations; restored original integer `0` initial values for pipeline_value, weighted_revenue and close_rate, preserving zero-case runtime values. |
| `docs/audit/AUTH_SENSITIVE_CHANGES.md` | Docs only | Corrected the historical Redis protocol entry and linked the design note. |
| `docs/audit/PROGRESS.md` | Docs only | Audit progress and owner-decision evidence. |
| `docs/audit/REFRESH_PROTOCOL.md` | Docs only | New design note; no application code. |

No schema, Pydantic schema, API response model or serializer files are in the compare result. For the model changes, SQL column types, defaults, primary keys, foreign keys, indexes and explicit nullability are preserved; `Mapped` annotations and `mapped_column` are the SQLAlchemy 2.0 declarative mapping form. No database migration was added.

**Security-sensitive scope check:** no changed file is `auth.py`, `security.py`, `rbac.py`, `tenant.py`, `client_ip.py`, `main.py`, JWT configuration, or proxy-IP resolver. The auth route file is byte-for-byte identical to the pre-port backup. The only rate-limit file changes are typing declarations/casts; there are no runtime hunks in refresh, rate-limit keying, auth, JWT, RBAC, tenant isolation or proxy-IP behavior. The previously alleged `rate_limit.py` violation remains withdrawn.

**Non-annotation runtime drift found and corrected:** CRM/revenue initial numeric literals had briefly changed from integer `0` to float `0.0`. They have been restored to `0` while retaining variable annotations in commits `5a8838e5c8814564718b8fc01374e50d3a636e8f` and `b6687c835e9339518114dad43f8c327822480405`. Thus the final port audit contains no intended runtime behavior changes.

## 2026-11-04 — PR #5 verification and PR #6 branch status

### PR #5 finished CI on the reviewed code head
- Reviewed head: [PR #5 current code head](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/commit/d8acd2b0519f2e8b082219e7acfc641bb4fca506).
- [Security Tests run 41732576285](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41732576285): all jobs completed green. `backend-quality` ran; Ruff passed; Mypy reported zero errors across 118 source files. Backend regression suite: **126 passed, 0 failed, 0 skipped, 243 warnings**. This exactly matches the pre-port passing test count of 126; no tests were removed and the count did not drop. Frontend lint, frontend regression tests and production build passed.
- [Dependency Audit run 41732576260](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41732576260): `python-audit` and `npm-audit` completed green; pip-audit reported no known vulnerabilities and npm audit reported 0 vulnerabilities.
- [Secret Scan run 41732576172](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41732576172): completed green; Gitleaks diff scan reported no leaks in the scanned change range.
- [Full-history Gitleaks audit run 41732569955](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41732569955): audit workflow completed successfully but reported **3 findings**: two `generic-api-key` metadata findings in audit documentation and the existing historical JWT assignment finding at `backend/app/core/security.py`, commit `c06218f640b5765746cf98916f3a92792992dfb7`. The values were redacted by the audit workflow and are not reproduced here. No baseline or suppression was added. Treat the two documentation findings as UNVERIFIED until independently adjudicated; JWT rotation remains UNVERIFIED.
- These finished runs correspond to the reviewed code head above. Subsequent changes in this section are documentation-only.

### PR #6 unchanged-head reconfirmation
- PR #6 remains on its existing head `86121487d509a302e60bcaf76d1c122d18a55f10`, targeting the same base branch `feat/security-hardening` as PR #5.
- [Security Tests run 41557633460](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41557633460): `backend-quality`, `backend-security-tests` and `frontend-checks` completed green.
- [Dependency Audit run 41557633335](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41557633335): Python and npm audits completed green.
- [Secret Scan run 41557633307](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41557633307): Gitleaks diff scan completed green.
- [Full-history audit run 41557626920](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41557626920): completed successfully with the one historical JWT finding; no baseline or suppression.

### Sync / merge gate
- PR #5 and PR #6 are sibling branches; both target `feat/security-hardening`. PR #6 is not stacked on PR #5.
- No branch merge was performed. The instruction “Never merge” remains controlling; therefore no PR #5-to-PR #6 merge commit was created. PR #6 remains unchanged.
- PR #4 remains open and unmerged. `main` was not touched. JWT and PostgreSQL credential rotation remain UNVERIFIED.
- Docker Step 6 remains BLOCKED: full-history Gitleaks still has 3 findings (2 documentation findings not adjudicated and 1 historical JWT finding), and the explicit no-merge rule prevents the requested branch sync.

## 2026-11-04 — Owner decision: Redis protocol retained; corrected provenance and fail-closed evidence

### Redis protocol provenance and port diff
- Correct first-add commit: [`cd8a21f1c18c0b89ff271ea47005b5e9787839d9`](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/commit/cd8a21f1c18c0b89ff271ea47005b5e9787839d9), message `fix(auth): make refresh rotation claims atomic and idempotent`. Its parent is `4f457e170256790cc51676e86eead73a21098054`; fetching `backend/app/core/rate_limit.py` from that parent confirms neither script nor `begin_refresh_rotation` exists there. The introducing commit adds both scripts and the first claim/complete/result implementation. A local `git log -S` could not be run because the environment could not resolve github.com for clone; GitHub commit patch + parent-file verification establishes the first-add commit without claiming the local command ran.
- Refinements: `42f4219f4267ec393f94327972c0f3264710a030` adds the result key to the duplicate/grace test; `4bec95dca2719bb842b66d9d7658de33e10d9579` corrects the claim script key count to three.
- Exact string comparisons show both Lua script bodies are identical between immutable pre-port backup `02b7379b3e04f484555bfb7e814ea238980789a8` and current PR #5 branch. `backend/app/routers/auth.py` and the three refresh tests (`test_rate_limit.py`, `test_auth_sessions.py`, `test_redis_refresh_rotation.py`) have identical blob SHAs at both refs. The refresh callers at auth.py lines 199, 223 and 239 are unchanged.
- **Finding withdrawn:** the typing port did not change runtime behavior in `backend/app/core/rate_limit.py`. Its pre-port-to-current changes are typing declarations/casts only. Do not revert the scripts or callers.
- Existing evidence is already recorded in `docs/audit/AUTH_SENSITIVE_CHANGES.md`, PR #5 description and PR #6 description, including the first-add commit, covering tests, finished CI run 41561425429 and `convention not followed: historical`. The design note `docs/audit/REFRESH_PROTOCOL.md` already documents KEYS/ARGV, key suffixes, TTLs, claim/complete flow, crash behavior, local fallback and multi-worker limitation, plus Redis Cluster hash-slot requirement.

### Redis outage behavior and limitation
- Production `_redis()` requires a configured URL and performs a ping on initial client creation. Missing URL or failed ping raises `RateLimitBackendUnavailable`; Redis operation exceptions in claim, completion and result lookup also raise it outside local mode. The auth refresh route catches it and returns HTTP 503 with `Retry-After: 5`; it does not issue replacement cookies.
- Route-level test `backend/tests/test_auth_sessions.py::test_refresh_fails_closed_when_session_backend_is_unavailable` injects `RateLimitBackendUnavailable` from `begin_refresh_rotation` and asserts HTTP 503. The missing-result test also asserts HTTP 503. The live Redis integration test verifies atomic Redis claims, cached result and post-grace replay against a real isolated Redis service.
- **UNVERIFIED / STOP:** no test currently forces an actual Redis TCP/socket outage against the refresh route. The code path handles the resulting connection exception as above, but live outage behavior is not end-to-end integration-tested. Per owner instruction, do not proceed past this gap until the owner accepts the code-path + injected-exception evidence or authorizes a dedicated outage test.
- Local/development/desktop/test mode may fall back to process-local dictionaries protected by a thread lock. This coordinates threads in one process only; it does not coordinate separate backend worker processes and is unsafe for multi-worker refresh single-use guarantees. Production does not use the fallback.
- Redis Lua multi-key scripts require the keys to share one cluster hash slot. Current independently SHA-256-derived key names do not guarantee that. Supported for the single Redis node in Compose; not Redis Cluster-ready.

### Model typing: no casts used
- The 12 earlier Mypy assignment diagnostics were caused by declaring `Mapped[T]` while assigning SQLAlchemy Core `Column(...)` objects. No cast was used. Root-cause correction is now present: all 12 declarations use SQLAlchemy 2.0 `Mapped[T] = mapped_column(...)` and restore `from sqlalchemy.orm import Mapped, mapped_column`.
- Current locations: activity.py:17; ai_usage.py:17; audit_log.py:37; feature_flag.py:35; invitation.py:18; lead.py:17; lead_note.py:17; organization.py:16; subscription.py:17; user.py:18, 35, 40.
- The prior exact Mypy errors are retained in the review report; current CI on PR #5 head `e1be03641e88e7215b475058467d040a9b5c8561` reports zero Mypy errors. No cast or security-sensitive field narrowing was introduced.

### Current PR #5 checks
- PR #5 reviewed head: `e1be03641e88e7215b475058467d040a9b5c8561`.
- Security Tests run [41732798145](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41732798145): frontend-checks, backend-security-tests and backend-quality all completed green. Ruff passed; Mypy reports zero issues in 118 files; backend tests 126 passed, 0 failed, 0 skipped, 243 warnings; frontend lint, regression tests and build passed.
- Dependency Audit run [41732798154](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41732798154): pip-audit and npm audit both completed green; no known vulnerabilities.
- Gitleaks diff scan run [41732798096](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41732798096): completed green, no leaks in the scanned diff range.
- Full-history Gitleaks run [41732569955](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41732569955) was on the preceding code head `d8acd2b0519f2e8b082219e7acfc641bb4fca506`, not the current docs-only head. Do not represent it as a current-head run. Full-history status on current head remains to be verified.
- PR #6 remains unchanged at `86121487d509a302e60bcaf76d1c122d18a55f10`. Both PRs are siblings targeting `feat/security-hardening`; no merge is applicable. The explicit rule “Never merge” also prohibits the requested PR #5-to-PR #6 merge, so no merge/sync will be performed.



## 2026-11-04 — Live Redis outage characterization test implementation

- Owner authorized dedicated live Redis outage tests; clarified that concurrency means exactly one rotation, with duplicate requests allowed to receive the identical cached replacement pair. No production code was changed.
- Existing backend workflow `.github/workflows/security-tests.yml` already provisions Redis 7.4 as a real service and runs `pytest -q`; it sets `REDIS_TEST_URL`. Added a CI-only step to expose the service container ID so the characterization test can stop/restart the real Redis service between claim and completion. The existing 1.5-second `socket_connect_timeout` and `socket_timeout` remain unchanged.
- Added `backend/tests/test_redis_refresh_outages.py` with cases a–f: pre-request closed endpoint; real Redis stop after claim and restart in teardown; real Redis `CLIENT PAUSE` and socket timeout; recovery/result expiry; production-vs-explicit-local fallback; ten concurrent refresh requests released by a barrier. TTL polling uses `time.monotonic()` deadlines. Redis test keys are registered for teardown cleanup.
- Concurrency assertions require 10 successful requests to return byte-identical access/refresh cookie pairs, exactly one Redis consumed claim and one cached result, no 5xx, then 401 reuse rejection after result TTL and session-family version increment. The application uses stateless JWTs and has no per-token database row; the Redis claim/result state is the persisted rotation record.
- Redis key names are SHA-256-derived from JTI. The result value contains the serialized JWT pair and has the 5-second TTL. Claim key default TTL is 7 days; in-flight and result keys default to 5 seconds. Test does not alter these defaults.
- Compose persistence verified: Redis starts with `--appendonly yes --save 60 1000`, stores `/data` in `redis_data`; result JWT values can be written to AOF/RDB while live. Documented as a Phase 3 security consideration; no persistence setting changed.
- Design note updated in `docs/audit/REFRESH_PROTOCOL.md`; audit coverage appended to `docs/audit/AUTH_SENSITIVE_CHANGES.md`. PR #5 and PR #6 descriptions are pending their matching coverage/run evidence update.
- Test implementation commits: `6a350c79b62fa70c8678f785a5578d05af86eae5`, `31959ca85446862c5948c1789b9e378dfd0db070`, `1dc67924aacf4670acdcafb056cb463f34eb09e3`, `cc80e219c8f157ef791ea42fb432190ef40b338e`, `5fcbff992bf9d1f8150343319aa2dceb6abcd609`; workflow wiring commit `ba7195a0a3a69e686caefa0821b32993eaf98afd`; design note commit `bf9e76c86107dc9022fbaaa045d3239c77717215`.
- Characterization workflow [41735551017](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41735551017) was observed queued on PR #5 head `5fcbff992bf9d1f8150343319aa2dceb6abcd609`. No result is claimed until completion. Documentation commits after that head will require a fresh final-head CI run.
- No merges; `main` untouched; PR #4 remains open. JWT and PostgreSQL credential rotation remain UNVERIFIED. Docker Step 6 remains blocked pending finished green current-head checks and the Gitleaks review gates.


## 2026-11-04 — Redis characterization test-isolation diagnosis and test-only correction

- Diagnosed the two HTTP 401 failures in [run 41735551017](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41735551017). Both failing tests created a fresh SQLite user with ID 1 and a new refresh JWT with session_version 0, while the shared Redis DB 15 retained `user-version:1=1` from the preceding reuse-detection test. The route checks the Redis session version before the JTI claim and therefore correctly returned `{"detail":"Refresh session expired"}`. The failure was test-state contamination; no production defect was indicated.
- Existing refresh regression tests use a fresh in-memory RateLimitManager and do not share Redis user-version state. The new live Redis tests used a shared Redis DB and their cleanup deleted only the three JTI-derived keys, not the user-version key.
- Test-only corrections: assign a unique integer user ID per SQLite fixture; flush the dedicated Redis test DB before and after each test; add healthy same-fixture request controls to the post-claim outage, paused-Redis and production-fallback cases; assert the paused request raises the Redis client's timeout exception and completes within the 1.5-second timeout envelope. No production source changed.
- CI hygiene correction: mask both the ephemeral JWT test key and its serialized JSON value before exporting it through `GITHUB_ENV`. The earlier run exposed the ephemeral test key in its job environment; no production signing key was involved. The key is not repeated here.
- The failed run recorded 254 warnings versus the earlier 243-warning baseline. Pytest attributed 11 warnings to the new `test_redis_refresh_outages.py` module; the other 243 warnings were from the existing suite. Warning categories include the existing Passlib `crypt`, Starlette/httpx deprecation and SQLAlchemy `datetime.utcnow()` deprecation warnings.
- Test-only fix commits: `e6ade77adb48ecb4d059e18314eacb5070806c88`, CI key masking `ff9a64f26445e4aa314a420f92d93bc930042208`, and test formatting `054b44c95bdac6d6c4e8f8512bbb076c22d6b32c`. Current-head validation is pending; no result is claimed until finished.
- No production code, Redis persistence settings, token policy, JWT/PostgreSQL rotation, or main branch changed. No merges. PR #4 remains open. Docker Step 6 remains blocked.



## 2026-11-04 — Finished current-head validation and history scan

- Current PR #5 source/CI head at validation: 1010b150ce6817fb637f45eaedb8f0f894dad0ab. Compared with failed-run head 5fcbff992bf9d1f8150343319aa2dceb6abcd609, seven commits were added; changes are limited to test fixture/controls, CI test-key masking, full-history Gitleaks workflow wiring, and audit documentation. No production source file changed.
- [Security Tests 41738304955](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41738304955) finished green: backend 132 passed, 0 failed, 0 skipped, 257 warnings; Ruff passed; Mypy 0 issues in 118 source files; frontend lint, regression tests and build passed. The ephemeral JWT test key was masked in the Actions environment.
- [Dependency Audit 41738304835](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41738304835) finished green: npm audit found 0 vulnerabilities; pip-audit found no known vulnerabilities.
- [Secret Scan 41738305269](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41738305269): PR diff scan passed. Added explicit all-ref Gitleaks scan; it examined 705 commits and failed with 3 historical findings: 2 generic-api-key false positives in old documentation (a schema wording line and a commit SHA) and 1 historical hardcoded JWT SECRET_KEY assignment in backend/app/core/security.py. Output was redacted; no secret value is reproduced. No baseline, suppression, history rewrite or purge was performed.
- Warning delta: 257 total versus 243 baseline (+14). Pytest attributes the 14 additional warnings to tests/test_redis_refresh_outages.py; they are SQLAlchemy datetime.utcnow() deprecations from fixture-driven model defaults. No warnings were suppressed.
- Redis persistence analysis is recorded in REFRESH_PROTOCOL.md: Redis holds consumed claims and session-version revocations; database does not backstop these keys; total Redis state loss can allow a still-valid rotated token to be accepted. Recommendation is encrypted cached result values with an external key (Option C), pending owner approval. Redis volume and backups are treated as live-token material; Phase 3 backup must exclude redis_data until the decision is approved.
- JWT signing-key rotation and PostgreSQL credential rotation remain UNVERIFIED. Full-history Gitleaks is not green, so the security gate is not fully green. Docker Step 6 remains blocked.
- No production code or persistence settings changed. main untouched; PR #4 remains open. No merge was performed; the standing rule "Never merge" takes precedence over the conflicting PR #5-to-PR #6 merge request. PR #6 head remains unchanged pending final head verification.
