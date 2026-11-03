# SYJ NexusIntel AI — Release Plan

**Baseline:** `main` @ `d2669b9264ed5de189facfcaafd3cd76f26cd965`  
**Planning date:** 2026-11-01  
**Principle:** security and reproducibility before licensing mechanics or desktop packaging.

## Release position

Do not distribute the current code as a commercial production release. The current repository is an early SaaS/CRM foundation with substantial feature code, but P0 security issues and missing quality gates prevent a safe release. Estimates below are engineering effort, not calendar promises; they assume one experienced full-stack engineer plus QA/security review and exclude external approvals.

## Phase 1 — Baseline audit (current branch: `audit/baseline`)

**Deliverables:** `AUDIT_REPORT.md`, `ROADMAP_STATUS.md`, `RELEASE_PLAN.md`, and dependency license inventory.  
**Status:** documentation prepared from repository inspection. Runtime/build tests remain UNVERIFIED because the audit runner could not clone GitHub due to network/DNS restrictions.  
**Exit:** owner review of risks and acceptance of P0 remediation scope.

## Phase 2 — Security and production foundation

**Proposed branch:** `feat/security-hardening`  
**Estimate:** 2–4 engineering weeks, depending on tenant boundary breadth and test coverage.

### P0 work

1. Rotate JWT signing key anywhere the historical literal was reused; invalidate all existing sessions. Record rotation completion without exposing values.
2. Remove all login debug alerts and redact sensitive data from logs/errors.
3. Replace JavaScript-readable cookie with a server-managed session or secure HttpOnly cookie architecture. Define CSRF protection for cookie-authenticated state changes, secure attributes, token expiry, revocation and inactive-user handling.
4. Build a complete route authorization matrix. Make organization administration SUPER_ADMIN-only where appropriate; restrict owners/managers to their own organization; apply tenant filters to all tenant-owned records.
5. Add OSINT SSRF defenses: parse and canonicalize hostnames; reject localhost, private, loopback, link-local, multicast, reserved and metadata IPs; resolve and validate all A/AAAA answers; revalidate redirect destinations; defend against DNS rebinding; set strict timeouts/response limits; restrict protocols/ports; isolate outbound network.
6. Replace domain-derived report filenames with UUIDs or safe slugs; enforce storage root containment and escape all report text.
7. Add request throttling for login, OSINT and report generation, with quotas enforced atomically.
8. Add regression tests for every P0 finding, including two-tenant fixtures and unauthorized role matrices.

### P1 foundation

- Add Alembic and a baseline migration; stop using `create_all` as production schema management.
- Add DB readiness check, transaction boundaries, structured logging and request IDs.
- Validate settings at startup with a typed configuration schema; add sanitized `.env.example`.
- Replace hardcoded frontend API origin with build/runtime configuration.
- Add CI for backend tests/lint/type checks, frontend lint/type/build, secret scanning and dependency auditing.

**Exit gate:** all P0 tests pass; no critical/high unresolved security findings; CI required on PRs; migration upgrade tested on a copy of production data; key rotation verified.

## Phase 3 — Commercial licensing (only after owner approval)

**Proposed branch:** `feat/licensing`  
**Estimate:** 1–2 engineering weeks for technical implementation; legal review is separate.

Deliver:
- Proprietary `LICENSE` template with owner/company placeholders and counsel review.
- EULA template with territory, term, fees, permitted users/devices, restrictions, support, warranty/liability, privacy/data handling, termination, governing law and dispute placeholders.
- Full `THIRD_PARTY_NOTICES` generated from resolved backend/frontend dependencies and packaged artifacts.
- Dependency SBOM (CycloneDX or SPDX) and license policy gate.
- Ed25519-signed license claims (product, tier, seats/devices, organization, issued-at, not-before, expiry, grace period, optional feature flags); offline verification uses embedded public key only.
- Separate signing/key-generation CLI held in a restricted private repository or secure operator environment; never ship private signing key.
- Tests for invalid signature, expired key, clock rollback/tampering limits, tier limits, grace window, offline activation and key rotation.

**Commercial model recommendation to evaluate:** per-organization annual subscription with included seat/device allowance and paid tiers. Offer perpetual single-organization only as a higher-priced, explicitly limited maintenance/support option. Final pricing, terms and licensing jurisdiction require owner decision and legal review.

**Exit gate:** legal review completed; dependency obligations cleared; license test suite passes; private signing key storage and recovery procedure documented.

## Phase 4 — Installable Windows/Linux product

**Proposed branch:** `feat/desktop-packaging`  
**Estimate:** 3–6 engineering weeks for first usable release; cross-platform signing and QA may extend calendar time.

### Architecture recommendation

