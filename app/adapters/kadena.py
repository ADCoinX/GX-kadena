"""Kadena adapter for address info (real explorer API)."""
import time
from app.services.http_fallback import try_sources

def get_tx_count(address: str) -> int:
    """Get Kadena tx count with failover, sum from all chains."""
    sources = [
        f"https://explorer.chainweb.com/mainnet/account/{address}"
    ]
    data = try_sources(sources, {})
    if isinstance(data, dict):
        # If multiple chains
        if "chains" in data and isinstance(data["chains"], list):
            return sum(int(chain.get("transactions", 0)) for chain in data["chains"])
        # If single chain or no chains key
        elif "transactions" in data:
            return int(data.get("transactions", 0))
    return 0

def get_address_age_days(address: str) -> int:
    """Get Kadena address age in days (earliest firstSeen from all chains)."""
    sources = [
        f"https://explorer.chainweb.com/mainnet/account/{address}"
    ]
    data = try_sources(sources, {})
    first_seen_list = []
    if isinstance(data, dict):
        if "chains" in data and isinstance(data["chains"], list):
            for chain in data["chains"]:
                if "firstSeen" in chain:
                    try:
                        first_seen_list.append(int(chain["firstSeen"]))
                    except Exception:
                        continue
        elif "firstSeen" in data:
            try:
                first_seen_list.append(int(data["firstSeen"]))
            except Exception:
                pass
    if first_seen_list:
        earliest = min(first_seen_list) / 1000  # ms → s
        return max(0, int((time.time() - earliest) / 86400))
    return 0

def get_balance(address: str) -> float:
    """Get Kadena balance across all chains."""
    sources = [
        f"https://explorer.chainweb.com/mainnet/account/{address}"
    ]
    data = try_sources(sources, {})
    total = 0.0
    if isinstance(data, dict):
        if "chains" in data and isinstance(data["chains"], list):
            for chain in data["chains"]:
                try:
                    total += float(chain.get("balance", 0))
                except Exception:
                    continue
        elif "balance" in data:
            try:
                total = float(data.get("balance", 0))
            except Exception:
                pass
    return total

def get_related_address_count(address: str) -> int:
    """
    Dummy implementation: Kadena explorer API does not directly provide related address count.
    You may implement logic based on transaction history, or return 0 for now.
    """
    # TODO: Replace this with real logic if you have another API/source.
    return 0
