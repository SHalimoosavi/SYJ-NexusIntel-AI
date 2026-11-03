from pathlib import Path


def test_uvicorn_launch_config_disables_implicit_forwarded_header_trust():
    root = Path(__file__).resolve().parents[2]
    dockerfile = (root / "backend" / "Dockerfile").read_text(encoding="utf-8")
    procfile = (root / "backend" / "Procfile").read_text(encoding="utf-8")

    for command in (dockerfile, procfile):
        assert "--no-proxy-headers" in command
        assert "--forwarded-allow-ips=" in command
