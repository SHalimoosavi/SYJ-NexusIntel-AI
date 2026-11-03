"""Typing regression for production API documentation configuration."""
from mypy import api


def test_api_docs_configuration_is_fully_typed() -> None:
    stdout, stderr, exit_status = api.run(
        ["--config-file", "mypy.ini", "app/core/api_docs.py"]
    )
    assert exit_status == 0, f"mypy stdout:\n{stdout}\nmypy stderr:\n{stderr}"
