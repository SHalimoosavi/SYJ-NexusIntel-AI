"""ASGI integration coverage for trusted client-IP rate-limit bucket selection."""
from __future__ import annotations

import asyncio

from starlette.requests import Request
from starlette.responses import Response

import app.main as main


class RecordingRateLimiter:
    def __init__(self) -> None:
        self.keys: list[str] = []

    def check(self, key: str, _limit: int, _window: int) -> tuple[bool, int]:
        self.keys.append(key)
        return True, 0


def _request(peer: str, forwarded_for: str) -> Request:
    return Request({
        "type": "http",
        "method": "GET",
        "scheme": "http",
        "path": "/health",
        "query_string": b"",
        "headers": [(b"x-forwarded-for", forwarded_for.encode("ascii"))],
        "client": (peer, 12345),
        "server": ("testserver", 80),
    })


def test_rate_limit_middleware_uses_resolved_ip_for_trusted_and_untrusted_peers(monkeypatch) -> None:
    limiter = RecordingRateLimiter()
    monkeypatch.setattr(main, "rate_limit_manager", limiter)
    monkeypatch.setattr(main, "TRUSTED_PROXIES", ["172.30.0.0/24"])

    async def call_next(_request: Request) -> Response:
        return Response(status_code=200)

    trusted_response = asyncio.run(
        main.apply_route_rate_limits(
            _request("172.30.0.2", "198.51.100.25, 172.30.0.3"),
            call_next,
        )
    )
    assert trusted_response.status_code == 200
    assert any(key.startswith("ip:198.51.100.25:") for key in limiter.keys)

    limiter.keys.clear()
    untrusted_response = asyncio.run(
        main.apply_route_rate_limits(
            _request("198.51.100.10", "203.0.113.77"),
            call_next,
        )
    )
    assert untrusted_response.status_code == 200
    assert any(key.startswith("ip:198.51.100.10:") for key in limiter.keys)
    assert not any("203.0.113.77" in key for key in limiter.keys)
