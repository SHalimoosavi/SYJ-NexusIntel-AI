"""Validation helpers for public DNS hostnames accepted as scan targets."""
import ipaddress
import re

import idna

_LABEL = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$")
_BLOCKED_SUFFIXES = (".localhost", ".local", ".internal", ".test", ".invalid", ".example")


def validate_domain(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("A valid public domain name is required")
    candidate = value.strip().rstrip(".")
    if not candidate or len(candidate) > 253:
        raise ValueError("A valid public domain name is required")
    if any(char in candidate for char in "/\\:@?#") or "://" in candidate:
        raise ValueError("Provide a hostname only, without scheme, path, port or credentials")
    if candidate.lower() == "localhost" or candidate.lower().endswith(_BLOCKED_SUFFIXES):
        raise ValueError("Local and internal hostnames are not permitted")
    try:
        ipaddress.ip_address(candidate.strip("[]"))
    except ValueError:
        pass
    else:
        raise ValueError("IP address targets are not permitted; provide a public DNS hostname")
    try:
        ascii_domain = idna.encode(candidate, uts46=True).decode("ascii").lower()
    except idna.IDNAError as exc:
        raise ValueError("Invalid internationalized domain name") from exc
    labels = ascii_domain.split(".")
    if len(labels) < 2 or any(not _LABEL.fullmatch(label) for label in labels):
        raise ValueError("Provide a fully qualified public domain name")
    if len(labels[-1]) < 2:
        raise ValueError("Invalid top-level domain")
    return ascii_domain
