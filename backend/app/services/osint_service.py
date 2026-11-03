import socket
import ssl
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

import dns.resolver
from bs4 import BeautifulSoup
from bs4.element import Tag

from app.core.safe_http import assert_public_domain, resolve_public_addresses, safe_get


def get_whois(domain: str):
    try:
        from whois import whois
        host = assert_public_domain(domain)
        data = whois(host)
        return {
            "registrar": str(data.registrar),
            "creation_date": str(data.creation_date),
            "expiration_date": str(data.expiration_date),
        }
    except Exception:
        return {"error": "WHOIS lookup failed for the supplied public domain"}


def get_dns(domain: str):
    try:
        host = assert_public_domain(domain)
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
        answers = resolver.resolve(host, "A", lifetime=5)
        result = [record.to_text() for record in answers]
        for address in result:
            import ipaddress
            if not ipaddress.ip_address(address).is_global:
                raise ValueError("Non-public DNS answer rejected")
        return result
    except Exception:
        return {"error": "DNS lookup failed or returned a non-public address"}


def get_ip(domain: str):
    try:
        _host, addresses = resolve_public_addresses(domain)
        return addresses[0]
    except Exception:
        return None


class _PeerCertificateSource(Protocol):
    def getpeercert(self, binary_form: bool = False) -> object: ...


@dataclass(frozen=True)
class _TLSCertificateInfo:
    not_after: str
    expires_at: float
    subject_alt_names: tuple[tuple[str, str], ...]
    issuer: str | None
    expired: bool


def _read_tls_certificate(
    peer: _PeerCertificateSource,
) -> _TLSCertificateInfo | None:
    """Read and validate the decoded peer certificate without trusting stub unions."""
    try:
        certificate = peer.getpeercert(binary_form=False)
    except (OSError, ssl.SSLError, ValueError):
        return None

    if certificate is None or not isinstance(certificate, dict) or not certificate:
        return None

    not_after_value = certificate.get("notAfter")
    if not isinstance(not_after_value, str):
        return None
    try:
        expires_at = ssl.cert_time_to_seconds(not_after_value)
    except (OverflowError, TypeError, ValueError):
        return None

    san_value = certificate.get("subjectAltName", ())
    if not isinstance(san_value, tuple):
        return None
    subject_alt_names: list[tuple[str, str]] = []
    for entry in san_value:
        if (
            not isinstance(entry, tuple)
            or len(entry) != 2
            or not isinstance(entry[0], str)
            or not isinstance(entry[1], str)
        ):
            return None
        subject_alt_names.append((entry[0], entry[1]))

    issuer_value = certificate.get("issuer")
    issuer = repr(issuer_value) if isinstance(issuer_value, tuple) else None
    return _TLSCertificateInfo(
        not_after=not_after_value,
        expires_at=expires_at,
        subject_alt_names=tuple(subject_alt_names),
        issuer=issuer,
        expired=expires_at <= time.time(),
    )


def get_ssl_info(domain: str):
    try:
        host, addresses = resolve_public_addresses(domain)
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(), server_hostname=host) as sock:
            sock.settimeout(5)
            sock.connect((addresses[0], 443))
            certificate = _read_tls_certificate(sock)  # type: ignore[arg-type]  # Python 3.12.15 typeshed overload mismatch; helper calls binary_form=False and rejects None, empty/non-dict certs, and malformed typed fields.
        if certificate is None:
            return {"valid": False, "error": "TLS certificate missing or unusable"}
        if certificate.expired:
            return {"valid": False, "error": "TLS certificate is expired"}
        return {
            "valid": True,
            "issuer": certificate.issuer or "unknown",
            "not_after": certificate.not_after,
            "subject_alt_names": certificate.subject_alt_names,
        }
    except Exception:
        return {"valid": False, "error": "TLS inspection failed for public domain"}


def get_security_headers(domain: str):
    try:
        response = safe_get(domain, timeout=10)
        try:
            headers = response.headers
            return {
                "hsts": "Strict-Transport-Security" in headers,
                "csp": "Content-Security-Policy" in headers,
                "x_frame_options": "X-Frame-Options" in headers,
                "x_content_type_options": "X-Content-Type-Options" in headers,
            }
        finally:
            response.close()
    except Exception:
        return {"error": "Security header inspection failed for public domain"}


def _get_tag_attribute(tag: Tag | None, name: str) -> str | None:
    if tag is None:
        return None

    attributes = tag.attrs or {}
    if not isinstance(attributes, Mapping):
        return None

    value: object = attributes.get(name)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if not isinstance(item, str):
                return None
            parts.append(item)
        return " ".join(parts) or None
    return None


def get_seo_data(domain: str):
    try:
        response = safe_get(domain, timeout=10)
        try:
            soup = BeautifulSoup(response.text, "lxml")
            title = soup.title.text if soup.title else ""
            meta: Tag | None = soup.select_one('meta[name="description"]')
            description = _get_tag_attribute(meta, "content") or ""
            return {
                "title": title,
                "description": description,
                "h1_count": len(soup.find_all("h1")),
            }
        finally:
            response.close()
    except Exception:
        return {"error": "SEO inspection failed for public domain"}
