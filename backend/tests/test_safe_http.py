import socket

import pytest

from app.core.safe_http import assert_public_domain, safe_get


def _addr(ip):
    return (socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443))


def test_private_dns_answer_is_rejected(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [_addr("127.0.0.1")],
    )
    with pytest.raises(ValueError, match="non-public"):
        assert_public_domain("public-example.com")


def test_mixed_public_and_private_dns_answers_are_rejected(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [_addr("93.184.216.34"), _addr("10.0.0.8")],
    )
    with pytest.raises(ValueError, match="non-public"):
        assert_public_domain("public-example.com")


def test_redirect_to_metadata_or_private_ip_is_rejected(monkeypatch):
    calls = []

    class Redirect:
        is_redirect = True
        is_permanent_redirect = False
        headers = {"Location": "http://169.254.169.254/latest/meta-data"}

        def close(self):
            pass

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [_addr("93.184.216.34")],
    )

    def fake_get(*_args, **_kwargs):
        calls.append(True)
        return Redirect()

    import app.core.safe_http as safe_http
    monkeypatch.setattr(safe_http.requests, "get", fake_get)

    with pytest.raises(ValueError):
        safe_get("public-example.com")
    assert len(calls) == 1
