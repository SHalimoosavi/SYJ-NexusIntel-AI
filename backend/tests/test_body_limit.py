import asyncio

from app.core.body_limit import RequestBodyLimitMiddleware


def _run(app, scope, messages):
    output = []
    queue = list(messages)

    async def receive():
        return queue.pop(0)

    async def send(message):
        output.append(message)

    asyncio.run(app(scope, receive, send))
    return output


def _scope(headers=None):
    return {
        "type": "http",
        "method": "POST",
        "path": "/test",
        "headers": headers or [],
    }


def test_declared_oversized_body_is_rejected_before_route_execution():
    called = []

    async def app(scope, receive, send):
        called.append(True)

    middleware = RequestBodyLimitMiddleware(app, max_body_bytes=8)
    result = _run(
        middleware,
        _scope([(b"content-length", b"9")]),
        [],
    )
    assert not called
    assert result[0]["status"] == 413


def test_chunked_body_is_counted_and_rejected_when_limit_exceeded():
    async def app(scope, receive, send):
        while True:
            message = await receive()
            if not message.get("more_body"):
                break
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    middleware = RequestBodyLimitMiddleware(app, max_body_bytes=8)
    result = _run(
        middleware,
        _scope(),
        [
            {"type": "http.request", "body": b"12345", "more_body": True},
            {"type": "http.request", "body": b"67890", "more_body": False},
        ],
    )
    assert result[0]["status"] == 413


def test_body_at_limit_is_allowed():
    async def app(scope, receive, send):
        message = await receive()
        assert message["body"] == b"12345678"
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    middleware = RequestBodyLimitMiddleware(app, max_body_bytes=8)
    result = _run(
        middleware,
        _scope([(b"content-length", b"8")]),
        [{"type": "http.request", "body": b"12345678", "more_body": False}],
    )
    assert result[0]["status"] == 200
