# Secret Exposure Findings — SYJ NexusIntel AI

**Updated:** 2026-11-01  
**Repository:** SHalimoosavi/SYJ-NexusIntel-AI  
**Working branch:** feat/security-hardening  
**Policy:** Every credential-like value committed to Git is treated as compromised unless positively established to be a synthetic placeholder. No credential was tested against a live service. No history purge was performed or authorized.

## Executive disposition

| Finding | Classification | Rotation action |
|---|---|---|
| Historical JWT HS256 signing key | **CONFIRMED exposed credential** in Git history and tags | **Mandatory rotation**; invalidate tokens/sessions signed by it. Owner rotation status is **UNVERIFIED** because no date/status was supplied. |
| Historical PostgreSQL URL in .env.example:4 | **CONFIRMED credential-bearing URL**; whether synthetic or provisioned is **UNVERIFIED** | Treat as compromised. Rotate/retire the database username/password unless the owner positively confirms the pair was synthetic and never reused. Owner status is **UNVERIFIED**. |
| Gitleaks match in docs/audit/AUDIT_REPORT.md:199 | **FALSE POSITIVE**, not a static credential | No rotation. It is a shell command substitution that generates a key dynamically using Python's secrets module. The current branch no longer contains that historical document path. |
| Other provider/API/OAuth/SMTP/platform/webhook/private-key findings | No additional Gitleaks findings in the full-history scan after rule correction; this is not a guarantee against every possible secret pattern | No additional value confirmed. Owner-side inventory and reuse status remain **UNVERIFIED**. |

The owner's rotation-status fields were left unfilled. Therefore neither JWT nor PostgreSQL rotation is represented as complete. Do not paste secret values or rotation credentials into GitHub, ChatGPT, issues, logs, or this report.

## 1. Confirmed historical JWT signing-key exposure

| Field | Evidence |
|---|---|
| Type | Hardcoded JWT HS256 signing key |
| File and line | backend/app/core/security.py:6 |
| Introducing commit | c06218f640b5765746cf98916f3a92792992dfb7 |
| Last confirmed appearance | 97d29d73178c44a0efd8da2c3d0e94298734b086:6 |
| Removal commit | 827aad3701b3e25843d56804e6ee21e8e2dab55f |
| Masked value | **** |
| Deployment/reuse | **UNVERIFIED**; no live test was made |
| Rotation action | **Mandatory** regardless of whether deployment can be proven |

The literal remains recoverable in all 24 inspected tags:

phase5.2b-stable, v0.4-security-complete, v0.4.0-checkpoint, v0.5-business-intelligence, v0.5.0-checkpoint, v0.6-backend-release-candidate, v0.6.0-checkpoint, v0.7.0-checkpoint, v0.7.2-checkpoint, v0.8.0-checkpoint, v0.9.1-checkpoint, v0.9.2-checkpoint, v0.9.2-fullstack, v1.0-commercial, v1.0.0-phase10-start, v1.0.1-opportunity, v1.1.0-crm, v1.2.0-crm-analytics, v1.3.0-dashboard, v1.4.0-executive-ai, v1.5.0-demo, v1.5.1-smart-scoring, v1.6.0-multi-agent, and v1.7.0-platform-core.

The current implementation now loads signing keys from JWT_SIGNING_KEYS and JWT_ACTIVE_KID, and refuses startup if either is missing, a key is shorter than 32 UTF-8 bytes, a known placeholder/default is used, or the value has obvious repeated-character/low-entropy content. The change is in commit bdbd2357de809df0e58f82cc583b92c0906eb69d; test fixture and workflow corrections are in df66adfee6a33614e87a8c02aca9c8fb02af5064 and 4198d384e64be43210771f7eb0548ae122964fc8.

**Action:** generate a fresh key, set it in every backend runtime secret store, remove the historical key from every verification keyring, redeploy, and invalidate outstanding access/refresh tokens. Follow docs/audit/KEY_ROTATION.md. No key overlap with the compromised value is permitted.

## 2. Historical PostgreSQL credential-bearing URL

| Field | Evidence |
|---|---|
| File and line | .env.example:4 |
| Introducing commit | c0e2705da78d2568dcb38181728fa0701b48e4ed |
| Value | Masked as ****; the full URL is intentionally not reproduced |
| Classification | Username/password-bearing PostgreSQL URL was present in Git history |
| Validity/provisioning/reuse | **UNVERIFIED**; no connection attempt was made |
| Rotation action | Treat as compromised. Rotate/retire the corresponding DB credentials unless the owner confirms they were synthetic and never provisioned or reused. |

The current root example was replaced with the explicit non-secret template postgresql://USER:PASSWORD@HOST:5432/DBNAME in commit 7cce933b47d201f6c651c2596cdfb301a3b58e1e. This cleans the current tree only; the historical value remains recoverable from Git history. The replacement is not a history purge and does not remove the rotation requirement.

