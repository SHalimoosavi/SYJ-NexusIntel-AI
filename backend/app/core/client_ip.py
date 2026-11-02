"""Resolve client IPs only through explicitly trusted reverse proxies."""
import ipaddress
import os
from collections.abc import Iterable


def _parse_address(value: str):
    try:
        return ipaddress.ip_address(value.strip())
    except ValueError:
        return None


def _parse_networks(values: Iterable[str]):
    networks = []
    for value in values:
        item = value.strip()
        if not item:
            continue
        try:
            networks.append(ipaddress.ip_network(item, strict=False))
        except ValueError as exc:
            raise RuntimeError("TRUSTED_PROXIES contains an invalid IP or CIDR") from exc
    return tuple(networks)


def resolve_client_ip(
    peer_ip: str | None,
    forwarded_for: str | None,
    trusted_proxies: Iterable[str] | None = None,
) -> str:
    """Return the right-most untrusted address in a validated X-Forwarded-For chain."""
    peer = _parse_address(peer_ip or "")
    if peer is None:
        return peer_ip or "unknown"

    configured = trusted_proxies
    if configured is None:
        configured = os.getenv("TRUSTED_PROXIES", "").split(",")
    networks = _parse_networks(configured)

    def is_trusted(address):
        return any(address.version == network.version and address in network for network in networks)

    if not forwarded_for or not is_trusted(peer):
        return str(peer)

    forwarded = [_parse_address(value) for value in forwarded_for.split(",")]
    if not forwarded or any(address is None for address in forwarded):
        return str(peer)

    # Walk from the socket peer toward the origin. The first non-proxy hop is
    # the client; entries to its left are caller-controlled and are ignored.
    for address in reversed([*forwarded, peer]):
        if not is_trusted(address):
            return str(address)
    return str(forwarded[0])
