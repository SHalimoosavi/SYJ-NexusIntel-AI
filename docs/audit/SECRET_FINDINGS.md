# Secret Exposure Findings — SYJ NexusIntel AI

**Audit date:** 2026-11-01  
**Repository:** `SHalimoosavi/SYJ-NexusIntel-AI`  
**Branch for this report:** `feat/security-hardening`  
**Scope:** Git-history evidence, current branch/tag/PR snapshots, and current secret/configuration files. No credential was tested against a live service. No production data or credential was accessed.

> **Security rule:** Every secret literal that has ever appeared in Git history must be treated as compromised, even if it was later deleted from the working tree. Deleting a value from a later commit does not remove it from earlier commits, tags, clones, forks, caches or PR refs.

## Executive summary

- **Confirmed historical credential exposure:** 1 hardcoded JWT HS256 signing key. **Additional credential-like finding:** 1 PostgreSQL connection URL containing a username/password pair in `.env.example:4`; it is unverified whether the pair is a dummy/local-only value or was ever used. Treat it as compromised and rotate it if it was provisioned or reused.
- **Additional unclassified scanner match:** 1 occurrence — the previous one-time Gitleaks report recorded two matches across 322 commits, but its JSON artifact was ephemeral and the second match's path/commit/line/type was not retained. It may be a repeat occurrence or a distinct finding; this is **UNVERIFIED**.
- **Other confirmed literal exposures:** no AI provider key, OAuth client secret, SMTP credential, Railway/Vercel token, webhook signing secret or PEM private key was confirmed in the newly scanned 16-commit batch, the four post-baseline main commits, or inspected current configuration. The earlier 48-commit batch has no retained raw scan artifact; category-by-category absence there remains **UNVERIFIED**. The PostgreSQL URL in `.env.example:4` is separately recorded below as a credential-bearing candidate.
- **Historical JWT key is still recoverable from Git history and all 24 repository tags inspected**, despite not appearing in the current three branch snapshots or the two current PR head snapshots.
- **Rotation status:** UNVERIFIED. No live credential checks were performed. The PostgreSQL example URL has not been tested; treat its embedded pair as compromised until the owner confirms it was never used and replaces it.

## 1. Confirmed finding: historical JWT signing key

| Field | Evidence |
|---|---|
| Type | Hardcoded JWT HS256 signing key |
| File | `backend/app/core/security.py` |
| Introducing commit | `c06218f640b5765746cf98916f3a92792992dfb7` |
| Introducing line | 6 |
| First confirmed appearance | `c06218f640b5765746cf98916f3a92792992dfb7`, line 6 |
| Last confirmed appearance | `97d29d73178c44a0efd8da2c3d0e94298734b086`, line 6 |
| Removal commit | `827aad3701b3e25843d56804e6ee21e8e2dab55f` |
| Removal detail | The removal commit's parent is `97d29d73178c44a0efd8da2c3d0e94298734b086`; the literal is present in that parent tree and absent from the post-removal source file. |
| Masked value | `****` |
| Validity / deployment | **UNVERIFIED** — never tested against a live service; whether it was deployed or reused is unknown. |
| Rotation required | **YES — mandatory.** Treat as compromised regardless of deployment status. |

**Correction to the earlier register:** commit `97d29d73178c44a0efd8da2c3d0e94298734b086` did not introduce the key. It is the parent of the removal commit and is the last confirmed commit whose tree still contains it. The initial commit `c06218f640b5765746cf98916f3a92792992dfb7` introduced it.

### Where the JWT literal remains present

The three current branch heads were checked:

| Ref | Result |
|---|---|
| `main` at `e51373d276b443581367f2c19aa291ebf2a042d3` | No hardcoded JWT literal in current `backend/app/core/security.py` |
| `feat/security-hardening` at `a196fa84ae66a84cfb1e4837130f0a4cb20be42f` | No hardcoded JWT literal in current `backend/app/core/security.py` |
| `audit/baseline` at `c2b71f367327cc105ba886b2816900fbc34eab6d` | No hardcoded JWT literal in current `backend/app/core/security.py` |

