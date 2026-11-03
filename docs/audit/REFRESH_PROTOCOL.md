# Redis Refresh-Token Rotation Protocol

**Status:** Retained; historical auth-sensitive implementation. No code change is made by this note.

## Scope and implementation

The protocol is implemented in `backend/app/core/rate_limit.py` and called by `backend/app/routers/auth.py` in the refresh route:

1. Validate the refresh token, user, active status and session version.
2. Call `begin_refresh_rotation(jti, ttl_seconds, grace_seconds=5)`.
3. The Redis Lua claim returns:
   - `1`: this request owns the rotation; create the replacement access/refresh pair.
   - `2`: another request already claimed it, or a completed result is still within the idempotency window; poll for and return the exact cached replacement pair.
   - `0`: replay after the grace window; revoke the user's session family and reject the refresh.
4. Before publishing the pair, the route rechecks the user session version so logout/password-change revocation cannot race into publishing a valid replacement.
5. The winner calls `complete_refresh_rotation`, which writes the serialized pair to the result key and deletes the in-flight key.
6. Duplicate callers retrieve the result with `get_refresh_rotation_result`. If it is not available after the bounded wait, return HTTP 503 with `Retry-After`; do not mint another pair.

## Claim script key and argument contract

The claim call uses `client.eval(_REFRESH_CLAIM_SCRIPT, 3, key1, key2, key3, ttl_seconds, grace_seconds)`.

| Lua value | Meaning |
|---|---|
| `KEYS[1]` | Hashed `consumed-refresh:<jti>` key. Durable one-time claim marker. |
| `KEYS[2]` | Hashed `refresh-inflight:<jti>` key. Short-lived marker that a winning request is still processing. |
| `KEYS[3]` | Hashed `refresh-result:<jti>` key. Short-lived serialized replacement token pair. |
| `ARGV[1]` | Refresh token TTL in seconds; defaults to 7 days via `REFRESH_TOKEN_EXPIRE_DAYS`. |
| `ARGV[2]` | In-flight/idempotency grace TTL in seconds; defaults to 5 seconds. |

The script checks whether `KEYS[1]` already exists. If it does, it returns 2 when either `KEYS[2]` or `KEYS[3]` exists, otherwise 0. If it does not exist, it sets `KEYS[1]` to `1` with `ARGV[1]` expiry, sets `KEYS[2]` to `1` with `ARGV[2]` expiry, then returns 1. These checks and writes are one atomic Redis Lua operation.

## Completion script key and argument contract

The completion call uses `client.eval(_REFRESH_COMPLETE_SCRIPT, 2, result_key, inflight_key, serialized_tokens, grace_seconds)`.

| Lua value | Meaning |
|---|---|
| `KEYS[1]` | The same hashed `refresh-result:<jti>` key used as `KEYS[3]` by the claim script. |
| `KEYS[2]` | The same hashed `refresh-inflight:<jti>` key used as `KEYS[2]` by the claim script. |
| `ARGV[1]` | Compact JSON containing `access_token` and `refresh_token`. |
| `ARGV[2]` | Result-cache TTL in seconds; defaults to 5 seconds. |

The completion script writes `KEYS[1]` with the serialized token pair and expiry `ARGV[2]`, deletes `KEYS[2]`, and returns 1. The consumed-JTI marker remains until its refresh-token TTL expires.

## Crash between claim and completion

If the winning worker crashes after the claim and before completion:

- The consumed-JTI marker remains for the refresh-token TTL (default 7 days).
- The in-flight marker remains for the 5-second grace period.
- A duplicate during that grace receives claim result 2, but there is no result key to retrieve. The route polls for up to 1 second and then returns HTTP 503 with `Retry-After: 1`.
- After the in-flight marker expires, a later retry receives result 0 and is treated as token replay; the route revokes the session family and returns HTTP 401.

This is fail-closed. It can require the user to authenticate again after a worker crash; the implementation does not recover or recreate a missing replacement pair.

## Redis outage and local fallback

In production, `RateLimitManager._redis()` requires a configured Redis URL and successfully pings Redis. Missing/unreachable Redis raises `RateLimitBackendUnavailable`. The refresh route catches that exception and returns HTTP 503 with `Retry-After: 5`; it does not issue cookies or permit refresh. Failure during claim, completion or result lookup also raises the same backend-unavailable exception in production.

The route-level test `backend/tests/test_auth_sessions.py::test_refresh_fails_closed_when_session_backend_is_unavailable` injects that exception and asserts HTTP 503. The code path is fail-closed. A live network/socket outage integration test against Redis is not currently present, so the exact end-to-end socket failure simulation remains **UNVERIFIED**.

In local/development/desktop/test modes, the manager may fall back to in-memory dictionaries protected by a Python lock. That state is per process. It coordinates threads within one worker, but **does not coordinate multiple backend worker processes**. Multi-worker local mode is therefore not safe for refresh-token single-use guarantees. Production mode does not use this fallback.

## Replay-window security and persistence implications

The idempotency/replay-result window is **5 seconds** by default (`grace_seconds=5`). During this bounded window, any party holding the same stolen refresh token can receive the exact same replacement access/refresh pair as the legitimate client. This is an inherent residual risk of returning an idempotent result to concurrent retries; the result key expires after the configured grace TTL. The design avoids minting two different replacement pairs, but it does not distinguish the legitimate client from another holder of the bearer token during that window.

