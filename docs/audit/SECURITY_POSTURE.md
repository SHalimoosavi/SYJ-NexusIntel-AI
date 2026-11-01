# SYJ NexusIntel AI — Security Posture

**Assessment branch:** `feat/security-hardening`  
**Assessment date:** 2026-11-01  
**Release decision:** **NOT PRODUCTION READY**  
**Verification level:** Source review and test authoring complete for substantial controls; automated execution and infrastructure validation are still pending.

This document describes implemented controls and their evidence. It is not a certification, penetration-test report, or claim that the system is fully secure.

## Controls implemented

| Area | Implemented control | Evidence | Verification state |
|---|---|---|---|
| Secrets | Gitleaks default rules, targeted JWT/legacy `SECRET_KEY` rule, redacted diff-scan CI and pre-commit hook | `.gitleaks.toml`, `.github/workflows/secret-scan.yml`, `.pre-commit-config.yaml` | Diff scan pending; one-time history scan reported 2 matches, metadata not retained |
| JWT | HS256 algorithm pinned; `kid` required; active keyring; access token default 15 minutes; refresh token default 7 days; typed claims, issuer/audience, expiry and JTI checks | `backend/app/core/security.py`, `backend/app/routers/auth.py` | Tests authored; CI pending |
| Session lifecycle | Refresh JTI single-use; replay revokes user session version; logout and password change revoke the session family | `backend/app/core/rate_limit.py`, `backend/app/routers/auth.py` | Route tests authored; Redis persistence dependency remains |
| Authentication | Progressive login delay, IP+email and account-hash lockouts, dummy password verification for unknown users, generic invalid-credential response | `backend/app/routers/auth.py`, `backend/app/services/user_service.py` | Brute-force regression test authored; CI pending |
| Rate limiting | Redis-backed atomic sliding windows; per-IP route limits; stricter auth budgets; per-user and per-organization quotas; local fallback only for local/desktop/test; 429 + Retry-After | `backend/app/core/rate_limit.py`, `backend/app/main.py` | Unit and API tests authored; live Redis integration pending |
| Tenant isolation | DB-derived tenant context, scoped queries, role allowlists, guessed-ID tests and route dependency inventory | `backend/app/core/dependencies.py`, `backend/app/core/rbac.py`, `docs/audit/TENANT_BOUNDARY_MATRIX.md` | Service/API tests authored; not every business flow has a dedicated adversarial test |
| Response minimization | Explicit Pydantic response models; password hashes excluded; user/invitation/audit tenant or actor foreign keys omitted; report filesystem path removed | `backend/app/schemas/`, router response models | Schema tests authored; CI pending |
| Input and SSRF | Domain validation, public DNS checks, pinned-IP HTTPS fetches with hostname TLS validation, manual redirect validation, safe report filenames, bounded CRM/note/activity/agent-memory inputs | `backend/app/core/input_validation.py`, `safe_http.py`, schemas, `report_service.py` | Pinned-transport and DNS-rebinding regression tests authored; WHOIS/DNS egress policy remains a residual risk |
| XSS | React text rendering, nonce-based CSP, script-src without `unsafe-inline`; static check against raw HTML injection APIs | `frontend/proxy.ts`, `frontend/next.config.ts`, `backend/tests/test_static_security.py` | Source/static test authored; browser CSP compatibility pending |
| CORS/CSRF | Explicit HTTPS production allowlist; cookie-authenticated unsafe requests require trusted Origin; HttpOnly/Secure/SameSite cookies | `backend/app/main.py`, `backend/app/core/dependencies.py`, `backend/app/routers/auth.py` | Tests/config review pending |
| Errors/logging | Generic 500 response; exception detail/trace suppressed; email, phone, bearer/JWT and credential assignment redaction | `backend/app/main.py`, `backend/app/core/redaction.py` | Unit tests authored; production logging configuration still needs deployment verification |
| Network | Nginx rate/connection limits, 10 MB body cap, timeouts, gzip, TLS configuration, private backend/Redis network in self-hosted Compose | `docker-compose.yml`, `deploy/nginx/`, `docs/audit/NETWORK_HARDENING.md` | No Docker/Nginx/TLS runtime validation |
| Database | SQLite rejected in production; PostgreSQL TLS required; least-privilege role plan, audit trigger and backup/restore procedure | `backend/app/database/database.py`, `backend/sql/audit_log_immutability.sql`, `backend/sql/application_role_grants.sql`, `docs/audit/DATABASE_OPERATIONS.md` | Trigger/grants and restore drill not applied |
| Audit | Tenant-scoped read API; ORM update/delete guards; PostgreSQL append-only trigger script; actor attribution for authentication, CRM, user/admin, AI usage, invitation and subscription events | `backend/app/services/audit_service.py`, models, services and routers | ORM tests authored; DB trigger not applied |
| Dependencies | Pinned runtime/test dependencies, pip-audit/npm audit workflow and weekly Dependabot | `backend/requirements*.txt`, `.github/workflows/dependency-audit.yml`, `.github/dependabot.yml` | Audit workflows pending; CVE status not yet confirmed |

## Tests added

