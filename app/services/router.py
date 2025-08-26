"""GuardianX API router."""
from fastapi import APIRouter, Request, Response, status
from app.models import ValidationResult
from app.services.risk_engine import risk_score
from app.services.iso20022 import export_iso
from app.services.rwa_checker import check_rwa
from app.settings import settings
from app.utils import validate_chain, validate_address, safe_raise
from app.services.model_loader import is_loaded
import time

router = APIRouter()

@router.get("/health", response_model=dict)
async def health():
    """Health check endpoint."""
    return {
        "ok": True,
        "model_loaded": is_loaded(),
        "db": True,
    }

@router.post("/validate", response_model=ValidationResult)
async def validate(request: Request):
    """Validate chain address for risk."""
    payload = await request.json()
    chain = payload.get("chain", "")
    address = payload.get("address", "")
    check_rwa_flag = payload.get("check_rwa", False)
    if not validate_chain(chain):
        safe_raise(400, "Invalid chain")
    if not validate_address(address):
        safe_raise(400, "Invalid address")
    score, flags, _ = risk_score(chain, address)
    rwa_check = check_rwa(address) if check_rwa_flag else {}
    sources = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "chain": chain}
    iso_xml = export_iso(chain, address, score, flags, settings.MODEL_VERSION, sources, rwa_check)
    result = ValidationResult(
        score=score,
        flags=flags,
        rwa_check=rwa_check,
        iso_xml=iso_xml,
        model_version=settings.MODEL_VERSION,
        data_sources_used=sources,
    )
    return result

@router.get("/iso/export")
async def iso_export(chain: str, address: str, check_rwa: bool = False):
    """Export ISO20022 XML for address."""
    if not validate_chain(chain):
        safe_raise(400, "Invalid chain")
    if not validate_address(address):
        safe_raise(400, "Invalid address")
    score, flags, _ = risk_score(chain, address)
    rwa_check = check_rwa(address) if check_rwa else {}
    sources = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "chain": chain}
    xml = export_iso(chain, address, score, flags, settings.MODEL_VERSION, sources, rwa_check)
    return Response(content=xml, media_type="application/xml", status_code=status.HTTP_200_OK)