"""Conservative redaction helpers for application and audit log fields."""
import re

_EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*")
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(secret|token|password|api[_-]?key)\s*[:=]\s*[^\s,;]+"
)


def redact_text(value: str | None) -> str | None:
    if value is None:
        return None
    result = _EMAIL.sub("[REDACTED_EMAIL]", value)
    result = _BEARER.sub("Bearer [REDACTED]", result)
    result = _JWT.sub("[REDACTED_TOKEN]", result)
    return _SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=[REDACTED]", result)
