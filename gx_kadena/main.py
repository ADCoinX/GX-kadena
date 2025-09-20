from fastapi import FastAPI, Request, Response, HTTPException
import datetime as dt
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

@app.get("/health")
async def health():
    return {"status": "ok", "ts": dt.datetime.utcnow().isoformat() + "Z"}

@app.get("/validate/{address}", response_model=ValidationResult)
async def validate(address: str):
    try:
        return await validate_address(address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/risk/{address}")
async def risk_endpoint(address: str):
    res = await validate_address(address)
    return {"address": res.address, "risk_score": res.risk_score, "flags": res.flags}

@app.get("/rwa/{address}")
async def rwa(address: str):
    return get_rwa_assets(address)

@app.get("/iso/pacs008.xml")
async def iso_pacs(address: str, reference_id: str = "GX-TEST-001", amount: str = "0.00", ccy: str = "KDA"):
    res = await validate_address(address)
    rwa_blk = get_rwa_assets(address)
    xml_bytes = xml_pacs008(address=res.address, ref_id=reference_id, amt=amount, ccy=ccy, risk=res.risk_score, rwa_block=rwa_blk)
    return Response(content=xml_bytes, media_type="application/xml",
                    headers={"Content-Disposition": f'attachment; filename="pacs008_{reference_id}.xml"'})

@app.get("/iso/camt053.xml")
async def iso_camt(address: str):
    res = await validate_address(address)
    rwa_blk = get_rwa_assets(address)
    xml_bytes = xml_camt053(address=res.address, balance=res.total_balance, risk=res.risk_score, rwa_block=rwa_blk)
    return Response(content=xml_bytes, media_type="application/xml",
                    headers={"Content-Disposition": f'attachment; filename="camt053_{res.address}.xml"'})

@app.get("/metrics")
async def metrics():
    content, content_type = get_metrics()
    return Response(content, media_type=content_type)