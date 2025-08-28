"""GuardianX utility functions."""
from fastapi import HTTPException
import re

def validate_chain(chain: str) -> bool:
    """Validate chain name."""
    return chain.lower() in {"kadena", "xrpl"}

def validate_address(address: str) -> bool:
    """Validate address format for Kadena and XRPL."""
    # Kadena: k: + 64 hex
    if re.match(r"^k:[0-9a-fA-F]{64}$", address):
        return True
    # XRPL: r + 33-34 chars, typical XRPL format
    if re.match(r"^r[0-9a-zA-Z]{33,34}$", address):
        return True
    return False

def safe_raise(code: int, msg: str) -> None:
    """Raise safe HTTPException."""
    raise HTTPException(status_code=code, detail=msg)

