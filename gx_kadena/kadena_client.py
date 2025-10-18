# gx_kadena/kadena_client.py
# (Only the file is shown here. Replace the existing file with this content.)

import time
import datetime as dt
from typing import Optional, Tuple, Dict
import httpx
import os
import traceback
import json

from .config import (
    KADENA_PACT_BASES, MAINNET, CHAINS, API_TIMEOUT, KADENA_EXPLORER_BASE,
    KADINDEXER_API_KEY, KADINDEXER_BASE
)

# Simple in-memory TTL cache to reduce repeated calls when nodes are slow/blocked.
_BALANCE_CACHE_TTL = int(os.getenv("BALANCE_CACHE_TTL", "20"))  # seconds
_balance_cache: Dict[str, tuple] = {}  # address -> (ts, total, found, per_chain)

def normalize_balance(val) -> float:
    """
    Normalize many Pact responses:
      - {"int": "100000000"} -> 100000000.0
      - "0.0" | 12345 -> float
      - invalid -> 0.0
    """
    try:
        if isinstance(val, dict) and "int" in val:
            return float(val["int"])
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            return float(val)
    except Exception:
        return 0.0
    return 0.0

async def pact_local(client: httpx.AsyncClient, chain: int, code: str, data: dict = None, base: str = None, timeout: float = None) -> dict:
    """
    Stateless Pact local query with multi-base fallback and payload-format retries.
    Returns {} on failure (does not raise) to keep callers resilient.
    This function will:
      1) try the 'payload' wrapper format
      2) if 400 mentioning missing 'cmd', retry with {"cmd": payload}
      3) if still failing, retry with {"cmd": json.dumps(payload)}
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
            "creationTime": int(time.time())
        }
    }
    t = API_TIMEOUT if timeout is None else timeout
    bases = [base] if base else KADENA_PACT_BASES

    for b in bases:
        url = f"{b}/chainweb/0.0/{MAINNET}/chain/{chain}/pact/api/v1/local"

        # Attempt 1: standard payload format (existing)
        try:
            r = await client.post(url, json=payload, timeout=t)
            if r.status_code == 200:
                return r.json()
            # Log the response body for diagnosis
            body = (r.text or "")[:1000]
            print(f"[pact_local] Non-200 from {url}: {r.status_code} {body}")
            # If server complains about missing "cmd", we'll try alternative formats below
            if r.status_code == 400 and "cmd" in body:
                pass  # fall through to retry attempts
            else:
                # For other non-200 responses, still attempt alternative formats occasionally
                # but continue to next base after retries below.
                pass
        except Exception as e:
            print(f"[pact_local] {url} error (attempt 1): {repr(e)}")
            traceback.print_exc()

        # Attempt 2: wrap full payload under "cmd" key (some proxies expect this)
        try:
            alt = {"cmd": payload}
            r2 = await client.post(url, json=alt, timeout=t)
            if r2.status_code == 200:
                return r2.json()
            body2 = (r2.text or "")[:1000]
            print(f"[pact_local] Non-200 alt1 from {url}: {r2.status_code} {body2}")
            # if 200 not returned, continue to attempt 3
        except Exception as e:
            print(f"[pact_local] {url} error (attempt 2): {repr(e)}")
            traceback.print_exc()

        # Attempt 3: some gateways expect stringified cmd
        try:
            alt2 = {"cmd": json.dumps(payload)}
            r3 = await client.post(url, json=alt2, timeout=t)
            if r3.status_code == 200:
                return r3.json()
            body3 = (r3.text or "")[:1000]
            print(f"[pact_local] Non-200 alt2 from {url}: {r3.status_code} {body3}")
        except Exception as e:
            print(f"[pact_local] {url} error (attempt 3): {repr(e)}")
            traceback.print_exc()

        # if reached here, this base failed all attempts — continue to next base
    # Return empty to signal failure gracefully (don't raise)
    return {}

async def _get_balance_from_nodes(address: str) -> Tuple[float, Optional[int], Dict[int, float]]:
    """
    Try direct node calls across chains. Returns total, found, per_chain.
    Does NOT use kadindexer. Caller can fallback to kadindexer if needed.
    """
    total = 0.0
    found = None
    per_chain: Dict[int, float] = {}
    async with httpx.AsyncClient() as client:
        code = f'(coin.get-balance "{address}")'
        for c in CHAINS:
            try:
                res = await pact_local(client, c, code)
                if not res:
                    continue
                val = res.get("result", {}).get("data") if isinstance(res, dict) else None
                val_f = normalize_balance(val)
                if val_f and val_f > 0:
                    per_chain[c] = float(val_f)
                    total += float(val_f)
                    if found is None:
                        found = c
            except Exception as e:
                print(f"[get_balance_any_chain] Error fetching chain {c}: {repr(e)}")
                traceback.print_exc()
                continue
    return total, found, per_chain

async def get_balance_any_chain(address: str) -> Tuple[float, Optional[int], Dict[int, float]]:
    """
    Public function to get total balance. Tries (1) cache, (2) direct nodes, (3) kadindexer fallback.
    Returns (total, chain_found, per_chain_dict).
    """
    now = int(time.time())
    cached = _balance_cache.get(address)
    if cached:
        ts, total, found, per_chain = cached
        if now - ts < _BALANCE_CACHE_TTL:
            print(f"[cache] hit for {address} total={total}")
            return total, found, per_chain
        else:
            _balance_cache.pop(address, None)

    # 1) Try direct nodes
    total, found, per_chain = await _get_balance_from_nodes(address)
    if total > 0.0:
        _balance_cache[address] = (now, total, found, per_chain)
        print("[get_balance_any_chain] direct node success", total, per_chain)
        return total, found, per_chain

    # 2) Fallback to Kadindexer if API key provided
    if KADINDEXER_API_KEY:
        url = f"{KADINDEXER_BASE}account/{address}/balance"
        headers = {"x-api-key": KADINDEXER_API_KEY}
        try:
            async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    total = float(data.get("total", 0) or 0)
                    per_chain = {int(k): float(v) for k, v in (data.get("per_chain") or {}).items()}
                    found = next((c for c, v in per_chain.items() if v > 0), None)
                    _balance_cache[address] = (now, total, found, per_chain)
                    print("[get_balance_any_chain] kadindexer fallback total", total)
                    return total, found, per_chain
                else:
                    print("[get_balance_any_chain] kadindexer status", resp.status_code, resp.text[:200])
        except Exception as e:
            print("[get_balance_any_chain] kadindexer error", repr(e))
            traceback.print_exc()

    # 3) Nothing found — cache zero briefly to avoid hammer
    _balance_cache[address] = (now, 0.0, None, {})
    return 0.0, None, {}

async def get_tx_count_24h(address: str) -> Optional[int]:
    """
    Try Kadindexer first (if available), else explorer. Handle 403 and JSON errors gracefully.
    """
    # Kadindexer preferred for tx counts
    if KADINDEXER_API_KEY:
        url = f"{KADINDEXER_BASE}account/{address}/txcount24h"
        headers = {"x-api-key": KADINDEXER_API_KEY}
        try:
            async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return int(data.get("txcount24h", 0))
                else:
                    print("[get_tx_count_24h] kadindexer status", resp.status_code, resp.text[:200])
        except Exception as e:
            print("[get_tx_count_24h] kadindexer error", repr(e))
            traceback.print_exc()

    # Fallback: public explorer (legacy). Some explorer endpoints may return non-JSON / 403.
    url = f"{KADENA_EXPLORER_BASE}/transactions?search={address}&limit=200"
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            r = await client.get(url)
            if r.status_code != 200:
                print(f"[get_tx_count_24h] explorer status {r.status_code} {r.text[:200]}")
                return None
            # Defensive JSON parse
            try:
                data = r.json()
            except Exception as e:
                print("[get_tx_count_24h] explorer json error", repr(e))
                return None
            items = data.get("items", []) if isinstance(data, dict) else []
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
        print("[get_tx_count_24h] HTTP error", repr(e))
        traceback.print_exc()
        return None

async def is_contract_address(address: str) -> Optional[bool]:
    # MVP: always False (stub). Could be extended to check registry via kadindexer.
    return False