The two PR head snapshots were also checked:

- PR #1, `audit/baseline` head `c2b71f367327cc105ba886b2816900fbc34eab6d`: no hardcoded literal in the current source file.
- PR #2, closed/unmerged historical head `fdc04b028963a28bb0f7dd75310a94f231d29ec2`: no hardcoded literal in the current source file.

**All 24 repository tags inspected still contain the hardcoded JWT literal** in `backend/app/core/security.py` (same blob SHA `e06327758eb83e87c2d09146d936632ea31f079c`):

- `phase5.2b-stable`
- `v0.4-security-complete`
- `v0.4.0-checkpoint`
- `v0.5-business-intelligence`
- `v0.5.0-checkpoint`
- `v0.6-backend-release-candidate`
- `v0.6.0-checkpoint`
- `v0.7.0-checkpoint`
- `v0.7.2-checkpoint`
- `v0.8.0-checkpoint`
- `v0.9.1-checkpoint`
- `v0.9.2-checkpoint`
- `v0.9.2-fullstack`
- `v1.0-commercial`
- `v1.0.0-phase10-start`
- `v1.0.1-opportunity`
- `v1.1.0-crm`
- `v1.2.0-crm-analytics`
- `v1.3.0-dashboard`
- `v1.4.0-executive-ai`
- `v1.5.0-demo`
- `v1.5.1-smart-scoring`
- `v1.6.0-multi-agent`
- `v1.7.0-platform-core`

**Conclusion:** The value is still recoverable from Git history and tags. Current-branch deletion is not remediation. No tag or branch was deleted or modified. No history purge was attempted.

## 2. Additional credential-bearing PostgreSQL URL

| Field | Evidence |
|---|---|
| Type | PostgreSQL connection URL with embedded username and password |
| File | `.env.example` |
| Introducing commit | `c0e2705da78d2568dcb38181728fa0701b48e4ed` |
| First appearance | `c0e2705da78d2568dcb38181728fa0701b48e4ed`, line 4 |
| Last confirmed appearance | `c0e2705da78d2568dcb38181728fa0701b48e4ed`, line 4; file remains present at current `feat/security-hardening` HEAD `a196fa84ae66a84cfb1e4837130f0a4cb20be42f` |
| PR exposure | Present in closed, unmerged PR #2 head `fdc04b028963a28bb0f7dd75310a94f231d29ec2`; absent from current `main` and `audit/baseline` snapshots |
| Masked value | `****` |
| Validity | **UNVERIFIED** — the URL contains a username/password pair and a local/service hostname. No connection attempt or live credential test was made. It may be sample-only, but that is not proven. |
| Rotation action | Treat as compromised. Rotate the database username/password if the pair was ever provisioned, reused, copied into a deployment secret store or used by any environment. Replace the example with non-credential placeholders. |

The URL was added by `c0e2705da78d2568dcb38181728fa0701b48e4ed` and is still present in the feature branch. It was not found in the current `main`/`audit/baseline` trees or the 24 tag trees inspected. The file is an example file, not proof of production use; deployment validity remains **UNVERIFIED**.

## 3. Unclassified Gitleaks match

| Field | Evidence |
|---|---|
| Type | Unclassified Gitleaks match; not yet proven to be a distinct credential |
| File path | **UNVERIFIED** — original JSON report not retained |
| Commit | **UNVERIFIED** |
| Line | **UNVERIFIED** |
| First / last appearance | **UNVERIFIED** |
| Masked value | `****` |
| Validity | **UNVERIFIED** |
| Rotation action | Recover the already-generated report if available. If it resolves to a credential literal, rotate it immediately. Do not infer a credential type or test it against a live service. |

The prior report records **2 matches across 322 commits**. One is the confirmed JWT finding above. The other match's metadata was not persisted. It is not valid to claim two distinct exposed credentials based on this count.

