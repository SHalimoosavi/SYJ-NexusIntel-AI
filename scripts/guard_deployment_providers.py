#!/usr/bin/env python3
"""Reject retired hosted-deployment configuration and credential references."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ALLOWED_HISTORICAL_FILE = "docs/legacy-hosting.md"
RETIRED_FILES = {
    "ver" + "cel.json",
    "rail" + "way.json",
    "rail" + "way.toml",
    "Pro" + "cfile",
    "nix" + "packs",
    "nix" + "packs.toml",
}
RETIRED_DIRECTORIES = {
    "." + "ver" + "cel",
    "." + "rail" + "way",
}
ENV_PATTERN = re.compile(r"(?i)\\b(?:" + "VER" + "CEL" + "|" + "RAIL" + "WAY" + r")_[A-Z0-9_]+\\b")
HOST_PATTERN = re.compile(
    r"(?i)(?:[a-z0-9-]+\\.)?(?:"
    + re.escape("ver" + "cel")
    + r"\\.app|"
    + re.escape("rail" + "way")
    + r"\\.app)"
)
UPSTREAM_HOST_PATTERN = re.compile(
    r"(?i)(?:[a-z0-9-]+\\.)?" + re.escape("up." + "rail" + "way" + ".app")
)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
    )
    return [Path(item.decode("utf-8")) for item in result.stdout.split(b"\\0") if item]


def main() -> int:
    failures: list[str] = []
    for path in tracked_files():
        relative = path.as_posix()
        if relative == ALLOWED_HISTORICAL_FILE:
            continue
        if path.name in RETIRED_FILES or any(part in RETIRED_DIRECTORIES for part in path.parts):
            failures.append(f"{relative}: retired deployment artifact path")
            continue
        try:
            data = path.read_bytes()
        except OSError as exc:
            failures.append(f"{relative}: cannot read tracked file ({exc})")
            continue
        text = data.decode("utf-8", errors="ignore")
        for label, pattern in (
            ("provider credential variable", ENV_PATTERN),
            ("hosted provider URL", HOST_PATTERN),
            ("hosted backend URL", UPSTREAM_HOST_PATTERN),
        ):
            if pattern.search(text):
                failures.append(f"{relative}: {label}")
                break
    if failures:
        print("Retired deployment configuration or credential references detected:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Deployment-provider guard passed: no retired deployment configuration or credentials found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
