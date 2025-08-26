"""Kadena adapter for address info (with fallback + {address} formatting)."""
import os
from app.services.http_fallback import try_sources

# Read from ENV (comma-separated). Example:
# KADENA_TX_SOURCES=https://explorer.chainweb.com/mainnet/account/{address},https://backup/api?address={address}
# KADENA_AGE_SOURCES=https://explorer.chainweb.com/mainnet/firstseen/{address},https://backup/api?address={address}
_TX = [s.strip() for s in os.getenv("KADENA_TX_SOURCES", "").split(",") if s.strip()]
_AGE = [s.strip() for s in os.getenv("KADENA_AGE_SOURCES", "").split(",") if s.strip()]

# Fallback defaults if ENV not provided
if not _TX:
    _TX = ["https://explorer.chainweb.com/mainnet/account/{address}"]
if not _AGE:
    _AGE = ["https://explorer.chainweb.com/mainnet/firstseen/{address}"]

def _fmt_sources(sources: list[str], address: str) -> list[str]:
    """Replace {address} placeholder if present; leave as-is otherwise."""
    out = []
    for s in sources:
        try:
            out.append(s.format(address=address))
        except Exception:
            # if source doesn't use {address}, keep original (some APIs use ?address= via try_sources params)
            out.append(s)
    return out

def get_tx_count(address: str) -> int:
    """Get Kadena tx count with failover."""
    # Address already formatted into URL; pass empty params to try_sources
    return try_sources(_fmt_sources(_TX, address), {})

def get_address_age_days(address: str) -> int:
    """Get Kadena address age in days with failover."""
    return try_sources(_fmt_sources(_AGE, address), {})