The consumed-claim key has the refresh-token lifetime (default **7 days**, controlled by `REFRESH_TOKEN_EXPIRE_DAYS`). The in-flight marker and serialized result key each use the **5-second** grace TTL by default. The result key stores the serialized access and refresh JWTs in Redis while it exists. Its TTL bounds live Redis key visibility; it does not guarantee the token bytes never reach persistence files.

### Docker Compose Redis persistence note — Phase 3

The current `docker-compose.yml` starts Redis with `--appendonly yes --save 60 1000` and mounts the named `redis_data` volume at `/data`. Therefore AOF is enabled and RDB snapshots are configured (snapshot after 60 seconds when at least 1,000 key changes occur). A refresh-result value that exists during an AOF write or an RDB snapshot can be written to disk. Redis expiration metadata is persisted too, but expiry does not retroactively erase older AOF/RDB contents or backups. Treat Redis persistence files, volume backups and host access as sensitive authentication material. This is a Phase 3 design consideration only: persistence settings and Compose configuration are not changed in this test-only phase.

## Live Redis outage characterization coverage

The following tests are characterization of the current implementation, not claims that a behavior fix was introduced. They use the real Redis CI service and production-mode `RateLimitManager` instances; the outage cases isolate the client endpoint or pause Redis to exercise real socket behavior.

| Case | Test (file::test name) | Coverage |
|---|---|---|
| a — Redis unreachable before refresh | `backend/tests/test_redis_refresh_outages.py::test_refresh_rejects_when_redis_endpoint_is_unreachable_without_consuming_token` | Exact 503 response, no replacement cookies, no consumed claim or session revocation; same token can refresh after Redis endpoint is restored. |
| b — Redis endpoint lost after claim | `backend/tests/test_redis_refresh_outages.py::test_refresh_fails_closed_when_redis_endpoint_is_lost_after_claim` | Claim remains consumed; completion returns 503 without cookies; after the 5-second in-flight TTL expires, old-token retry is rejected and session-family revocation is asserted. |
| c — Redis paused / socket timeout | `backend/tests/test_redis_refresh_outages.py::test_refresh_is_bounded_by_redis_socket_timeout_when_service_is_paused` | Real Redis `CLIENT PAUSE`; request is bounded by the configured 1.5-second socket timeout and returns 503. |
| d — Redis recovery and expiry | `backend/tests/test_redis_refresh_outages.py::test_refresh_recovers_and_result_key_expires` | Refresh succeeds after Redis is available; claim/result TTLs are inspected and the result is not served after expiry. |
| e — production fallback disabled | `backend/tests/test_redis_refresh_outages.py::test_production_mode_never_uses_in_memory_fallback` | Production mode raises backend-unavailable without populating in-memory limiter/claim state; explicit local mode can use fallback. |
| f — ten-way concurrency | `backend/tests/test_redis_refresh_outages.py::test_ten_parallel_refreshes_create_one_idempotent_rotation` | Ten barrier-released requests; identical successful cookie pairs, one Redis claim/result rotation, no 5xx, post-window replay rejection and family-revocation result. |

**Coverage run URL:** pending the first finished CI run containing these characterization tests. No run is represented as complete until GitHub Actions reports completion.

## Redis Cluster constraint

A Redis Lua script that accesses multiple keys requires every key to map to the same Redis Cluster hash slot. The current keys are independently SHA-256-derived and do not share a Redis hash tag, so they are not guaranteed to occupy one slot. This is compatible with the planned single Redis node in Docker Compose. It is **not Redis Cluster-ready**; any future cluster deployment must introduce a deliberate shared hash-tag/key-slot scheme and test it before use.

## History and tests

- Original script introduction: [`cd8a21f1c18c0b89ff271ea47005b5e9787839d9`](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/commit/cd8a21f1c18c0b89ff271ea47005b5e9787839d9). Its parent `4f457e170256790cc51676e86eead73a21098054` lacks both scripts and the claim method.
- Later idempotency-result-key correction: `42f4219f4267ec393f94327972c0f3264710a030`.
- Correct three-key Lua invocation: [the key-count correction commit](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/commit/4bec95dca2719bb842b66d9d7658de33e10d9579).
- In-memory concurrency/idempotency: `backend/tests/test_rate_limit.py::test_refresh_rotation_claim_is_atomic_and_duplicate_is_idempotent`.
- Auth behavior: `backend/tests/test_auth_sessions.py::test_refresh_rotation_rejects_reuse_and_revokes_session_family`; `::test_refresh_fails_closed_when_session_backend_is_unavailable`; `::test_refresh_missing_cached_result_fails_closed`.
- Real Redis concurrency/idempotency/replay: `backend/tests/test_redis_refresh_rotation.py::test_redis_refresh_rotation_is_atomic_idempotent_and_detects_reuse`, using an isolated Redis CI service.
- Finished CI evidence: [Security Tests run 41561425429](https://github.com/SHalimoosavi/SYJ-NexusIntel-AI/actions/runs/41561425429), `backend-security-tests` and `frontend-checks` both passed; backend suite 123 passed, 0 failed, 0 skipped, 241 warnings. The integration test file was present at the run head.
- Historical convention: **convention not followed: historical**. This implementation predates the AUTH-SENSITIVE prefix/test-first convention. History was not rewritten.