## 4. Other credential categories

The remaining 16 commits of the documented 64-commit baseline were inspected once, in one batch. The prior 48-commit review was not repeated. Four post-baseline commits associated with the accidental helper-file add/delete sequence were separately inspected. Current branch configuration files were checked for literal credential patterns.

| Category | Evidence / result | Rotation decision |
|---|---|---|
| Database URLs and passwords | Initial commit `c06218f640b5765746cf98916f3a92792992dfb7`, `backend/app/database/database.py`, contains environment/local SQLite configuration, not a confirmed live DB credential. Separately, commit `c0e2705da78d2568dcb38181728fa0701b48e4ed` adds a credential-bearing PostgreSQL URL at `.env.example:4`; it remains in the current feature branch and closed PR #2 snapshot, but is absent from `main` and `audit/baseline`. Username/password presence is confirmed; whether they are real, valid or ever deployed is **UNVERIFIED**. | Treat as compromised; rotate immediately if ever provisioned or reused. Do not test it. |
| AI provider keys | No literal provider key pattern confirmed in the 16-commit batch, four post-baseline commits, or current inspected config files. Prior 48-commit register says no other literal API/cloud key was confirmed, but raw report is unavailable. | **UNVERIFIED** for exhaustive historical absence; inspect provider secret stores privately. Rotate any key found in Git or reused from an exposed environment. |
| OAuth client secrets | No literal OAuth client secret confirmed in the newly scanned commits/current inspected config. Earlier raw scan metadata is unavailable. | **UNVERIFIED**; rotate only if a literal/reuse is established by private provider inventory. |
| SMTP credentials | No literal SMTP password or credential confirmed in the newly scanned commits/current inspected config. Earlier raw scan metadata is unavailable. | **UNVERIFIED**; rotate only if a literal/reuse is established. |
| Railway / Vercel tokens | No literal platform token confirmed in the newly scanned commits or current inspected CI/deployment files. The Railway API base URL is a public endpoint, not a credential. | **UNVERIFIED** for all historical categories; review provider token inventory privately. |
| Webhook signing secrets | No literal webhook signing secret confirmed in the newly scanned commits/current inspected config. Prior register records no confirmed webhook secret in the earlier review. | No confirmed value to rotate; exhaustive old-range absence remains **UNVERIFIED**. |
| PEM/private keys | No private-key block confirmed in the newly scanned commit batch or current inspected config. Prior register records no confirmed private-key block in the earlier review. | No confirmed key to rotate; exhaustive old-range absence remains **UNVERIFIED**. |
| Committed `.env` files | No actual `.env` file found in the three current branch trees or any of the 24 tag trees. The security branch contains `.env.example`, `backend/.env.example`, and `frontend/.env.example`; root `.env.example:4` contains a credential-bearing PostgreSQL URL added by `c0e2705da78d2568dcb38181728fa0701b48e4ed`. | No actual `.env` file found, but the credential-bearing example URL must be treated as compromised and rotated if reused. External deployment values remain **UNVERIFIED**. |
| Docker / CI / configuration literals | No credential pattern found in inspected `.env.example`, Railway config, Dockerfiles, Compose file, Gitleaks config, pre-commit config, Dependabot or CI workflows on `feat/security-hardening`. The security test workflow contains a deterministic test-only JWT fixture, not a production credential. | No rotation indicated by these inspected files. Historical absence in the earlier 48 commits remains **UNVERIFIED** where the raw report is unavailable. |

### Historical range coverage

- Previously reviewed range: 48 commits, from `d2669b9264ed5de189facfcaafd3cd76f26cd965` through (exclusive) `762cb3f143c249313d5456473d0a0691047169c1`. Not rescanned.
- Newly reviewed remaining range: 16 commits, from `dc195abdcadf0d5e5825d085c777958c93e85349` through `c06218f640b5765746cf98916f3a92792992dfb7` inclusive.
- Separately reviewed post-baseline main commits: `f9d78ce69f579e6a63468321b12dee1be8dd3ed6`, `346819a75bfb8baccf137972a218ffdcd6b94935`, `010a17619991f9162b2ccac73a821aa9d4115a53`, `e51373d276b443581367f2c19aa291ebf2a042d3`.

