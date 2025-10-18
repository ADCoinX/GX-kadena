import time
import datetime as dt
from typing import Optional, Tuple, Dict, List
import asyncio
import httpx

from .config import (
    # Expect these to exist in your config; see notes at bottom for defaults.
    KADENA_PACT_BASES,   # List[str] e.g. ["https://api.chainweb.com", ...]
    MAINNET,             # e.g. "mainnet01"
    CHAINS,              # e.g. range(20)
    API_TIMEOUT,         # e.g. 15.0
    KADINDEXER_BASE,     # e.g. "https://api.mainnet.kadindexer.io/v1"
    KADINDEXER_API_KEY,  # optional str or ""
)

# ---------------- Utils ----------------
def normalize_balance(val) -> float:
    """
    Normalize Pact balance response:
      - {"int": "100000000"} -> 100000000.0
      - "0.0" | 12345        -> float
      - invalid              -> 0.0
    """
    try:
        if isinstance(val, dict) and "int" in val:
            return float(val["int"])
        elif isinstance(val, (int, float, str)):
            # handle "1e8" gracefully
            return float(str(val))
    except Exception:
        return 0.0
    return 0.0


# ---------------- Pact Local ----------------
async def pact_local(
    client: httpx.AsyncClient,
    chain: int,
    code: str,
    data: dict | None = None,
    timeout: float = None,
) -> dict:
    """
    Stateless Pact local query with multi-base fallback.
    Returns {} on failure (does not raise), to keep the pipeline resilient.
    """
    payload = {
        "networkId": MAINNET,
        "payload": {"exec": {"code": code, "data": data or {}}},
        "signers": [],
        "meta": {
            "chainId": str(chain),
            "gasLimit": 150000,
            "gasPrice": 1e-6,
            "ttl": 600,
            "creationTime": int(time.time()),
        },
    }
    t = API_TIMEOUT if timeout is None else timeout

    # small retry loop per base (network blips)
    for base in KADENA_PACT_BASES:
        url = f"{base}/chainweb/0.0/{MAINNET}/chain/{chain}/pact/api/v1/local"
        for attempt in range(2):
            try:
                r = await client.post(url, json=payload, timeout=t)
                if r.status_code == 200:
                    return r.json() or {}
            except Exception as e:
                # debug only; keep stateless/no raise
                print(f"[pact_local] {url} attempt {attempt+1} error: {e}")
                await asyncio.sleep(0.15 * (attempt + 1))
        # try next base
    return {}


# ---------------- Balance (across all chains) ----------------
async def _balance_one_chain(
    client: httpx.AsyncClient,
    chain: int,
    address: str,
    sem: asyncio.Semaphore,
) -> tuple[int, float]:
    """
    Helper to fetch one chain balance under a semaphore.
    Returns (chain, balance_float)
    """
    code = f'(coin.get-balance "{address}")'
    async with sem:
        res = await pact_local(client, chain, code)
    val = normalize_balance(res.get("result", {}).get("data", 0))
    return chain, val


async def get_balance_any_chain(address: str) -> Tuple[float, Optional[int], Dict[int, float]]:
    """
    Get total KDA balance for an address across MAINNET chains.
    Parallelized with concurrency cap for stability. Stateless.
    Returns: (total_balance, first_chain_found_or_None, per_chain_dict)
    """
    total = 0.0
    found: Optional[int] = None
    per_chain: Dict[int, float] = {}

    # reasonable concurrency to avoid hammering nodes
    sem = asyncio.Semaphore(6)

    async with httpx.AsyncClient() as client:
        tasks: List[asyncio.Task] = [
            asyncio.create_task(_balance_one_chain(client, c, address, sem))
            for c in CHAINS
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            # ignore errors; stateless
            continue
        c, val = result
        if val > 0:
            per_chain[c] = val
            total += val
            if found is None:
                found = c

    # Optional: single-chain retry if everything zero (kept from your MVP)
    if total == 0.0 and 0 in list(CHAINS):
        try:
            async with httpx.AsyncClient() as client:
                res = await pact_local(client, 0, f'(coin.get-balance "{address}")')
            val = normalize_balance(res.get("result", {}).get("data", 0))
            if val > 0:
                per_chain[0] = val
                total = val
                found = 0
        except Exception as e:
            print(f"[get_balance_any_chain] Fallback chain 0 error: {e}")

    # Debug (stdout only; no file writes)
    print("[DEBUG] get_balance_any_chain total:", total)
    print("[DEBUG] get_balance_any_chain per_chain:", per_chain)
    print("[DEBUG] address:", address)

    return total, found, per_chain


# ---------------- Kadindexer v1 (GraphQL) ----------------
GQL_TX_QUERY = """
query($search: String!, $limit: Int!) {
  transactions(search: $search, limit: $limit) {
    edges {
      node {
        creationTime
      }
    }
  }
}
"""


async def get_tx_count_24h(address: str, limit: int = 200) -> Optional[int]:
    """
    Count transactions in the last 24 hours via Kadindexer v1 GraphQL.
    Respects KADINDEXER_BASE and optional KADINDEXER_API_KEY from .config.
    Returns int or None on transport error.
    """
    base = KADINDEXER_BASE.rstrip("/")
    headers = {"Content-Type": "application/json"}
    if KADINDEXER_API_KEY:
        headers["Authorization"] = f"Bearer {KADINDEXER_API_KEY}"

    payload = {
        "query": GQL_TX_QUERY,
        "variables": {"search": address, "limit": limit},
    }

    cutoff = dt.datetime.utcnow() - dt.timedelta(hours=24)

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(base, json=payload, headers=headers, timeout=API_TIMEOUT)
            if r.status_code != 200:
                print("[get_tx_count_24h] HTTP", r.status_code, r.text[:300])
                return None

            data = r.json()
            edges = data.get("data", {}).get("transactions", {}).get("edges", []) or []
            cnt = 0
            for e in edges:
                ts = (e or {}).get("node", {}).get("creationTime")
                if not ts:
                    continue
                try:
                    # ISO8601 Z → naive UTC
                    dt_obj = dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
                    if dt_obj >= cutoff:
                        cnt += 1
                except Exception:
                    continue
            return cnt
    except Exception as e:
        print("[get_tx_count_24h] Error:", e)
        return None


# ---------------- Contract detector (stub) ----------------
async def is_contract_address(address: str) -> Optional[bool]:
    """
    Stub for now (stateless). You can later upgrade by querying Pact for module
    definitions tied to the address if Kadena exposes a suitable primitive.
    """
    return False