- Tenant A/B service and API IDOR tests, including guessed IDs for leads, notes, activities, users, organizations and subscriptions.
- Route dependency inventory requiring authentication for every non-public API route.
- RBAC escalation and super-admin-only route tests.
- Redis/local limiter, quota, 429/Retry-After and login lockout tests.
- JWT key ID, algorithm pinning, signature tampering, refresh replay and logout/password-change revocation tests.
- Response-model minimization tests.
- Log redaction, SQL construction, upload endpoint and frontend raw-HTML static tests.
- Private DNS, pinned-IP TLS, DNS-rebinding and internal redirect rejection tests.
- ASGI declared/chunked request-body limit tests.
- Explicit trusted-proxy spoofing tests.
- Proxy spoofing test and Nginx configuration assertions.

These tests are authored but have not yet been confirmed passing in GitHub Actions. The Nginx and ASGI 10 MB body limits are statically asserted and unit-tested for chunked/declared payloads; a real oversized-body request through a running proxy has not been simulated.

## Confirmed secret exposure and scan state

- **CRITICAL:** a hardcoded JWT signing key was present in `backend/app/core/security.py:6`, commit `97d29d73178c44a0efd8da2c3d0e94298734b086`. The value is intentionally not reproduced. Treat it as compromised, rotate it, and invalidate tokens signed with it.
- A one-time automated Gitleaks run scanned 322 commits and reported 2 matches. The runner's JSON report was ephemeral and did not retain per-match path/commit/line metadata. It is unknown whether the two matches represent two distinct values or repeated occurrences. Do not assume a second credential type without evidence.
- The earlier manual review ledger covers 48/64 original main-branch commits; 16 commits were marked UNVERIFIED. The automated Gitleaks scan is not a substitute for a manually triaged 25-commit evidence ledger.
- Continuous CI is now diff-scoped. The full-history scan will not be repeated under the no-rescan rule.
- The historical key's deployment/reuse is unknown. Rotation is required whether or not it was deployed.

## Residual risks and release blockers

1. **Historical JWT key rotation is unconfirmed.** Rotate it in every environment where it may have been used. Do not retain it as a verification fallback. History rewriting requires separate approval; rotation is mandatory even if history is rewritten.
2. **Two Gitleaks matches lack retained metadata.** The known JWT exposure is confirmed; the other match details remain UNVERIFIED.
3. **Redis holds session-version and consumed-refresh-JTI state.** Redis persistence and backup must be enabled in hosted production. Redis data loss could reset revocation/replay state; this needs a durable persistence/restore design or database-backed session state before high-assurance production.
4. **Vercel + Railway split hosting does not make the backend private.** Railway public ingress remains directly reachable. CORS is not an access-control boundary. A private BFF/ingress architecture is required to prevent direct API reachability.
5. **SSRF and network egress:** The shared HTTPS fetch and TLS-inspection paths pin connections to validated public DNS addresses and cap response bodies at 2 MB, closing the ordinary DNS-rebinding gap there. WHOIS/DNS operations still require network egress restrictions blocking private, loopback, link-local, reserved and metadata IP ranges.
6. **No PostgreSQL Row-Level Security is enabled.** Tenant isolation is application-level. RLS is recommended defense-in-depth after transaction-scoped tenant context and migration design are approved.
7. **Database role separation, audit trigger and backup/restore drills are not applied or verified.** Runtime DB user must not own tables or have update/delete/truncate privileges on audit logs.
8. **No independent immutable audit sink exists.** A database owner/superuser can still alter triggers and data; export high-value events to separately administered append-only storage.
9. **No production dependency audit result is confirmed.** pip-audit/npm audit jobs are queued or pending; CVEs may still block release.
10. **Proxy/TLS/CSP infrastructure has not been deployed or runtime-tested.** Nginx syntax, Compose topology, TLS issuance/renewal, cookie behavior and browser CSP must be tested in an isolated staging environment.
11. **AI prompt injection is not currently evidenced as a live LLM-provider path.** Multi-agent orchestration is deterministic. If an LLM provider is added, implement the controls in `AI_INPUT_SECURITY.md` before release.
12. **No backend file-upload endpoint is present.** Any future upload feature requires a dedicated size/type/magic-byte/malware/tenant-storage policy.
13. **Full endpoint data-flow testing remains incomplete.** Route authentication inventory is broad, but all endpoint combinations, IDOR permutations, tenant cache behavior and role transitions need a structured independent test/penetration test.
14. **Main-branch policy incident:** two helper files were accidentally committed to `main` and immediately deleted in compensating commits. Current main tree is restored, but history contains those four commits. This is recorded in `PROGRESS.md`; no further main writes are authorized or planned.

## Recommended independent penetration-test scope

- Auth brute force, credential stuffing, enumeration, refresh replay, logout/password-change revocation, JWT algorithm/kid/signature tampering and cookie/CSRF behavior.
- Cross-tenant IDOR and RBAC bypass across every route, including guessed IDs, list/search filters, exports, reports, invitations and caches.
- SSRF, DNS rebinding, redirect chains, oversized responses, IPv4/IPv6 special ranges, cloud metadata and internal service access.
- Proxy trust and spoofed forwarding headers, TLS downgrade, oversized/slow request bodies, rate-limit evasion and connection exhaustion.
- XSS/CSP bypass, CORS misuse, error/log leakage, report generation path traversal and file access.
- Database least privilege, audit tampering, backup confidentiality and restore integrity.
- Dependency/supply-chain review, CI secret handling and historical credential exposure.

## Release recommendation

Do not deploy this branch to production yet. First rotate the historical JWT key and confirm no other secret exposures; resolve the untriaged Gitleaks matches; obtain passing CI results; apply and verify database role/trigger controls; test Nginx/Redis/PostgreSQL in isolated staging; and run an independent penetration test. No licensing, packaging or installer work is included in this phase.
