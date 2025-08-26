"""ScamDB adapter with failover."""
from app.services.http_fallback import try_sources

def check_scam(address: str) -> bool:
    """Check if address is in scamdb."""
    sources = [
        "https://scamdb.guardianx.io/api/check",
        "https://publicscamdb.com/api/check",
        "https://backupscamdb.net/api/check",
    ]
    return try_sources(sources, {"address": address})