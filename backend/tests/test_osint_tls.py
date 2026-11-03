from __future__ import annotations

from typing import Any

from app.services.osint_service import _read_tls_certificate


class FakePeer:
    def __init__(self, certificate: object) -> None:
        self.certificate = certificate

    def getpeercert(self, binary_form: bool = False) -> object:
        assert binary_form is False
        return self.certificate


def test_none_certificate_fails_closed() -> None:
    assert _read_tls_certificate(FakePeer(None)) is None


def test_empty_certificate_fails_closed() -> None:
    assert _read_tls_certificate(FakePeer({})) is None


def test_valid_certificate_is_typed_and_not_expired() -> None:
    cert: dict[str, Any] = {
        "notAfter": "Dec 31 23:59:59 2099 GMT",
        "subjectAltName": (("DNS", "example.com"),),
        "issuer": ((("commonName", "Example CA"),),),
    }
    result = _read_tls_certificate(FakePeer(cert))
    assert result is not None
    assert result.not_after == cert["notAfter"]
    assert result.subject_alt_names == (("DNS", "example.com"),)
    assert result.expired is False


def test_expired_certificate_is_marked_expired() -> None:
    cert = {"notAfter": "Jan  1 00:00:00 2000 GMT", "subjectAltName": ()}
    result = _read_tls_certificate(FakePeer(cert))
    assert result is not None
    assert result.expired is True


def test_malformed_not_after_is_rejected() -> None:
    assert _read_tls_certificate(FakePeer({"notAfter": "not-a-date"})) is None


def test_subject_alt_name_preserves_multiple_entries() -> None:
    cert = {
        "notAfter": "Dec 31 23:59:59 2099 GMT",
        "subjectAltName": (("DNS", "example.com"), ("IP Address", "192.0.2.1")),
    }
    result = _read_tls_certificate(FakePeer(cert))
    assert result is not None
    assert result.subject_alt_names == (
        ("DNS", "example.com"),
        ("IP Address", "192.0.2.1"),
    )


def test_missing_not_after_is_rejected() -> None:
    assert _read_tls_certificate(FakePeer({"subjectAltName": ()})) is None


def test_missing_subject_alt_name_is_an_empty_tuple() -> None:
    result = _read_tls_certificate(FakePeer({"notAfter": "Dec 31 23:59:59 2099 GMT"}))
    assert result is not None
    assert result.subject_alt_names == ()


def test_wrong_certificate_value_types_are_rejected() -> None:
    assert _read_tls_certificate(FakePeer({"notAfter": 123, "subjectAltName": ()})) is None
    assert _read_tls_certificate(
        FakePeer({"notAfter": "Dec 31 23:59:59 2099 GMT", "subjectAltName": ["DNS", "x"]})
    ) is None
    assert _read_tls_certificate(
        FakePeer({"notAfter": "Dec 31 23:59:59 2099 GMT", "subjectAltName": (("DNS", 7),)})
    ) is None
