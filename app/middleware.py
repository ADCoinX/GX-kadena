"""GuardianX custom middleware."""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.settings import settings
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter."""
    bucket = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        now = int(time.time())
        burst = settings.RATE_BURST
        per_min = settings.RATE_LIMIT_PER_MIN
        bucket = self.bucket.setdefault(ip, {"count": 0, "ts": now})
        if now - bucket["ts"] > 60:
            bucket["count"] = 0
            bucket["ts"] = now
        bucket["count"] += 1
        if bucket["count"] > per_min + burst:
            return Response(
                content='{"error":"rate limit exceeded"}',
                media_type="application/json",
                status_code=429,
            )
        return await call_next(request)

class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Limit request body size."""
    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        if len(body) > settings.MAX_BODY_BYTES:
            return Response(
                content='{"error":"request too large"}',
                media_type="application/json",
                status_code=413,
            )
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Set secure HTTP headers."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=63072000"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

def pow_check(request: Request) -> None:
    """Proof-of-work check stub."""
    # Implement POW check if enabled; raise if invalid
    if settings.POW_ENABLE:
        # Validate nonce, ts, and hash difficulty (stub)
        pass