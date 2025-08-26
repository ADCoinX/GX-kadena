"""GuardianX utility functions."""
from fastapi import HTTPException
import re

def validate_chain(chain: str) -> bool:
    """Validate chain name."""
    return chain.lower() in {"kadena", "xrpl"}

def validate_address(address: str) -> bool:
    """Validate address format (very basic for Kadena/XRPL)."""
    return bool(re.match(r"^[a-zA-Z0-9]{32,64}$", address))

def safe_raise(code: int, msg: str) -> None:
    """Raise safe HTTPException."""
    raise HTTPException(status_code=code, detail=msg)