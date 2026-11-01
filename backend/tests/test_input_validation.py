import pytest

from app.core.input_validation import validate_domain


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("example.com", "example.com"),
        (" EXAMPLE.COM. ", "example.com"),
        ("bücher.de", "xn--bcher-kva.de"),
    ],
)
def test_valid_public_hostname(value, expected):
    assert validate_domain(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "localhost",
        "service.local",
        "metadata.google.internal",
        "127.0.0.1",
        "10.0.0.1",
        "[::1]",
        "https://example.com",
        "example.com/path",
        "example.com:443",
        "user@example.com",
    ],
)
def test_rejects_non_hostname_or_internal_targets(value):
    with pytest.raises(ValueError):
        validate_domain(value)


def test_public_domain_validator_rejects_private_dns_answers(monkeypatch):
    import socket

    from app.core.safe_http import assert_public_domain

    private_answer = (
        socket.AF_INET,
        socket.SOCK_STREAM,
        6,
        "",
        ("10.0.0.12", 443),
    )
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: [private_answer])
    with pytest.raises(ValueError, match="non-public"):
        assert_public_domain("public-company.com")


def test_safe_get_rejects_redirect_to_internal_target(monkeypatch):
    import app.core.safe_http as safe_http

    monkeypatch.setattr(
        safe_http,
        "resolve_public_addresses",
        lambda host: (host, ["93.184.216.34"]),
    )

    class RedirectResponse:
        status = 302
        headers = {"Location": "http://127.0.0.1/admin"}
        data = b""

        def read(self, amount, decode_content=True):
            return b""

        def release_conn(self):
            pass

    class FakePool:
        def __init__(self, host, **_kwargs):
            assert host == "93.184.216.34"

        def request(self, *_args, **_kwargs):
            return RedirectResponse()

        def close(self):
            pass

    monkeypatch.setattr(safe_http, "HTTPSConnectionPool", FakePool)
    with pytest.raises(ValueError):
        safe_http.safe_get("public-company.com")
