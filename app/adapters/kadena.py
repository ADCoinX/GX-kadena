"""Kadena adapter for address info (real explorer API)."""
import time
from app.services.http_fallback import try_sources

def get_tx_count(address: str) -> int:
    """Get Kadena tx count with failover."""
    sources = [
        f"https://explorer.chainweb.com/mainnet/account/{address}"
    ]
    data = try_sources(sources, {})
    return data.get("transactions", 0) if isinstance(data, dict) else 0

def get_address_age_days(address: str) -> int:
    """Get Kadena address age in days with failover."""
    sources = [
        f"https://explorer.chainweb.com/mainnet/account/{address}"
    ]
    data = try_sources(sources, {})
    if isinstance(data, dict) and "firstSeen" in data:
        first_seen = int(data["firstSeen"]) / 1000  # ms → s
        return int((time.time() - first_seen) / 86400)
    return 0
