import pytest

from app.core.client_ip import resolve_client_ip


def test_untrusted_peer_cannot_spoof_forwarded_for():
    assert resolve_client_ip(
        "198.51.100.10",
        "203.0.113.77",
        ["172.30.0.2"],
    ) == "198.51.100.10"


def test_trusted_proxy_uses_rightmost_untrusted_hop():
    assert resolve_client_ip(
        "172.30.0.2",
        "198.51.100.25, 172.30.0.3",
        ["172.30.0.0/24"],
    ) == "198.51.100.25"


def test_ipv6_client_and_proxy_are_supported():
    assert resolve_client_ip(
        "2001:db8:ffff::1",
        "2001:db8::42",
        ["2001:db8:ffff::/48"],
    ) == "2001:db8::42"


@pytest.mark.parametrize(
    "header",
    [
        "",
        "not-an-ip",
        "203.0.113.1, garbage",
        "203.0.113.1:443",
        "203.0.113.1,",
    ],
)
def test_malformed_forwarded_for_is_ignored(header):
    assert resolve_client_ip(
        "172.30.0.2",
        header,
        ["172.30.0.2"],
    ) == "172.30.0.2"


def test_trusted_proxy_default_is_empty(monkeypatch):
    monkeypatch.delenv("TRUSTED_PROXIES", raising=False)
    assert resolve_client_ip("172.30.0.2", "203.0.113.9") == "172.30.0.2"
