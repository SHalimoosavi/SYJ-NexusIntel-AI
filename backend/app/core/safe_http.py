"""Outbound HTTP safeguards for user-supplied domain intelligence targets.

This performs DNS/IP and redirect validation before every request. Production
deployments must additionally enforce outbound egress restrictions at the
network boundary to mitigate DNS rebinding and cloud metadata access.
"""
import ipaddress
import socket
from urllib.parse import urljoin, urlsplit

import requests

from app.core.input_validation import validate_domain


def assert_public_domain(domain: str) -> str:
    host = validate_domain(domain)
    try:
        answers = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError("Target domain could not be resolved") from exc
    addresses = {answer[4][0].split("%", 1)[0] for answer in answers}
    if not addresses:
        raise ValueError("Target domain has no public address")
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise ValueError("Target domain resolves to a non-public address")
    return host


def safe_get(domain: str, timeout: int = 10, max_redirects: int = 3):
    host = assert_public_domain(domain)
    current_url = f"https://{host}/"
    for redirect_count in range(max_redirects + 1):
        parsed = urlsplit(current_url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("Only HTTPS public targets are permitted")
        if parsed.username or parsed.password or parsed.port not in (None, 443):
            raise ValueError("Target URL contains unsupported authority details")
        checked_host = assert_public_domain(parsed.hostname)
        response = requests.get(
            current_url,
            timeout=timeout,
            allow_redirects=False,
            headers={"User-Agent": "SYJ-NexusIntel-AI/1.0"},
        )
        if response.is_redirect or response.is_permanent_redirect:
            location = response.headers.get("Location")
            response.close()
            if not location or redirect_count >= max_redirects:
                raise ValueError("Target exceeded the permitted redirect limit")
            next_url = urljoin(current_url, location)
            next_parsed = urlsplit(next_url)
            if next_parsed.hostname is None:
                raise ValueError("Invalid redirect target")
            assert_public_domain(next_parsed.hostname)
            current_url = next_url
            continue
        return response
    raise ValueError("Target exceeded the permitted redirect limit")
