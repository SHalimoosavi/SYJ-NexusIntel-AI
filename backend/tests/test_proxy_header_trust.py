import asyncio

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware


def _scope(peer_ip: str, forwarded_ip: str):
    return {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/health",
        "raw_path": b"/health",
        "query_string": b"",
        "root_path": "",
        "headers": [(b"x-forwarded-for", forwarded_ip.encode("ascii"))],
        "client": (peer_ip, 12345),
        "server": ("api", 8000),
    }


def _run(middleware, scope):
    seen = []

    async def app(inner_scope, receive, send):
        seen.append(inner_scope["client"])

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(_message):
        pass

    asyncio.run(middleware(app)(_scope(*scope), receive, send))
    return seen[0]


def test_untrusted_peer_cannot_spoof_client_ip_with_forwarded_header():
    client = _run(
        ProxyHeadersMiddleware,
        ("198.51.100.10", "203.0.113.77"),
    )
    assert client[0] == "198.51.100.10"


def test_explicitly_trusted_proxy_can_supply_overwritten_client_ip():
    client = _run(
        ProxyHeadersMiddleware,
        ("127.0.0.1", "203.0.113.77"),
    )
    assert client[0] == "203.0.113.77"
