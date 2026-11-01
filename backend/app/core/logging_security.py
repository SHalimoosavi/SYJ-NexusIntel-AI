"""Logging filter that removes secrets and PII before handlers emit records."""
import logging

from app.core.redaction import redact_log_message


class SensitiveDataLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            rendered = record.getMessage()
        except Exception:
            rendered = "[unrenderable log record]"
        record.msg = redact_log_message(rendered)
        record.args = ()
        # Exception tracebacks may contain request values or SQL parameters.
        # Production exception details are intentionally omitted from logs.
        record.exc_info = None
        record.exc_text = None
        record.stack_info = None
        return True


def configure_sensitive_logging() -> None:
    root = logging.getLogger()
    if not any(isinstance(item, SensitiveDataLogFilter) for item in root.filters):
        root.addFilter(SensitiveDataLogFilter())
    for handler in root.handlers:
        if not any(isinstance(item, SensitiveDataLogFilter) for item in handler.filters):
            handler.addFilter(SensitiveDataLogFilter())
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        target = logging.getLogger(logger_name)
        if not any(isinstance(item, SensitiveDataLogFilter) for item in target.filters):
            target.addFilter(SensitiveDataLogFilter())
        for handler in target.handlers:
            if not any(isinstance(item, SensitiveDataLogFilter) for item in handler.filters):
                handler.addFilter(SensitiveDataLogFilter())
