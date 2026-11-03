from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "check_no_deployment_providers.py"
SPEC = importlib.util.spec_from_file_location("deployment_provider_guard", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)


def add_tracked_file(root: Path, relative: str, content: bytes) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    subprocess.run(["git", "add", relative], cwd=root, check=True)


def init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)


def run_guard(root: Path, capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    monkeypatch_result = None
    old_cwd = Path.cwd()
    try:
        import os
        os.chdir(root)
        result = GUARD.main()
    finally:
        os.chdir(old_cwd)
    output = capsys.readouterr().out
    return result, output


def test_clean_tree_passes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    init_repo(tmp_path)
    add_tracked_file(tmp_path, "README.md", b"Normal self-hosted documentation.\n")
    result, output = run_guard(tmp_path, capsys)
    assert result == 0
    assert "passed" in output


@pytest.mark.parametrize(
    ("relative", "content"),
    [
        ("config/" + "ver" + "cel.json", b"{}"),
        ("config/" + "rail" + "way.json", b"{}"),
        ("config/" + "rail" + "way.toml", b""),
        ("config/" + "Pro" + "cfile", b"web: run\n"),
        ("config/" + "nix" + "packs", b""),
        ("config/" + "nix" + "packs.toml", b""),
        ("config/" + "." + "ver" + "cel" + "/project", b""),
        ("config/settings.env", ("VER" + "CEL_" + "TOKEN=secret-value\n").encode()),
        ("config/host.txt", ( "app." + "ver" + "cel" + ".app\n").encode()),
        ("config/host2.txt", ("api." + "rail" + "way" + ".app\n").encode()),
        ("config/host3.txt", ("service." + "up." + "rail" + "way" + ".app\n").encode()),
        ("config/vars.env", ("RAIL" + "WAY_" + "TOKEN=another-secret\n").encode()),
    ],
)
def test_each_rule_fails(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    relative: str,
    content: bytes,
) -> None:
    init_repo(tmp_path)
    add_tracked_file(tmp_path, relative, content)
    result, output = run_guard(tmp_path, capsys)
    assert result == 1
    assert relative in output
    assert ":1:" in output


def test_historical_allowlist_passes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    init_repo(tmp_path)
    legacy = ("https://" + "app." + "ver" + "cel" + ".app").encode()
    audit = ("RAIL" + "WAY_" + "TOKEN=historic").encode()
    add_tracked_file(tmp_path, "docs/legacy-hosting.md", legacy)
    add_tracked_file(tmp_path, "docs/audit/provider-review.md", audit)
    result, output = run_guard(tmp_path, capsys)
    assert result == 0
    assert "passed" in output


def test_binary_files_are_skipped(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    init_repo(tmp_path)
    add_tracked_file(tmp_path, "assets/blob.bin", b"\x00" + b"VERCEL_TOKEN=https://x.vercel.app")
    result, output = run_guard(tmp_path, capsys)
    assert result == 0
    assert "passed" in output


def test_output_never_prints_secret_value(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    init_repo(tmp_path)
    secret = "distinctive-secret-value-7391"
    content = ("VER" + "CEL_" + "TOKEN=" + secret + "\n").encode()
    add_tracked_file(tmp_path, "config/private.env", content)
    result, output = run_guard(tmp_path, capsys)
    assert result == 1
    assert "provider environment variable name" in output
    assert secret not in output
