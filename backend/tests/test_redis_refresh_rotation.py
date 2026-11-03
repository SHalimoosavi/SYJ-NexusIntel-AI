"""Redis-backed refresh rotation integration tests; CI supplies an isolated Redis service."""
from __future__ import annotations

import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
import redis

from app.core.rate_limit import RateLimitManager


@pytest.mark.integration
def test_redis_refresh_rotation_is_atomic_idempotent_and_detects_reuse() -> None:
    redis_url = os.getenv("REDIS_TEST_URL")
    if not redis_url:
        pytest.skip("REDIS_TEST_URL is not configured outside the CI integration job")

    client = redis.Redis.from_url(redis_url, decode_responses=True)
    client.ping()
    manager = RateLimitManager(redis_url=redis_url, app_env="production")
    jti = f"ci-refresh-{uuid.uuid4().hex}"
    keys = [
        manager._key(f"consumed-refresh:{jti}"),
        manager._key(f"refresh-inflight:{jti}"),
        manager._key(f"refresh-result:{jti}"),
    ]
    client.delete(*keys)
    barrier = Barrier(2)

    def claim() -> int:
        barrier.wait()
        return manager.begin_refresh_rotation(jti, ttl_seconds=30, grace_seconds=2)

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            claims = list(pool.map(lambda _index: claim(), range(2)))
        assert sorted(claims) == [1, 2]

        replacement = {
            "access_token": "integration-access",
            "refresh_token": "integration-refresh",
        }
        manager.complete_refresh_rotation(jti, replacement, grace_seconds=2)
        assert manager.begin_refresh_rotation(jti, ttl_seconds=30, grace_seconds=2) == 2
        assert manager.get_refresh_rotation_result(jti) == replacement

        time.sleep(2.2)
        assert manager.begin_refresh_rotation(jti, ttl_seconds=30, grace_seconds=2) == 0
    finally:
        client.delete(*keys)
