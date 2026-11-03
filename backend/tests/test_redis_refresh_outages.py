"""Live Redis outage and refresh-rotation characterization tests.

These tests characterize existing behavior; they do not claim to implement a fix.
The CI job supplies an isolated Redis 7.4 service through REDIS_TEST_URL.
"""
from __future__ import annotations

import json
import os
import socket
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
import redis
from fastapi import HTTPException, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from starlette.requests import Request

from app.core.rate_limit import RateLimitBackendUnavailable, RateLimitManager
from app.core.security import create_refresh_token, hash_password, verify_token
from app.database.database import Base
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
import app.routers.auth as auth_router


@pytest.fixture
def redis_url() -> str:
    value = os.getenv("REDIS_TEST_URL")
    if not value:
        pytest.skip("REDIS_TEST_URL is not configured")
    client = redis.Redis.from_url(value, decode_responses=True)
    client.ping()
    return value


@pytest.fixture
def auth_world(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'refresh-outage.sqlite3'}",
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    db = factory()
    organization = Organization(name="Redis Test Tenant", slug=f"redis-{uuid.uuid4().hex}")
    role = Role(name=f"REDIS_TEST_{uuid.uuid4().hex[:8]}")
    db.add_all([organization, role])
    db.commit()
    db.refresh(organization)
    db.refresh(role)
    user = User(
        full_name="Redis Integration User",
        email=f"redis-{uuid.uuid4().hex}@example.com",
        hashed_password=hash_password("IntegrationPassword123!"),
        organization_id=organization.id,
        role_id=role.id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    data = {"factory": factory, "user_id": user.id, "email": user.email, "engine": engine}
    db.close()
    yield data
    engine.dispose()


def _closed_port() -> str:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return f"redis://127.0.0.1:{port}/15"


def _request(token: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "http",
            "path": "/auth/refresh",
            "query_string": b"",
            "headers": [
                (b"origin", b"http://localhost:3000"),
                (b"cookie", f"refresh_token={token}".encode("ascii")),
            ],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
        }
    )


def _invoke(token: str, factory):
    db = factory()
    response = Response()
    try:
        result = auth_router.refresh_session(_request(token), response, db)
        return 200, result, response
    except HTTPException as exc:
        return exc.status_code, {"detail": exc.detail}, response
    finally:
        db.close()


def _cookie_pair(response: Response) -> tuple[bytes, bytes]:
    cookies = {}
    for name, value in response.raw_headers:
        if name.lower() == b"set-cookie":
            cookie = value.split(b";", 1)[0]
            key, raw = cookie.split(b"=", 1)
            if key in {b"access_token", b"refresh_token"}:
                cookies[key] = raw
    assert set(cookies) == {b"access_token", b"refresh_token"}
    return cookies[b"access_token"], cookies[b"refresh_token"]


def _wait_until(predicate, timeout: float, description: str) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.01)
    pytest.fail(f"Timed out waiting for {description}")


def _keys(manager: RateLimitManager, jti: str) -> tuple[str, str, str]:
    return (
        manager._key("consumed-refresh:" + jti),
        manager._key("refresh-inflight:" + jti),
        manager._key("refresh-result:" + jti),
    )


def _new_token(world) -> str:
    return create_refresh_token(
        {"sub": world["email"], "user_id": world["user_id"], "session_version": 0}
    )


def test_refresh_rejects_when_redis_endpoint_is_unreachable_without_consuming_token(
    monkeypatch, redis_url, auth_world
):
    token = _new_token(auth_world)
    payload = verify_token(token)
    assert payload is not None
    jti = payload["jti"]
    unavailable = RateLimitManager(redis_url=_closed_port(), app_env="production")
    monkeypatch.setattr(auth_router, "rate_limit_manager", unavailable)

    status, body, response = _invoke(token, auth_world["factory"])

    assert status == 503
    assert body == {"detail": "Session service temporarily unavailable"}
    assert not any(name.lower() == b"set-cookie" for name, _ in response.raw_headers)
    assert unavailable._memory_consumed_jti == {}
    assert unavailable._memory_user_versions == {}

    live_client = redis.Redis.from_url(redis_url, decode_responses=True)
    live_manager = RateLimitManager(redis_url=redis_url, app_env="production")
    consumed, inflight, result = _keys(live_manager, jti)
    assert live_client.exists(consumed, inflight, result) == 0
    assert live_manager.get_user_session_version(auth_world["user_id"]) == 0

    monkeypatch.setattr(auth_router, "rate_limit_manager", live_manager)
    recovered_status, _recovered_body, recovered_response = _invoke(
        token, auth_world["factory"]
    )
    assert recovered_status == 200
    _cookie_pair(recovered_response)
    assert live_manager.get_user_session_version(auth_world["user_id"]) == 0


