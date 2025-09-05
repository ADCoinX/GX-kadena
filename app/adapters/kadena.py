"""Kadena adapter for address info (real explorer API, all live data)."""
import time
from app.services.http_fallback import try_sources

def get_tx_count(address: str) -> int:
    """Get Kadena tx count with failover, sum from all chains (LIVE DATA)."""
    sources = [
        f"https://explorer.chainweb.com/mainnet/account/{address}"
    ]
    data = try_sources(sources, {})
    if isinstance(data, dict):
        if "chains" in data and isinstance(data["chains"], list):
            return sum(int(chain.get("transactions", 0)) for chain in data["chains"])
        elif "transactions" in data:
            return int(data.get("transactions", 0))
    return 0

def get_address_age_days(address: str) -> int:
    """Get Kadena address age in days (earliest firstSeen from all chains, LIVE DATA)."""
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
    """Get Kadena balance across all chains (LIVE DATA)."""
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
    Get number of unique related addresses (LIVE DATA).
    Will count unique addresses interacted with (senders/recipients) from all chain transactions.
    """
    sources = [
        f"https://explorer.chainweb.com/mainnet/account/{address}/transfers?size=1000"
    ]
    data = try_sources(sources, {})
    related_addresses = set()
    if isinstance(data, dict) and "transfers" in data and isinstance(data["transfers"], list):
        for tx in data["transfers"]:
            # Kadena explorer: each transfer should have from/to fields
            from_addr = tx.get("from")
            to_addr = tx.get("to")
            # Add only if not the current address
            if from_addr and from_addr != address:
                related_addresses.add(from_addr)
            if to_addr and to_addr != address:
                related_addresses.add(to_addr)
    return len(related_addresses)
