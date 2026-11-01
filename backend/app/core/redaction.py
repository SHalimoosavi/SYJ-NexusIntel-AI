"""Conservative redaction helpers for application and audit log fields."""
import logging
import re

_EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*")
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(secret|token|password|api[_-]?key|private[_-]?key|authorization|cookie)\s*[:=]\s*[^\s,;]+"
)
_PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d .()/-]{7,}\d)(?!\w)")


def redact_text(value: str | None) -> str | None:
    if value is None:
        return None
    result = _EMAIL.sub("[REDACTED_EMAIL]", value)
    result = _BEARER.sub("Bearer [REDACTED]", result)
    result = _JWT.sub("[REDACTED_TOKEN]", result)
    result = _SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=[REDACTED]", result)
    result = _IPV4.sub("[REDACTED_IP]", result)
    return _PHONE.sub("[REDACTED_PHONE]", result)


def redact_log_message(value: object) -> str:
    rendered = str(value)
    return (redact_text(rendered) or "")[:4000]


class RedactingLogFilter(logging.Filter):
    """Redact log payloads and suppress exception text that may contain secrets."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            rendered = record.getMessage()
        except Exception:
            rendered = "[unrenderable log record]"
        record.msg = redact_log_message(rendered)
        record.args = ()
        record.exc_info = None
        record.exc_text = None
        record.stack_info = None
        return True
