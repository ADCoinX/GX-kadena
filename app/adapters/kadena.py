"""Kadena adapter for address info."""
from app.services.http_fallback import try_sources

def get_tx_count(address: str) -> int:
    """Get Kadena tx count with failover."""
    sources = ["https://api.chainweb.com/kadena/txcount"]
    return try_sources(sources, {"address": address})

def get_address_age_days(address: str) -> int:
    """Get Kadena address age in days with failover."""
    sources = ["https://api.chainweb.com/kadena/addressage"]
    return try_sources(sources, {"address": address})