from fastapi import Request
from jose import JWTError
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.security import decode_token


def rate_limit_key(request: Request) -> str:
    # Pre-authentication routes have no user identity to key against — IP is the
    # only available signal, and this is exactly where brute-force protection matters most.
    if request.url.path.startswith("/auth"):
        return f"ip:{get_remote_address(request)}"

    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
        try:
            payload = decode_token(token)
            if payload.get("type") == "access":
                return f"user:{payload['sub']}"
        except JWTError:
            pass  # fall through to IP-based keying below

    # No valid token found (missing, expired, malformed) — fall back to IP so the
    # route's rate limit still applies to something, rather than being unkeyable.
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(key_func=rate_limit_key, enabled=settings.rate_limiting_enabled)

# --- bottom of file ---
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    # The window length (60s for "5/minute") is a safe upper bound for how long a client should wait.
    try:
        retry_after = int(exc.limit.limit.get_expiry())
    except AttributeError:
        retry_after = 60
    return JSONResponse(
        status_code=429,
        content={"error": f"Rate limit exceeded: {exc.detail}"},
        headers={"Retry-After": str(retry_after)},
    )