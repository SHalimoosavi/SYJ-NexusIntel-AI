import pytest

from app.core.input_validation import validate_domain


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("example.com", "example.com"),
        (" EXAMPLE.COM. ", "example.com"),
        ("bücher.de", "xn--bcher-kva.de"),
    ],
)
def test_valid_public_hostname(value, expected):
    assert validate_domain(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "localhost",
        "service.local",
        "metadata.google.internal",
        "127.0.0.1",
        "10.0.0.1",
        "[::1]",
        "https://example.com",
        "example.com/path",
        "example.com:443",
        "user@example.com",
    ],
)
def test_rejects_non_hostname_or_internal_targets(value):
    with pytest.raises(ValueError):
        validate_domain(value)
