import time
from app.services.http_fallback import try_sources

def get_tx_count(address: str) -> int:
    """Get Kadena tx count with failover, sum from all chains."""
    sources = [
        f"https://explorer.chainweb.com/mainnet/account/{address}"
    ]
    data = try_sources(sources, {})
    if isinstance(data, dict) and "chains" in data:
        return sum(chain.get("transactions", 0) for chain in data["chains"])
    elif isinstance(data, dict) and "transactions" in data:
        return data.get("transactions", 0)
    return 0

def get_address_age_days(address: str) -> int:
    """Get Kadena address age in days (earliest firstSeen from all chains)."""
    sources = [
        f"https://explorer.chainweb.com/mainnet/account/{address}"
    ]
    data = try_sources(sources, {})
    first_seen_list = []
    if isinstance(data, dict) and "chains" in data:
        for chain in data["chains"]:
            if "firstSeen" in chain:
                first_seen_list.append(int(chain["firstSeen"]))
    elif isinstance(data, dict) and "firstSeen" in data:
        first_seen_list.append(int(data["firstSeen"]))
    if first_seen_list:
        earliest = min(first_seen_list) / 1000  # ms → s
        return int((time.time() - earliest) / 86400)
    return 0

def get_balance(address: str) -> float:
    """Get Kadena balance across all chains."""
    sources = [
        f"https://explorer.chainweb.com/mainnet/account/{address}"
    ]
    data = try_sources(sources, {})
    total = 0.0
    if isinstance(data, dict) and "chains" in data:
        for chain in data["chains"]:
            total += float(chain.get("balance", 0))
    elif isinstance(data, dict) and "balance" in data:
        total = float(data.get("balance", 0))
    return total
