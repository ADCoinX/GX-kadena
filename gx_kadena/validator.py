import datetime as dt
import time
from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel, Field
from .kadena_client import get_balance_any_chain, get_tx_count_24h, is_contract_address
from .risk import risk_score

class ValidationResult(BaseModel):
    address: str
    chain_found: Optional[int] = None
    balance: float
    total_balance: float
    balances_per_chain: Optional[Dict[int, float]] = None
    tx_total_24h: Optional[int] = None
    is_contract: Optional[bool] = None
    risk_score: int
    flags: List[str]
    duration_ms: int
    timestamp: dt.datetime = Field(default_factory=lambda: dt.datetime.utcnow())

def is_kadena_address(addr: str) -> bool:
    # Strict: valid "k:<hex>" or 64/66/68 chars of hex (no "k:")
    if addr.startswith("k:") and len(addr) == 66:
        return True
    if len(addr) in (64, 66, 68):
        try:
            int(addr.replace("k:", ""), 16)
            return True
        except Exception:
            return False
    return False

async def validate_address(address: str) -> ValidationResult:
    if not is_kadena_address(address):
        raise ValueError("Invalid Kadena address format")
    t0 = time.time()
    # Get total balance, chain_found (first found chain), and per-chain balances
    total_balance, chain_found, balances_per_chain = await get_balance_any_chain(address)
    tx24 = await get_tx_count_24h(address)
    isct = await is_contract_address(address)
    score, flags = risk_score(total_balance, tx24, isct)
    dur = int((time.time() - t0) * 1000)
    # Defensive: If balances_per_chain is None or empty, force dict and balance = 0.0
    if not balances_per_chain:
        balances_per_chain = {}
    balance = 0.0
    if chain_found is not None and chain_found in balances_per_chain:
        balance = balances_per_chain[chain_found]
    # Debug print for troubleshooting
    print("DEBUG ValidationResult:", {
        "address": address,
        "chain_found": chain_found,
        "balance": balance,
        "total_balance": total_balance,
        "balances_per_chain": balances_per_chain,
        "tx_total_24h": tx24,
        "is_contract": isct,
        "risk_score": score,
        "flags": flags,
        "duration_ms": dur,
    })
    return ValidationResult(
        address=address,
        chain_found=chain_found,
        balance=balance,
        total_balance=total_balance,
        balances_per_chain=balances_per_chain,
        tx_total_24h=tx24,
        is_contract=isct,
        risk_score=score,
        flags=flags,
        duration_ms=dur,
    )
