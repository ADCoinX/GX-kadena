from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, Response, HTTPException
import time
from .config import ALLOWED_ORIGIN, RATE_LIMIT_RPS

_last_ts = time.time()
_tokens = RATE_LIMIT_RPS

def get_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[ALLOWED_ORIGIN] if ALLOWED_ORIGIN != "*" else ["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

async def security_headers_mw(request: Request, call_next):
    global _last_ts, _tokens
    # Token bucket simple rate limit
    now = time.time()
    _tokens = min(RATE_LIMIT_RPS, _tokens + (now - _last_ts) * RATE_LIMIT_RPS)
    _last_ts = now
    if _tokens < 1.0:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    _tokens -= 1.0
    response: Response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response