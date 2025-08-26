"""GuardianX FastAPI main entrypoint."""
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.settings import settings
from app.middleware import (
    RateLimitMiddleware,
    BodySizeLimitMiddleware,
    SecurityHeadersMiddleware,
    pow_check,
)
from app.services.router import router as api_router
from app.services.logger import setup_logging

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"

def create_app() -> FastAPI:
    """Create and configure FastAPI app."""
    # hide swagger/redoc in prod if you want
    app = FastAPI(title="GuardianX", docs_url=None, redoc_url=None)

    # API routes
    app.include_router(api_router)

    # static assets (css/js/img incl. GX_Logo.PNG) -> /static/*
    app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["content-type"],
    )

    # security/abuse protections
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(BodySizeLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    setup_logging()
    return app

app = create_app()

# ---------- UI ROUTE ----------
@app.get("/", include_in_schema=False)
def index():
    """Serve the mobile-friendly UI."""
    return FileResponse(WEB_DIR / "index.html")
# --------------------------------

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
        content='{"error":"Server error"}',
        media_type="application/json",
        status_code=500,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
