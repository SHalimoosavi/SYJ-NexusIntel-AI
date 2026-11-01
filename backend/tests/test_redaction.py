import logging

from app.core.redaction import RedactingLogFilter, redact_text


def test_redact_text_removes_common_secrets_and_pii():
    raw = (
        "user=alice@example.com Authorization=Bearer abc.def "
        "jwt=eyJabcdefgh.abcdefgh.abcdefgh password=hunter2 "
        "client=203.0.113.9 phone=+1 415 555 0123"
    )
    safe = redact_text(raw)
    assert "alice@example.com" not in safe
    assert "abc.def" not in safe
    assert "eyJabcdefgh" not in safe
    assert "hunter2" not in safe
    assert "203.0.113.9" not in safe
    assert "415 555 0123" not in safe


def test_redacting_log_filter_formats_then_redacts_arguments():
    record = logging.LogRecord(
        "test", logging.INFO, __file__, 1,
        "token=%s email=%s", ("sensitive-token-value", "a@example.com"), None,
    )
    assert RedactingLogFilter().filter(record)
    rendered = record.getMessage()
    assert "sensitive-token-value" not in rendered
    assert "a@example.com" not in rendered
