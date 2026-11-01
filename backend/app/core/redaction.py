"""Conservative redaction helpers for application and audit log fields."""
import logging
import re

_EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*")
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(secret|token|password|api[_-]?key|authorization|cookie)\s*[:=]\s*[^\s,;]+"
)
_IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
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


class RedactingLogFilter(logging.Filter):
    """Redact rendered log messages before they reach configured handlers."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            rendered = record.getMessage()
        except Exception:
            rendered = "[UNFORMATTABLE_LOG_RECORD]"
        record.msg = redact_text(rendered) or ""
        record.args = ()
        return True