The current backend example uses a local SQLite URL and a clearly marked JWT placeholder. The frontend example uses a placeholder backend URL. Docker Compose injects required database/JWT values from the runtime environment rather than embedding credentials. These files were inspected; no other realistic-looking credential value was confirmed in the inspected current examples/configuration.

## 3. Formerly unclassified Gitleaks match — resolved

| Field | Evidence |
|---|---|
| File | docs/audit/AUDIT_REPORT.md (historical path; absent from current feature-branch tree) |
| Commit | 6b66d83191f99fce235aa7262c0863e8a17e5077 |
| Line | 199 |
| Rule ID | syj-legacy-jwt-secret-assignment |
| Classification | **FALSE POSITIVE — dynamic key generation command, not a static secret literal** |
| Rotation action | None for this match |

The line assigns the output of a Python secrets.token_urlsafe(48) command substitution to a shell variable. The original broad custom regex captured part of the shell expression as though it were a literal. The full-history scan initially reported two matches; the second match was traced to this command. The rule was narrowed to accept only static literal characters in commit 28e0b81126ad1eadeca5a89e606cacefc6998a6d.

The subsequent full-history scan run 41335108048 completed successfully and reported exactly one finding: the confirmed historical JWT key at backend/app/core/security.py:6, commit c06218f640b5765746cf98916f3a92792992dfb7. The false positive no longer appears.

## 4. Current secret hygiene controls

- Root .env.example now contains only explicit placeholders; current replacement commit: 7cce933b47d201f6c651c2596cdfb301a3b58e1e.
- .gitignore excludes .env, .env.*, private-key/certificate formats, and local database files, while allowing root and nested .env.example files; same commit.
- Root, backend and frontend Docker ignore files exclude environment files, key/certificate material and local database artifacts; same commit.
- backend/app/core/security.py enforces required JWT configuration and rejects short/default/placeholder/low-entropy keys; commit bdbd2357de809df0e58f82cc583b92c0906eb69d.
- Rotation instructions for Railway, Vercel-backend deployments and local/Docker environments are in docs/audit/KEY_ROTATION.md; same commit.
- Gitleaks default rules plus repository-specific rules, the exact-path/exact-placeholder allowlist, and the full-history metadata workflow are in commit 7043f58b48d164f09904946d35f754969257ca0c. The legacy literal rule was narrowed in 28e0b81126ad1eadeca5a89e606cacefc6998a6d.
- The allowlist is restricted to the two checked-in environment-example paths and the exact verified placeholders USER:PASSWORD, REPLACE_PASSWORD, and REPLACE_WITH_AT_LEAST_32_RANDOM_BYTES. No source, Docker, CI, or deployment path is allowlisted.
- The Gitleaks pre-commit hook is configured in .pre-commit-config.yaml; CI uses .github/workflows/secret-scan.yml and the redacted full-history metadata workflow .github/workflows/gitleaks-history-audit.yml.
- Test JWT keys are generated ephemerally in test setup/CI; commit 4198d384e64be43210771f7eb0548ae122964fc8. No production credential is embedded in the test workflow.

## 5. Scan coverage and limitations

- Previously documented historical review: 48 commits, from d2669b9264ed5de189facfcaafd3cd76f26cd965 through (exclusive) 762cb3f143c249313d5456473d0a0691047169c1.
- Remaining historical batch previously inspected: 16 commits, from dc195abdcadf0d5e5825d085c777958c93e85349 through c06218f640b5765746cf98916f3a92792992dfb7 inclusive.
- Four post-baseline main commits were separately inspected: f9d78ce69f579e6a63468321b12dee1be8dd3ed6, 346819a75bfb8baccf137972a218ffdcd6b94935, 010a17619991f9162b2ccac73a821aa9d4115a53, and e51373d276b443581367f2c19aa291ebf2a042d3.
- The automated history audit scans all fetched refs with full Git history and redacts finding values. It reported one actual finding after the false-positive rule correction (run 41335108048).
- No additional AI provider key, OAuth secret, SMTP credential, Railway/Vercel token, webhook secret or PEM private-key finding was reported by that scan. Scanner coverage is not proof that every possible secret format or private provider inventory is clean.
- No actual .env file was found in the previously inspected three branch trees or 24 tag trees. Current checked-in environment examples are placeholders/local-only values.
- The earlier 48-commit raw scanner artifact was not retained. The newer full-history scan provides refreshed automated coverage; any provider-side reuse remains **UNVERIFIED**.
- No credential was tested against a live service. No production secret store was accessed.

## Final action list

1. Owner: rotate the historical JWT key and invalidate all outstanding tokens/sessions; record date/environment only.
2. Owner: rotate/retire the historical PostgreSQL username/password unless positively confirmed synthetic and never reused.
3. Recheck the latest CI run after commit 4198d384e64be43210771f7eb0548ae122964fc8; earlier test run failure was caused by a static fixture being mistakenly included in the negative test set and was corrected in that commit.
4. History purge remains a separate decision and is **NOT APPROVED** by this task. Do not rewrite history or delete tags/branches.