## 5. Accidental add/delete sequence

The four post-baseline main commits were inspected:

| Commit | Change | Secret assessment |
|---|---|---|
| `f9d78ce69f579e6a63468321b12dee1be8dd3ed6` | Added `backend/app/core/logging_security.py` | Redaction helper/patterns; no credential literal detected |
| `346819a75bfb8baccf137972a218ffdcd6b94935` | Added `backend/tests/test_log_redaction.py` | Synthetic test values and redaction assertions; no live credential detected |
| `010a17619991f9162b2ccac73a821aa9d4115a53` | Deleted `backend/app/core/logging_security.py` | Reversal; no credential detected |
| `e51373d276b443581367f2c19aa291ebf2a042d3` | Deleted `backend/tests/test_log_redaction.py` | Reversal; no credential detected |

The helper and test contents remain recoverable from their historical commits, but the inspected contents do not contain the historical JWT literal or another confirmed credential. The JWT remains recoverable separately from `c06218f...` and the tags listed above.

## 6. Rotation checklist

Complete these actions privately. Do not paste credentials into ChatGPT, GitHub issues, commits or logs.

1. **Generate a new JWT signing key** using a cryptographically secure random generator. Use a new key identifier (`kid`). Never reuse the historical value.
2. **Update the deployment secret manager** for every environment that may have used the historical key: Railway, staging, local production-like environments, and any external deployment. Do not place the value in source control.
3. **Remove the historical key from all active verification keyrings.** Do not retain it as a fallback or overlap key.
4. **Invalidate existing sessions and tokens** signed with the historical key. Require affected users to authenticate again.
5. **Redeploy every API instance** with the new key configuration. Confirm operationally through deployment configuration and non-secret health checks; do not test the exposed credential.
6. **Review private provider inventories** for DB credentials, AI provider keys, OAuth secrets, SMTP credentials, webhook secrets, Railway/Vercel tokens and private keys. Rotate any value found in Git history or reused in an environment that could have been exposed.
7. **Review provider audit logs** for suspicious use during the exposure window. Keep tokens/passwords out of exported evidence.
8. **Record rotation evidence** as date, environment, service, operator and completion status only. Never record secret values.
9. **Only after rotation is complete**, consider a separate Git history purge. History rewriting is not included in this task and requires separate owner approval. It may invalidate commit SHAs, tags, PR bases, clones, forks, caches and integrations. Rotation remains mandatory even after any purge.
10. **Do not delete tags or rewrite shared history** without explicit separate approval.

## 7. Scanner and verification limitations

- The previous full-history Gitleaks report's JSON artifact was not retained. Its second match cannot be classified from the available evidence.
- The current CI Secret Scan run passed on commit `fdc04b028963a28bb0f7dd75310a94f231d29ec2`, but its workflow is diff-scoped and is not proof that every historical tag is clean.
- The 16-commit historical batch and four post-baseline commits were inspected once. The earlier 48-commit range was not rescanned.
- No credential was tested against a live service. Deployment validity/reuse is **UNVERIFIED**.
- No tag, branch, PR or history was deleted, rewritten, force-pushed or merged.

## Final disposition

**One confirmed historical JWT exposure plus one credential-bearing PostgreSQL URL in `.env.example` whose validity is UNVERIFIED; one additional unclassified Gitleaks occurrence remains unresolved.** The JWT is recoverable from all 24 inspected tags. The PostgreSQL URL remains in the feature branch and closed PR #2 snapshot. Treat both credential values as compromised; rotate any corresponding active or reused credentials. No credential was tested against a live service. No history purge, tag deletion, branch deletion, force-push or merge was performed.
