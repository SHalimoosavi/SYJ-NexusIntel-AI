#!/usr/bin/env python3
"""CI guard for retired hosted-deployment artifacts and provider references."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HISTORICAL_ALLOWLIST = ("docs/legacy-hosting.md", "docs/audit/")
CONFIG_FILENAMES = {
    "ver" + "cel" + ".json",
    "." + "ver" + "cel",
    "rail" + "way" + ".json",
    "rail" + "way" + ".toml",
    "Pro" + "cfile",
    "nix" + "packs",
    "nix" + "packs.toml",
}

PROVIDER_VARIABLE = re.compile(
    r"(?i)\b(?:" + "VER" + "CEL" + "|" + "RAIL" + "WAY" + r")_[A-Z0-9_]+\b"
)
VERCEL_DOMAIN = re.compile(
    r"(?i)(?:[a-z0-9-]+\.)?" + re.escape("ver" + "cel") + r"\.app\b"
)
RAILWAY_DOMAIN = re.compile(
    r"(?i)(?:[a-z0-9-]+\.)?" + re.escape("rail" + "way") + r"\.app\b"
)
RAILWAY_UPSTREAM_DOMAIN = re.compile(
    r"(?i)(?:[a-z0-9-]+\.)?" + re.escape("up." + "rail" + "way" + ".app") + r"\b"
)


def is_allowlisted(relative_path: str) -> bool:
    return relative_path == HISTORICAL_ALLOWLIST[0] or relative_path.startswith(
        HISTORICAL_ALLOWLIST[1]
    )


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [
        Path(item.decode("utf-8"))
        for item in result.stdout.split(b"\0")
        if item
    ]


def is_binary(data: bytes) -> bool:
    if b"\0" in data:
        return True
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def path_rule(relative_path: str) -> str | None:
    parts = Path(relative_path).parts
    for part in parts:
        if part in CONFIG_FILENAMES:
            return "retired deployment configuration filename"
    return None


def content_rules(text: str) -> list[tuple[int, str]]:
    matches: list[tuple[int, str]] = []
    patterns = (
        ("provider environment variable name", PROVIDER_VARIABLE),
        ("Vercel hosted domain", VERCEL_DOMAIN),
        ("Railway hosted domain", RAILWAY_DOMAIN),
        ("Railway upstream domain", RAILWAY_UPSTREAM_DOMAIN),
    )
    for line_number, line in enumerate(text.splitlines(), start=1):
        for label, pattern in patterns:
            if pattern.search(line):
                matches.append((line_number, label))
    return matches


def main() -> int:
    failures: list[str] = []
    for path in tracked_files():
        relative = path.as_posix()
        if is_allowlisted(relative):
            continue

        filename_violation = path_rule(relative)
        if filename_violation:
            failures.append(f"{relative}:1: {filename_violation}")
            continue

        try:
            data = path.read_bytes()
        except OSError:
            failures.append(f"{relative}:1: tracked file could not be read")
            continue

        if is_binary(data):
            continue

        text = data.decode("utf-8")
        for line_number, label in content_rules(text):
            failures.append(f"{relative}:{line_number}: {label}")

    if failures:
        print("Deployment-provider guard failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Deployment-provider guard passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
