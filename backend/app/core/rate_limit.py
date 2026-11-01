"""Shared Redis rate limiting with a local-only in-memory fallback.

Production fails closed when Redis is missing/unavailable. Local/desktop/test
modes may use the process-local fallback; it is not suitable for replicas.
"""
import hashlib
import logging
import os
import time
import uuid
from collections import defaultdict, deque
from threading import Lock

logger = logging.getLogger("security.rate_limit")

_REDIS_WINDOW_SCRIPT = """
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', now - window)
local count = redis.call('ZCARD', KEYS[1])
if count >= limit then
  local oldest = redis.call('ZRANGE', KEYS[1], 0, 0, 'WITHSCORES')
  local retry = window
  if oldest[2] then retry = math.max(1, window - (now - tonumber(oldest[2]))) end
  return {0, math.ceil(retry)}
end
redis.call('ZADD', KEYS[1], now, ARGV[4])
redis.call('EXPIRE', KEYS[1], window + 1)
return {1, 0}
"""


class SlidingWindowLimiter:
    """Thread-safe fallback used only for local/desktop/test environments."""

    def __init__(self):
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                return False, max(1, int(window_seconds - (now - events[0])))
            events.append(now)
            return True, 0

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        return self.check(key, limit, window_seconds)[0]


class RateLimitBackendUnavailable(RuntimeError):
    pass


class RateLimitManager:
    def __init__(self, redis_url: str | None = None, app_env: str | None = None):
        self.redis_url = redis_url if redis_url is not None else os.getenv("REDIS_URL")
        self.app_env = (app_env or os.getenv("APP_ENV", "production")).lower()
        self.local_mode = self.app_env in {"development", "dev", "local", "test"}
        self._redis_client = None
        self._memory = SlidingWindowLimiter()
        self._memory_failures: dict[str, tuple[int, float]] = {}
        self._memory_lockouts: dict[str, float] = {}
        self._lock = Lock()

    def _redis(self):
        if not self.redis_url:
            if self.local_mode:
                return None
            raise RateLimitBackendUnavailable("Redis is required for production rate limiting")
        if self._redis_client is None:
            try:
                import redis

                self._redis_client = redis.Redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=1.5,
                    socket_timeout=1.5,
                    health_check_interval=30,
                )
                self._redis_client.ping()
            except Exception as exc:
                self._redis_client = None
                if self.local_mode:
                    logger.warning("rate_limit_backend_fallback mode=local")
                    return None
                raise RateLimitBackendUnavailable("Redis rate-limit backend unavailable") from exc
        return self._redis_client

    @staticmethod
    def _key(value: str) -> str:
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return f"syj:rl:{digest}"

    def check(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        client = self._redis()
        if client is None:
            return self._memory.check(key, limit, window_seconds)
        redis_key = self._key(key)
        try:
            result = client.eval(
                _REDIS_WINDOW_SCRIPT,
                1,
                redis_key,
                time.time(),
                window_seconds,
                limit,
                uuid.uuid4().hex,
            )
            return bool(int(result[0])), int(result[1])
        except Exception as exc:
            if self.local_mode:
                logger.warning("rate_limit_backend_fallback mode=local")
                return self._memory.check(key, limit, window_seconds)
            raise RateLimitBackendUnavailable("Redis rate-limit operation failed") from exc

    def is_login_locked(self, key: str) -> bool:
        client = self._redis()
        if client is None:
            with self._lock:
                until = self._memory_lockouts.get(key, 0.0)
                if until <= time.monotonic():
                    self._memory_lockouts.pop(key, None)
                    return False
                return True
        try:
            return bool(client.exists(self._key("lockout:" + key)))
        except Exception as exc:
            if self.local_mode:
                return self.is_login_locked_memory(key)
            raise RateLimitBackendUnavailable("Redis lockout lookup failed") from exc

    def is_login_locked_memory(self, key: str) -> bool:
        with self._lock:
            return self._memory_lockouts.get(key, 0.0) > time.monotonic()

    def record_login_failure(self, key: str, threshold: int = 5, lockout_seconds: int = 900) -> int:
        client = self._redis()
        if client is None:
            now = time.monotonic()
            with self._lock:
                count, expires = self._memory_failures.get(key, (0, now + lockout_seconds))
                if expires <= now:
                    count = 0
                count += 1
                self._memory_failures[key] = (count, now + lockout_seconds)
                if count >= threshold:
                    self._memory_lockouts[key] = now + lockout_seconds
                return count
        try:
            redis_key = self._key("failures:" + key)
            pipe = client.pipeline()
            pipe.incr(redis_key)
            pipe.ttl(redis_key)
            count, ttl = pipe.execute()
            if int(ttl) < 0:
                client.expire(redis_key, lockout_seconds)
            if int(count) >= threshold:
                client.setex(self._key("lockout:" + key), lockout_seconds, "1")
            return int(count)
        except Exception as exc:
            if self.local_mode:
                return self.record_login_failure_memory(key, threshold, lockout_seconds)
            raise RateLimitBackendUnavailable("Redis login failure tracking failed") from exc

    def record_login_failure_memory(self, key: str, threshold: int, lockout_seconds: int) -> int:
        now = time.monotonic()
        with self._lock:
            count, expires = self._memory_failures.get(key, (0, now + lockout_seconds))
            if expires <= now:
                count = 0
            count += 1
            self._memory_failures[key] = (count, now + lockout_seconds)
            if count >= threshold:
                self._memory_lockouts[key] = now + lockout_seconds
            return count

    def clear_login_failures(self, key: str) -> None:
        client = self._redis()
        if client is None:
            with self._lock:
                self._memory_failures.pop(key, None)
                self._memory_lockouts.pop(key, None)
            return
        try:
            client.delete(self._key("failures:" + key), self._key("lockout:" + key))
        except Exception as exc:
            if self.local_mode:
                with self._lock:
                    self._memory_failures.pop(key, None)
                    self._memory_lockouts.pop(key, None)
                return
            raise RateLimitBackendUnavailable("Redis login failure reset failed") from exc


def rate_limit_policy_for_path(path: str) -> tuple[int, int]:
    """Return (limit, window seconds); unmatched routes still receive a global IP limit."""
    normalized = path.rstrip("/") or "/"
    policies = {
        "/auth/login": (10, 900),
        "/auth/register": (3, 3600),
        "/auth/password-reset": (3, 3600),
        "/auth/refresh": (10, 60),
        "/invitations/accept": (5, 3600),
    }
    if normalized in policies:
        return policies[normalized]
    if normalized.startswith("/auth/"):
        return (20, 60)
    return (120, 60)


rate_limit_manager = RateLimitManager()
