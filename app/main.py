"""GuardianX FastAPI main entrypoint."""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.settings import settings
from app.middleware import (
    RateLimitMiddleware,
    BodySizeLimitMiddleware,
    SecurityHeadersMiddleware,
    pow_check,
)
from app.services.router import router as api_router
from app.services.logger import setup_logging
import os

def create_app() -> FastAPI:
    """Create and configure FastAPI app."""
    app = FastAPI(title="GuardianX")
    app.include_router(api_router)
    app.mount("/static", StaticFiles(directory="web/static"), name="static")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(BodySizeLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    setup_logging()
    return app

app = create_app()

@app.middleware("http")
async def proof_of_work_middleware(request: Request, call_next):
    """Optional Proof-of-Work header check."""
    if settings.POW_ENABLE:
        pow_check(request)
    return await call_next(request)

# Error handler for safe JSON responses
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return Response(
        content='{"error":"Internal server error"}',
        media_type="application/json",
        status_code=500,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)