def test_refresh_fails_closed_when_redis_endpoint_is_lost_after_claim(
    monkeypatch, redis_url, auth_world
):
    token = _new_token(auth_world)
    payload = verify_token(token)
    assert payload is not None
    jti = payload["jti"]
    client = redis.Redis.from_url(redis_url, decode_responses=True)
    manager = RateLimitManager(redis_url=redis_url, app_env="production")
    consumed, inflight, result = _keys(manager, jti)
    client.delete(consumed, inflight, result)
    original_complete = manager.complete_refresh_rotation

    def lose_endpoint_after_claim(claimed_jti, tokens, grace_seconds=5):
        manager.redis_url = _closed_port()
        manager._redis_client = None
        return original_complete(claimed_jti, tokens, grace_seconds)

    monkeypatch.setattr(manager, "complete_refresh_rotation", lose_endpoint_after_claim)
    monkeypatch.setattr(auth_router, "rate_limit_manager", manager)

    status, body, response = _invoke(token, auth_world["factory"])

    assert status == 503
    assert body == {"detail": "Session service temporarily unavailable"}
    assert not any(name.lower() == b"set-cookie" for name, _ in response.raw_headers)

    manager.redis_url = redis_url
    manager._redis_client = None
    assert client.exists(consumed) == 1
    assert client.exists(inflight) == 1
    assert client.exists(result) == 0
    assert 0 < client.ttl(consumed) <= 7 * 24 * 60 * 60
    assert 0 < client.ttl(inflight) <= 5

    _wait_until(lambda: client.exists(inflight) == 0, 7.0, "in-flight claim TTL expiry")
    retry_status, retry_body, retry_response = _invoke(token, auth_world["factory"])
    assert retry_status == 401
    assert retry_body == {"detail": "Refresh session reuse detected"}
    assert not any(name.lower() == b"set-cookie" for name, _ in retry_response.raw_headers)
    assert manager.get_user_session_version(auth_world["user_id"]) == 1
    assert client.exists(consumed) == 1
    assert client.exists(result) == 0


def test_refresh_is_bounded_by_redis_socket_timeout_when_service_is_paused(
    monkeypatch, redis_url, auth_world
):
    token = _new_token(auth_world)
    manager = RateLimitManager(redis_url=redis_url, app_env="production")
    manager.get_user_session_version(auth_world["user_id"])
    assert manager._redis_client is not None
    connection_options = manager._redis_client.connection_pool.connection_kwargs
    assert connection_options["socket_connect_timeout"] == 1.5
    assert connection_options["socket_timeout"] == 1.5

    control = redis.Redis.from_url(redis_url, decode_responses=True)
    control.execute_command("CLIENT", "PAUSE", 2500, "ALL")
    monkeypatch.setattr(auth_router, "rate_limit_manager", manager)
    started = time.monotonic()
    try:
        status, body, response = _invoke(token, auth_world["factory"])
    finally:
        elapsed = time.monotonic() - started

    assert status == 503
    assert body == {"detail": "Session service temporarily unavailable"}
    assert elapsed < 2.5
    assert elapsed >= 1.2
    assert not any(name.lower() == b"set-cookie" for name, _ in response.raw_headers)
    _wait_until(lambda: _redis_ping(control), 4.0, "Redis to resume after CLIENT PAUSE")


def _redis_ping(client: redis.Redis) -> bool:
    try:
        return bool(client.ping())
    except redis.RedisError:
        return False


