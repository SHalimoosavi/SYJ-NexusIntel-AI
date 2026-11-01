import socket

import pytest

from app.core.safe_http import assert_public_domain, safe_get


def _addr(ip):
    return (socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443))


def test_private_dns_answer_is_rejected(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: [_addr("127.0.0.1")])
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


def test_https_connection_is_pinned_to_validated_ip_and_host(monkeypatch):
    import app.core.safe_http as safe_http

    created = []

    class FakeResponse:
        status = 200
        headers = {}
        data = b"public page"

        def read(self, amount, decode_content=True):
            return self.data[:amount]

        def read(self, amount, decode_content=True):
            return self.data[:amount]

        def release_conn(self):
            pass

    class FakePool:
        def __init__(self, host, **kwargs):
            created.append((host, kwargs))

        def request(self, *_args, **_kwargs):
            return FakeResponse()

        def close(self):
            pass

    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: [_addr("93.184.216.34")])
    monkeypatch.setattr(safe_http, "HTTPSConnectionPool", FakePool)

    response = safe_get("public-example.com")
    assert response.text == "public page"
    assert created[0][0] == "93.184.216.34"
    assert created[0][1]["server_hostname"] == "public-example.com"
    assert created[0][1]["assert_hostname"] == "public-example.com"
    response.close()


def test_redirect_to_metadata_or_private_ip_is_rejected(monkeypatch):
    import app.core.safe_http as safe_http

    calls = []

    class RedirectResponse:
        status = 302
        headers = {"Location": "http://169.254.169.254/latest/meta-data"}
        data = b""

        def release_conn(self):
            pass

    class FakePool:
        def __init__(self, host, **kwargs):
            calls.append(host)

        def request(self, *_args, **_kwargs):
            return RedirectResponse()

        def close(self):
            pass

    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: [_addr("93.184.216.34")])
    monkeypatch.setattr(safe_http, "HTTPSConnectionPool", FakePool)

    with pytest.raises(ValueError):
        safe_get("public-example.com")
    assert calls == ["93.184.216.34"]


def test_dns_rebinding_after_initial_resolution_cannot_change_pinned_destination(monkeypatch):
    import app.core.safe_http as safe_http

    answers = iter([
        [_addr("93.184.216.34")],
        [_addr("93.184.216.34")],
    ])
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: next(answers))
    created = []

    class FakeResponse:
        status = 200
        headers = {}
        data = b"ok"

        def release_conn(self):
            pass

    class FakePool:
        def __init__(self, host, **kwargs):
            created.append(host)

        def request(self, *_args, **_kwargs):
            return FakeResponse()

        def close(self):
            pass

    monkeypatch.setattr(safe_http, "HTTPSConnectionPool", FakePool)
    response = safe_get("public-example.com")
    assert created == ["93.184.216.34"]
    response.close()


def test_outbound_response_size_is_bounded(monkeypatch):
    import app.core.safe_http as safe_http

    class OversizedResponse:
        status = 200
        headers = {}
        data = b""

        def read(self, amount, decode_content=True):
            return b"x" * amount

        def close(self):
            pass

        def release_conn(self):
            pass

    class FakePool:
        def __init__(self, _host, **_kwargs):
            pass

        def request(self, *_args, **_kwargs):
            return OversizedResponse()

        def close(self):
            pass

    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: [_addr("93.184.216.34")])
    monkeypatch.setattr(safe_http, "HTTPSConnectionPool", FakePool)
    with pytest.raises(ValueError, match="response exceeded"):
        safe_http.safe_get("public-example.com", max_response_bytes=32)
