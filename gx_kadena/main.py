from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sys, datetime as dt
from urllib.parse import unquote

from .validator import validate_address, ValidationResult
from .rwa.assets import get_rwa_assets
from .iso.pacs008 import xml_pacs008
from .iso.camt053 import xml_camt053
from .security_mw import get_cors_middleware, security_headers_mw
from .logging_mw import logging_middleware
from .metrics import metrics_mw, get_metrics

app = FastAPI(title="GX-Kadena (MVP)", version="0.1.0")

get_cors_middleware(app)
app.middleware("http")(security_headers_mw)
app.middleware("http")(logging_middleware)
app.middleware("http")(metrics_mw)

# ---------- DEBUG: log lokasi penting ----------
APP_FILE = Path(__file__).resolve()
GX_DIR   = APP_FILE.parent                 # .../gx_kadena
REPO_DIR = GX_DIR.parent                   # .../
WEB_DIR  = REPO_DIR / "web"                # .../web (index.html + static/)
LEGACY   = GX_DIR / "static"               # .../gx_kadena/static (kalau ada)
print(f"[BOOT] __file__={APP_FILE}")
print(f"[BOOT] GX_DIR={GX_DIR}")
print(f"[BOOT] REPO_DIR={REPO_DIR}")
print(f"[BOOT] WEB_DIR exists? {WEB_DIR.exists()}  -> {WEB_DIR}")
print(f"[BOOT] LEGACY exists? {LEGACY.exists()}    -> {LEGACY}")
print(f"[BOOT] sys.path[0]={sys.path[0]}")

# ---------- UI MOUNT (tanpa crash kalau folder tiada) ----------
MOUNTED = False
if WEB_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(WEB_DIR), html=True), name="ui")
    MOUNTED = True
elif LEGACY.exists():
    app.mount("/app", StaticFiles(directory=str(LEGACY), html=True), name="ui")
    MOUNTED = True
else:
    print("⚠️  UI folder not found. Will run API-only. (Tried /web and /gx_kadena/static)")

@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/app/" if MOUNTED else "/docs")

# Optional: favicon lookup di dua lokasi
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    for p in [WEB_DIR / "static" / "favicon.ico", LEGACY / "favicon.ico"]:
        if p.exists():
            return FileResponse(p)
    return HTMLResponse(status_code=204, content="")

# ---------------- Health ----------------
@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "ts": dt.datetime.utcnow().isoformat() + "Z"}

# --------------- Core -------------------
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
    return {"address": res.address, "risk_score": res.risk_score, "flags": res.flags}

@app.get("/rwa/{address}", tags=["rwa"])
async def rwa(address: str):
    address = unquote(address)
    return get_rwa_assets(address)

# -------------- ISO 20022 ---------------
@app.get("/iso/pacs008.xml", tags=["iso20022"])
async def iso_pacs(address: str, reference_id: str = "GX-TEST-001",
                   amount: str = "0.00", ccy: str = "KDA"):
    address = unquote(address)
    res = await validate_address(address)
    rwa_blk = get_rwa_assets(address)
    xml_bytes = xml_pacs008(address=res.address, ref_id=reference_id,
                            amt=amount, ccy=ccy, risk=res.risk_score,
                            rwa_block=rwa_blk)
    return Response(content=xml_bytes, media_type="application/xml",
                    headers={"Content-Disposition": f'attachment; filename="pacs008_{reference_id}.xml"'})

@app.get("/iso/camt053.xml", tags=["iso20022"])
async def iso_camt(address: str):
    address = unquote(address)
    res = await validate_address(address)
    rwa_blk = get_rwa_assets(address)
    xml_bytes = xml_camt053(address=res.address, balance=res.total_balance,
                            risk=res.risk_score, rwa_block=rwa_blk)
    return Response(content=xml_bytes, media_type="application/xml",
                    headers={"Content-Disposition": f'attachment; filename="camt053_{res.address}.xml"'})

# --------------- Metrics ----------------
@app.get("/metrics", include_in_schema=False, tags=["system"])
async def metrics():
    content, content_type = get_metrics()
    return Response(content, media_type=content_type)

# --------------- Traction Endpoint ---------------
@app.get("/traction", tags=["system"])
async def traction():
    # Return total request count for UI
    from .metrics import REQ_COUNT
    count = 0
    for sample in REQ_COUNT.collect()[0].samples:
        count += sample.value
    return {"total_requests": int(count)}
