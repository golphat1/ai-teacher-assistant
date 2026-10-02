# backend/app/core/redact.py
import re

_SECRET_PATTERN = re.compile(r"(sk-[a-zA-Z0-9\-_]{10,}|Bearer\s+[a-zA-Z0-9\-_.]+)")


def redact_secrets(text: str) -> str:
    return _SECRET_PATTERN.sub("[REDACTED]", text)