def test_refresh_recovers_and_result_key_expires(monkeypatch, redis_url, auth_world):
    token = _new_token(auth_world)
    payload = verify_token(token)
    assert payload is not None
    jti = payload["jti"]
    client = redis.Redis.from_url(redis_url, decode_responses=True)
    manager = RateLimitManager(redis_url=redis_url, app_env="production")
    consumed, inflight, result = _keys(manager, jti)
    client.delete(consumed, inflight, result)
    monkeypatch.setattr(auth_router, "rate_limit_manager", manager)

    status, _body, response = _invoke(token, auth_world["factory"])
    assert status == 200
    access_token, refresh_token = _cookie_pair(response)

    assert client.exists(consumed) == 1
    assert client.exists(inflight) == 0
    assert client.exists(result) == 1
    claim_ttl = client.ttl(consumed)
    result_ttl = client.ttl(result)
    assert 0 < claim_ttl <= 7 * 24 * 60 * 60
    assert 0 < result_ttl <= 5

    result_value = json.loads(client.get(result))
    assert result_value == {
        "access_token": access_token.decode("ascii"),
        "refresh_token": refresh_token.decode("ascii"),
    }
    key_names = [key for key in client.keys("syj:rl:*") if jti.encode() in key.encode()]
    assert key_names == []
    for key in client.keys("syj:rl:*refresh*"):
        assert token.encode("ascii") not in key.encode("ascii")
        assert access_token not in key.encode("ascii")
        assert refresh_token not in key.encode("ascii")

    _wait_until(lambda: client.exists(result) == 0, 7.0, "refresh-result TTL expiry")
    assert manager.get_refresh_rotation_result(jti) is None
    assert client.exists(consumed) == 1


def test_production_mode_never_uses_in_memory_fallback():
    production = RateLimitManager(redis_url=_closed_port(), app_env="production")
    with pytest.raises(RateLimitBackendUnavailable):
        production.check("production-outage", 10, 60)
    with pytest.raises(RateLimitBackendUnavailable):
        production.begin_refresh_rotation("production-outage-jti", 60)
    assert production._memory._events == {}
    assert production._memory_consumed_jti == {}
    assert production._memory_refresh_inflight == {}
    assert production._memory_refresh_results == {}

    local = RateLimitManager(redis_url="", app_env="local")
    allowed, retry_after = local.check("explicit-local", 10, 60)
    assert allowed is True
    assert retry_after == 0
    assert local.begin_refresh_rotation("explicit-local-jti", 60) == 1
    assert "explicit-local" in local._memory._events
    assert "explicit-local-jti" in local._memory_consumed_jti


def test_ten_parallel_refreshes_create_one_idempotent_rotation(
    monkeypatch, redis_url, auth_world
):
    count = 10
    token = _new_token(auth_world)
    payload = verify_token(token)
    assert payload is not None
    jti = payload["jti"]
    client = redis.Redis.from_url(redis_url, decode_responses=True)
    manager = RateLimitManager(redis_url=redis_url, app_env="production")
    consumed, inflight, result = _keys(manager, jti)
    client.delete(consumed, inflight, result)
    monkeypatch.setattr(auth_router, "rate_limit_manager", manager)
    barrier = Barrier(count)

    def refresh_together(_index):
        barrier.wait(timeout=5)
        return _invoke(token, auth_world["factory"])

    with ThreadPoolExecutor(max_workers=count) as pool:
        responses = list(pool.map(refresh_together, range(count)))

    statuses = [status for status, _body, _response in responses]
    assert all(status == 200 for status in statuses), statuses
    pairs = [_cookie_pair(response) for _status, _body, response in responses]
    assert len(set(pairs)) == 1, "Concurrent refreshes produced more than one token pair"

    # JWTs are stateless; this application has no per-token database record.
    # Redis is the authoritative one-time claim and short-lived replacement record.
    assert client.exists(consumed) == 1
    assert client.exists(inflight) == 0
    assert client.exists(result) == 1
    assert client.ttl(consumed) > 0
    assert 0 < client.ttl(result) <= 5
    stored = json.loads(client.get(result))
    assert stored == {
        "access_token": pairs[0][0].decode("ascii"),
        "refresh_token": pairs[0][1].decode("ascii"),
    }

    refresh_keys = [key for key in client.keys("syj:rl:*refresh*") if manager._key("consumed-refresh:" + jti)[:-64].encode() in key.encode()]
    assert len(refresh_keys) == 2
    for key in refresh_keys:
        assert token.encode("ascii") not in key.encode("ascii")
        assert pairs[0][0] not in key.encode("ascii")
        assert pairs[0][1] not in key.encode("ascii")

    _wait_until(lambda: client.exists(result) == 0, 7.0, "concurrent refresh result TTL expiry")
    assert manager.get_refresh_rotation_result(jti) is None
    replay_status, replay_body, replay_response = _invoke(token, auth_world["factory"])
    assert replay_status == 401
    assert replay_body == {"detail": "Refresh session reuse detected"}
    assert not any(name.lower() == b"set-cookie" for name, _ in replay_response.raw_headers)
    assert manager.get_user_session_version(auth_world["user_id"]) == 1
    assert client.exists(consumed) == 1
