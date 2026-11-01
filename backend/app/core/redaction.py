"""Conservative redaction helpers for application and audit log fields."""
import re

_EMAIL = re.compile(r"(?i)\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}\\b")
_BEARER = re.compile(r"(?i)\\bBearer\\s+[A-Za-z0-9._~+/-]+=*")
_JWT = re.compile(r"\\beyJ[A-Za-z0-9_-]{8,}\\.[A-Za-z0-9_-]{8,}\\.[A-Za-z0-9_-]{8,}\\b")
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\\b(secret|token|password|api[_-]?key|private[_-]?key|authorization|cookie)\\s*[:=]\\s*[^\\s,;]+"
)
_PHONE = re.compile(r"(?<!\\w)(?:\\+?\\d[\\d .()/-]{7,}\\d)(?!\\w)")


def redact_text(value: str | None) -> str | None:
    if value is None:
        return None
    result = _EMAIL.sub("[REDACTED_EMAIL]", value)
    result = _BEARER.sub("Bearer [REDACTED]", result)
    result = _JWT.sub("[REDACTED_TOKEN]", result)
    result = _SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=[REDACTED]", result)
    return _PHONE.sub("[REDACTED_PHONE]", result)


def redact_log_message(value: object) -> str:
    """Convert arbitrary log arguments to a redacted, bounded message."""
    rendered = str(value)
    redacted = redact_text(rendered) or ""
    return redacted[:4000]
