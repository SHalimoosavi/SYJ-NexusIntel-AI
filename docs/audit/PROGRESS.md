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
