"""SSRF-resistant outbound HTTPS client for public domain inspection.

DNS answers are validated and the connection is pinned to one validated IP,
while TLS SNI and certificate verification continue to use the original host.
Redirects are followed manually and revalidated at each hop.
"""
import ipaddress
import socket
import ssl
from typing import cast
from urllib.parse import urljoin, urlsplit

import certifi
from urllib3 import Timeout
from urllib3.connectionpool import HTTPSConnectionPool

from app.core.input_validation import validate_domain


def resolve_public_addresses(domain: str) -> tuple[str, list[str]]:
    host = validate_domain(domain)
    try:
        answers = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError("Target domain could not be resolved") from exc
    addresses = sorted({cast(str, answer[4][0]).split("%", 1)[0] for answer in answers})
    if not addresses:
        raise ValueError("Target domain has no public address")
    for address in addresses:
        if not ipaddress.ip_address(address).is_global:
            raise ValueError("Target domain resolves to a non-public address")
    return host, addresses


def assert_public_domain(domain: str) -> str:
    host, _addresses = resolve_public_addresses(domain)
    return host


class SafeHTTPResponse:
    """Small response adapter exposing only the attributes used by services."""

    def __init__(self, response, pool):
        self._response = response
        self._pool = pool
        self.status_code = response.status
        self.headers = response.headers

    @property
    def text(self) -> str:
        return self._response.data.decode("utf-8", errors="replace")

    @property
    def is_redirect(self) -> bool:
        return self.status_code in {301, 302, 303, 307, 308}

    @property
    def is_permanent_redirect(self) -> bool:
        return self.status_code in {301, 308}

    def close(self) -> None:
        try:
            self._response.release_conn()
        finally:
            self._pool.close()


def _pinned_https_get(
    host: str,
    ip_address: str,
    path: str,
    timeout: int,
    max_response_bytes: int,
) -> SafeHTTPResponse:
    pool = HTTPSConnectionPool(
        host=ip_address,
        port=443,
        maxsize=1,
        block=True,
        cert_reqs=ssl.CERT_REQUIRED,
        ca_certs=certifi.where(),
        server_hostname=host,
        assert_hostname=host,
    )
    try:
        response = pool.request(
            "GET",
            path,
            headers={
                "Host": host,
                "User-Agent": "SYJ-NexusIntel-AI/1.0",
                "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "identity",
            },
            redirect=False,
            retries=False,
            timeout=Timeout(total=timeout),
            preload_content=False,
        )
        body = response.read(max_response_bytes + 1, decode_content=True)
        if len(body) > max_response_bytes:
            response.close()
            pool.close()
            raise ValueError("Target response exceeded the permitted size")
        setattr(response, "data", body)
        return SafeHTTPResponse(response, pool)
    except Exception:
        pool.close()
        raise


def safe_get(
    domain: str,
    timeout: int = 10,
    max_redirects: int = 3,
    max_response_bytes: int = 2 * 1024 * 1024,
) -> SafeHTTPResponse:
    host, addresses = resolve_public_addresses(domain)
    current_url = f"https://{host}/"

    for redirect_count in range(max_redirects + 1):
        parsed = urlsplit(current_url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("Only HTTPS public targets are permitted")
        if parsed.username or parsed.password or parsed.port not in (None, 443):
            raise ValueError("Target URL contains unsupported authority details")

        host, addresses = resolve_public_addresses(parsed.hostname)
        request_path = parsed.path or "/"
        if parsed.query:
            request_path += f"?{parsed.query}"

        response = _pinned_https_get(host, addresses[0], request_path, timeout, max_response_bytes)
        if response.is_redirect:
            location = response.headers.get("Location")
            response.close()
            if not location or redirect_count >= max_redirects:
                raise ValueError("Target exceeded the permitted redirect limit")
            next_url = urljoin(current_url, location)
            next_parsed = urlsplit(next_url)
            if next_parsed.scheme != "https" or not next_parsed.hostname:
                raise ValueError("Redirect target must use HTTPS")
            if next_parsed.username or next_parsed.password or next_parsed.port not in (None, 443):
                raise ValueError("Redirect target contains unsupported authority details")
            resolve_public_addresses(next_parsed.hostname)
            current_url = next_url
            continue
        return response

    raise ValueError("Target exceeded the permitted redirect limit")
