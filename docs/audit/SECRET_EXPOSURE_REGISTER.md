# Secret Exposure Register and Rotation Checklist

**Scope:** evidence confirmed from the 48 previously inspected commits and current source review. The remaining 16 historical commits are explicitly UNVERIFIED and were not re-scanned after the interrupted session. No secret values are reproduced here.

## Confirmed secret exposure

| Severity | Secret type | Location | Commit | Line | Status |
|---|---|---|---|---:|---|
| CRITICAL | Hardcoded JWT signing secret (HS256) | `backend/app/core/security.py` | `97d29d73178c44a0efd8da2c3d0e94298734b086` | 6 | Public Git history; compromised by policy. Value redacted. |

The later commit `827aad3701b3e25843d56804e6ee21e8e2dab55f` moved the setting to an environment variable. This does not remove the secret from earlier Git history. Whether the exposed value was deployed or reused is UNKNOWN. Do not add it to any verification key ring.

## Other credential-like items reviewed

- Frontend token helper/debug history (including commits `3c903a405d291a057bbede0c2ad0ecd98d27c22d`, `f15a8f63d0fe3d2be73347a6755a5d74501e7a9f`, and `d61f7c176e59c519b9f0d871cf0f228170ced030`) handled runtime access tokens and included debug logging/storage patterns. The reviewed diff evidence did not establish a literal committed live bearer token. Treat this as a token disclosure vulnerability, not a confirmed static token value.
- `DATABASE_URL`, `SECRET_KEY`, API-key and webhook references found as environment-variable names or deployment instructions are configuration references, not proof of embedded credential values.
- The frontend Railway API base URL is a public service endpoint, not a credential.
- No other literal API credential, database password, cloud key, webhook signing secret, or private-key block was confirmed in the previously inspected 48 commits.
- **UNVERIFIED:** the oldest 16 commits in the repository history were not successfully recorded in the interrupted scan. This register is not a claim that no further secrets exist.

## Mandatory rotation checklist

1. Generate a new independent random JWT signing secret (at least 32 bytes of cryptographic randomness) outside Git and outside chat.
2. Configure only the new secret under a new `kid` in the deployment secret manager. Never reuse the historical key.
3. Set `JWT_ACTIVE_KID` to the new key ID. Keep only explicitly approved, non-compromised verification keys in `JWT_SIGNING_KEYS`; never retain the exposed legacy key as a fallback.
4. Restart/redeploy every API instance with the new key configuration. Confirm the application refuses to start if the keyring or active key is missing.
5. Invalidate all existing sessions/tokens signed by the historical key. Require users to authenticate again; do not attempt a graceful overlap with the compromised key.
6. Review Railway and any local/staging deployment secret stores for legacy `SECRET_KEY` values. Rotate if present; remove obsolete variable names after confirming the deployment uses the new keyring.
7. Review provider logs/audit logs for suspicious authentication activity around the exposure window. Do not export tokens or passwords into issue trackers.
8. Rotate any other credential only if a literal value is confirmed by the full-history scan or provider inventory. Rotate database credentials, OAuth/client secrets, webhook signing keys and API keys independently; do not infer they were exposed merely from variable names.
9. Consider Git history rewriting only as a separately approved repository-maintenance action. Rotation is mandatory even if history is rewritten; do not rewrite history as part of this security PR.
10. Record rotation date, affected service, operator and completion evidence without recording secret values.

## Scanner interpretation

The earlier ad-hoc keyword scan produced false positives for ordinary variable names, Pydantic schema fields, OpenAPI JSON, docs and API contract strings. A keyword match is not a secret finding. The maintained scanner uses Gitleaks defaults plus assignment-shaped, high-entropy literal patterns and private-key/JWT-specific patterns. Every hit still requires human classification.


## Automated full-history scan observation (2026-11-01)

A one-time Gitleaks CLI scan ran against the branch's complete Git history and reported **2 matches across 322 commits**. The job's JSON report was written to the ephemeral runner filesystem and was not uploaded or summarized with path/commit/line metadata. The only independently confirmed credential exposure remains the historical JWT signing key listed above. The second match, and whether the two matches represent distinct values or repeated occurrences, is **UNVERIFIED**. Do not infer an additional credential type from the count.

The full-history scan will not be repeated under the no-rescan rule. Continuous CI now scans new changes/diffs only. The scan result is a release blocker until the finding metadata is available through an already-retained report or a separately authorized targeted investigation. The historical JWT key remains compromised regardless of whether it was deployed.
