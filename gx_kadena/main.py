
# main.py
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import datetime as dt

# --- internal imports (sedia ada dalam repo kau) ---
from .validator import validate_address, ValidationResult
from .rwa.assets import get_rwa_assets
from .iso.pacs008 import xml_pacs008
from .iso.camt053 import xml_camt053
from .security_mw import get_cors_middleware, security_headers_mw
from .logging_mw import logging_middleware
from .metrics import metrics_mw, get_metrics

# ---------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------
app = FastAPI(title="GX-Kadena (MVP)", version="0.1.0")

# CORS & middlewares
get_cors_middleware(app)
app.middleware("http")(security_headers_mw)
app.middleware("http")(logging_middleware)
app.middleware("http")(metrics_mw)

# ---------------------------------------------------------------------
# Static UI (serve folder: gx_kadena/static)
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Mount UI under /app to avoid shadowing /docs
app.mount("/app", StaticFiles(directory=str(STATIC_DIR), html=True), name="ui")

# Redirect "/" → UI
@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/app/")

# Optional: direct file routes (favicon, robots)
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    icon = STATIC_DIR / "favicon.ico"
    if icon.exists():
        return FileResponse(icon)
    return HTMLResponse(status_code=204, content="")

# ---------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------
@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "ts": dt.datetime.utcnow().isoformat() + "Z"}

# ---------------------------------------------------------------------
# Core: Validate / Risk / RWA
# ---------------------------------------------------------------------
@app.get("/validate/{address}", response_model=ValidationResult, tags=["validate"])
async def validate(address: str):
    try:
        return await validate_address(address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/risk/{address}", tags=["validate"])
async def risk_endpoint(address: str):
    res = await validate_address(address)
    return {"address": res.address, "risk_score": res.risk_score, "flags": res.flags}

@app.get("/rwa/{address}", tags=["rwa"])
async def rwa(address: str):
    return get_rwa_assets(address)

# ---------------------------------------------------------------------
# ISO 20022 XML exports
# ---------------------------------------------------------------------
@app.get("/iso/pacs008.xml", tags=["iso20022"])
async def iso_pacs(
    address: str,
    reference_id: str = "GX-TEST-001",
    amount: str = "0.00",
    ccy: str = "KDA",
):
    res = await validate_address(address)
    rwa_blk = get_rwa_assets(address)
    xml_bytes = xml_pacs008(
        address=res.address,
        ref_id=reference_id,
        amt=amount,
        ccy=ccy,
        risk=res.risk_score,
        rwa_block=rwa_blk,
    )
    return Response(
        content=xml_bytes,
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="pacs008_{reference_id}.xml"'},
    )

@app.get("/iso/camt053.xml", tags=["iso20022"])
async def iso_camt(address: str):
    res = await validate_address(address)
    rwa_blk = get_rwa_assets(address)
    xml_bytes = xml_camt053(
        address=res.address,
        balance=res.total_balance,
        risk=res.risk_score,
        rwa_block=rwa_blk,
    )
    return Response(
        content=xml_bytes,
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="camt053_{res.address}.xml"'},
    )

# ---------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------
@app.get("/metrics", include_in_schema=False, tags=["system"])
async def metrics():
    content, content_type = get_metrics()
    return Response(content, media_type=content_type)