**Tauri 2 over Electron**, subject to a proof of concept. Tauri typically yields smaller installers and uses the platform WebView, while Electron bundles Chromium/Node and is easier for a Node-heavy app. The current backend is Python, so both require a managed sidecar process. Validate Tauri plugin maturity, Python sidecar packaging and OS-specific WebView behavior before committing.

### Local mode

- Add a repository/service abstraction and SQLite as the default local database.
- Use per-user application data directory, not the current working directory.
- Add Alembic migrations and safe first-run migration/backup.
- Keep PostgreSQL as optional server deployment mode; do not require hosted PostgreSQL for local desktop use.
- Make frontend API origin runtime-configurable.
- Build FastAPI sidecar with PyInstaller or Nuitka; include runtime assets, migrations and license public key.
- Shell starts backend on a randomly selected loopback port, waits for authenticated health/readiness, then loads UI. Never bind local backend to public interfaces by default.
- Shell terminates child process on exit and cleans up stale processes/locks.
- First-run wizard: admin creation, license activation, AI provider setup, data location and backup guidance.
- Store provider credentials in Windows Credential Manager, macOS Keychain or Linux Secret Service through a vetted native credential store; never plaintext config or browser storage.
- Offline operation should keep CRM/local analytics available; AI/network features should clearly show "offline" or "provider unavailable" rather than silently returning fabricated data.

### Packaging outputs

- Windows: signed installer via WiX or NSIS; sign binaries and installer with Authenticode certificate; timestamp signatures.
- Linux: AppImage and .deb initially; .rpm optional after validation.
- GitHub Actions matrix: Windows x64, Linux x64; arm64 only if explicitly supported and tested.
- Release artifacts include checksums, SBOM, third-party notices and signature verification instructions.
- Clean-machine smoke tests install, launch, create admin, activate license, create records, restart, migrate/backup and uninstall without deleting user data.

### Auto-update

Use signed update manifests and signed artifacts; validate signature before applying. Provide staged rollout, rollback to previous known-good version, migration compatibility checks and explicit user control. Do not rely on unsigned arbitrary download URLs.

**Exit gate:** signed installers; clean Windows/Linux VM tests; no external cloud dependency in local mode; update rollback verified; data survives restart/upgrade.

## Phase 5 — iOS companion client

**Recommendation:** Capacitor client or PWA connecting to a self-hosted/cloud backend. Do not attempt to bundle/run FastAPI/Python backend natively on iOS. A thin native wrapper is appropriate only if required native APIs justify it.

Requirements:
- Apple Developer Program account and App Store Connect access.
- macOS runner with supported Xcode toolchain and signing certificates/profiles.
- TestFlight distribution and device testing.
- Backend hosted on a reachable HTTPS endpoint (or a user-managed self-hosted endpoint with secure pairing).
- Secure token storage using iOS Keychain; no API secrets embedded in the app.
- Privacy disclosures, data deletion/export, account deletion where required, privacy manifest and App Store review compliance.
- Review risk: apps that are merely website wrappers may be rejected or require substantial native value; ensure useful native capabilities and a polished offline/error experience.

**Exit gate:** TestFlight build accepted for internal testing; auth/session security reviewed; App Store submission checklist complete.

## Phase 6 — Release QA and operations

**Estimate:** 1–2 weeks per release candidate, plus time for external testing.

- P0 and P1 regression suite green.
- Static analysis, type checks, lint, unit/integration/e2e tests, secret scanning, dependency CVE scan, SBOM and license policy scan.
- Database migration/rollback and backup restore drills.
- Windows/Linux clean-machine smoke tests.
- Installer signature and update signature verification.
- Performance test with representative tenant and data volumes.
- Tenant isolation test matrix (read, create, update, delete, export, invite, organization admin).
- Operational runbooks: incident response, key rotation, data restore, license recovery, update rollback, support diagnostics.
- Release notes, known issues, compatibility matrix and checksums.

## External owner inputs needed before later phases

1. **Signing certificates:** Windows Authenticode certificate and Apple Developer signing access; Linux package signing identity if desired.
2. **Apple account:** Apple Developer Program membership and App Store Connect access for iOS.
3. **Domain:** final product website/API/download domain and email domain, if cloud sync/licensing portal is planned.
4. **License terms:** annual/perpetual policy, seat/device definitions, offline grace period, refund/support terms, permitted territories and legal entity/copyright wording.
5. **AI provider policy:** which providers are supported and whether keys are customer-owned (BYOK) or organization-managed.
6. **Deployment access:** optional read-only Vercel/Railway project access or sanitized deployment logs for independent verification. Do not send credentials or secret values in chat.

## Approval gate

This plan is advisory until approved. Phase 1 changes only audit documentation on `audit/baseline`. No Phase 2 security code, licensing implementation, installer work or iOS project work should begin without explicit owner approval.
