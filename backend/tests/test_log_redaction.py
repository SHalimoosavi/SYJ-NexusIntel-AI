import logging

from app.core.redaction import RedactingLogFilter, redact_text


def test_redact_text_masks_credentials_and_personal_data():
    source = (
        "user=person@example.invalid phone=+1 415 555 0123 "
        "Authorization: Bearer abcdefghijklmnop "
        "access_token=eyJabcdefgh.ijklmnop.qrstuvwx"
    )
    redacted = redact_text(source)
    assert "person@example.invalid" not in redacted
    assert "+1 415 555 0123" not in redacted
    assert "abcdefghijklmnop" not in redacted
    assert "eyJabcdefgh" not in redacted


def test_log_filter_removes_arguments_and_exception_details():
    record = logging.LogRecord(
        "test",
        logging.ERROR,
        __file__,
        10,
        "request failed for %s",
        ("person@example.invalid",),
        (ValueError, ValueError("secret=hidden"), None),
    )
    assert RedactingLogFilter().filter(record)
    assert "person@example.invalid" not in record.getMessage()
    assert "hidden" not in record.getMessage()
    assert record.exc_info is None
