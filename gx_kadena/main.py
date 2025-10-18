from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from urllib.parse import unquote
import datetime as dt
import sys

# Core modules
from .validator import validate_address, ValidationResult
from .rwa.assets import get_rwa_assets
from .iso.pacs008 import xml_pacs008
from .iso.camt053 import xml_camt053
from .security_mw import get_cors_middleware, security_headers_mw
from .logging_mw import logging_middleware

# ---------- APP CONFIG ----------
app = FastAPI(
    title="GX-Kadena (Stateless Edition)",
    version="0.2.0",
    description="ISO20022-ready, stateless validator for Kadena network (no DB, no cache, no session)."
)

# ---------- MIDDLEWARE ----------
get_cors_middleware(app)
app.middleware("http")(security_headers_mw)
app.middleware("http")(logging_middleware)

# Add stateless compliance header
@app.middleware("http")
async def stateless_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Stateless-Mode"] = "true"
    return response


# ---------- DIRECTORY STRUCTURE ----------
APP_FILE = Path(__file__).resolve()
GX_DIR   = APP_FILE.parent
REPO_DIR = GX_DIR.parent
WEB_DIR  = REPO_DIR / "web"
LEGACY   = GX_DIR / "static"

print(f"[BOOT] GX_DIR={GX_DIR}")
print(f"[BOOT] WEB_DIR exists? {WEB_DIR.exists()}")
print(f"[BOOT] LEGACY exists? {LEGACY.exists()}")
print(f"[BOOT] sys.path[0]={sys.path[0]}")

# ---------- UI MOUNT ----------
MOUNTED = False
if WEB_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(WEB_DIR), html=True), name="ui")
    MOUNTED = True
elif LEGACY.exists():
    app.mount("/app", StaticFiles(directory=str(LEGACY), html=True), name="ui")
    MOUNTED = True
else:
    print("⚠️ UI folder not found. Running API-only mode.")

@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/app/" if MOUNTED else "/docs")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    for p in [WEB_DIR / "static" / "favicon.ico", LEGACY / "favicon.ico"]:
        if p.exists():
            return FileResponse(p)
    return HTMLResponse(status_code=204, content="")

# ---------- HEALTH ----------
@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "timestamp": dt.datetime.utcnow().isoformat() + "Z", "stateless": True}

# ---------- VALIDATOR CORE ----------
@app.get("/validate/{address}", response_model=ValidationResult, tags=["validate"])
async def validate(address: str):
    address = unquote(address)
    try:
        return await validate_address(address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/risk/{address}", tags=["validate"])
async def risk_endpoint(address: str):
    address = unquote(address)
    res = await validate_address(address)
    return {"address": res.address, "risk_score": res.risk_score, "flags": res.flags, "stateless": True}

# ---------- RWA ----------
@app.get("/rwa/{address}", tags=["rwa"])
async def rwa(address: str):
    address = unquote(address)
    rwa_blk = get_rwa_assets(address)
    return {"address": address, "assets": rwa_blk, "stateless": True}

# ---------- ISO 20022 EXPORT ----------
@app.get("/iso/pacs008.xml", tags=["iso20022"])
async def iso_pacs(address: str, reference_id: str = "GX-TEST-001",
                   amount: str = "0.00", ccy: str = "KDA"):
    address = unquote(address)
    res = await validate_address(address)
    rwa_blk = get_rwa_assets(address)
    xml_bytes = xml_pacs008(
        address=res.address,
        ref_id=reference_id,
        amt=amount,
        ccy=ccy,
        risk=res.risk_score,
        rwa_block=rwa_blk
    )
    return Response(
        content=xml_bytes,
        media_type="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="pacs008_{reference_id}.xml"',
            "X-Stateless-Mode": "true"
        }
    )

@app.get("/iso/camt053.xml", tags=["iso20022"])
async def iso_camt(address: str):
    address = unquote(address)
    res = await validate_address(address)
    rwa_blk = get_rwa_assets(address)
    xml_bytes = xml_camt053(
        address=res.address,
        balance=res.total_balance,
        risk=res.risk_score,
        rwa_block=rwa_blk
    )
    return Response(
        content=xml_bytes,
        media_type="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="camt053_{res.address}.xml"',
            "X-Stateless-Mode": "true"
        }
    )

# ---------- STATUS ----------
@app.get("/status", tags=["system"])
async def status():
    return {
        "service": "GX-Kadena (Stateless Edition)",
        "version": "0.2.0",
        "network": "mainnet01",
        "stateless": True,
        "time": dt.datetime.utcnow().isoformat() + "Z"
    }
