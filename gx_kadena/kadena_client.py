import time
import datetime as dt
from typing import Optional, Tuple, Dict
import httpx

from .config import (
    KADENA_PACT_BASES, MAINNET, CHAINS, API_TIMEOUT, KADENA_EXPLORER_BASE,
    KADINDEXER_API_KEY, KADINDEXER_BASE
)

# --- Normalizer untuk balance ---
def normalize_balance(val) -> float:
    """
    Normalize Pact balance response:
    - {"int": "100000000"} -> 100000000.0
    - "0.0" -> 0.0
    - 12345 -> 12345.0
    - fail -> 0.0
    """
    try:
        if isinstance(val, dict) and "int" in val:
            return float(val["int"])
        elif isinstance(val, (int, float, str)):
            return float(val)
    except Exception:
        return 0.0
    return 0.0


async def pact_local(client: httpx.AsyncClient, chain: int, code: str, data: dict = None) -> dict:
    payload = {
        "networkId": MAINNET,
        "payload": {"exec": {"code": code, "data": data or {}}},
        "signers": [],
        "meta": {
            "chainId": str(chain),
            "gasLimit": 150000,
            "gasPrice": 1e-6,
            "ttl": 600,
            "creationTime": int(time.time())
        }
    }
    for base in KADENA_PACT_BASES:
        url = f"{base}/chainweb/0.0/{MAINNET}/chain/{chain}/pact/api/v1/local"
        try:
            r = await client.post(url, json=payload, timeout=API_TIMEOUT)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"[pact_local] Chain {chain} on {base} error: {e}")
            continue
    raise RuntimeError("All Pact endpoints failed")


async def get_balance_any_chain(address: str) -> Tuple[float, Optional[int], Dict[int, float]]:
    """
    Get total KDA balance for an address across all mainnet chains (0-19).
    Skips kadindexer, use direct Pact local calls.
    """
    total = 0.0
    found = None
    per_chain: Dict[int, float] = {}

    async with httpx.AsyncClient() as client:
        for c in range(20):  # Kadena mainnet chains: 0-19
            code = f'(coin.get-balance "{address}")'
            try:
                res = await pact_local(client, c, code)
                val = normalize_balance(res.get("result", {}).get("data", 0))
                if val > 0:
                    per_chain[c] = val
                    total += val
                    if found is None:
                        found = c
            except Exception as e:
                print(f"[get_balance_any_chain] Error fetching from chain {c}: {e}")
                continue

        # Fallback: retry chain 0 kalau semua balance kosong
        if total == 0.0:
            try:
                res = await pact_local(client, 0, f'(coin.get-balance "{address}")')
                val = normalize_balance(res.get("result", {}).get("data", 0))
                total = val
                found = 0 if val > 0 else None
                per_chain[0] = val
            except Exception as e:
                print(f"[get_balance_any_chain] Fallback chain 0 error: {e}")
                total = 0.0
                found = None

    # Debug log
    print("DEBUG get_balance_any_chain total:", total)
    print("DEBUG get_balance_any_chain per_chain:", per_chain)
    print("DEBUG address:", address)

    return total, found, per_chain


async def get_tx_count_24h(address: str) -> Optional[int]:
    url = f"{KADENA_EXPLORER_BASE}/transactions?search={address}&limit=200"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=API_TIMEOUT)
            if r.status_code != 200:
                return None
            data = r.json()
            items = data.get("items", [])
            cutoff = dt.datetime.utcnow() - dt.timedelta(hours=24)
            cnt = 0
            for it in items:
                ts = it.get("creationTime") or it.get("timestamp")
                if ts is None:
                    continue
                if isinstance(ts, str) and ts.isdigit():
                    ts = int(ts)
                if isinstance(ts, float):
                    ts = int(ts)
                if isinstance(ts, int):
                    dt_obj = dt.datetime.utcfromtimestamp(ts)
                else:
                    try:
                        dt_obj = dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
                    except Exception:
                        continue
                if dt_obj >= cutoff:
                    cnt += 1
            return cnt
    except Exception as e:
        print(f"[get_tx_count_24h] Error: {e}")
        return None


async def is_contract_address(address: str) -> Optional[bool]:
    # MVP: always False (stub)
    return False
