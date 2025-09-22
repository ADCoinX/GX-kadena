import time
import datetime as dt
from typing import Optional, Tuple, Dict
import httpx
import os

from .config import (
    KADENA_PACT_BASES, MAINNET, CHAINS, API_TIMEOUT, KADENA_EXPLORER_BASE,
    KADINDEXER_API_KEY, KADINDEXER_BASE
)

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
        except Exception:
            continue
    raise RuntimeError("All Pact endpoints failed")

async def get_balance_any_chain(address: str) -> Tuple[float, Optional[int], Dict[int, float]]:
    # --- USE KADINDEXER IF API KEY PRESENT ---
    if KADINDEXER_API_KEY:
        url = f"{KADINDEXER_BASE}account/{address}/balance"
        headers = {"x-api-key": KADINDEXER_API_KEY}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, headers=headers, timeout=API_TIMEOUT)
                if resp.status_code == 200:
                    data = resp.json()
                    # Assume API return: {"total": ..., "per_chain": {"0": val, ...}}
                    total = float(data.get("total", 0))
                    per_chain = {int(k): float(v) for k, v in data.get("per_chain", {}).items()}
                    found = next((c for c, v in per_chain.items() if v > 0), None)
                    return total, found, per_chain
        except Exception:
            pass  # fallback ke default public chainweb bawah

    # --- DEFAULT: PUBLIC CHAINWEB ---
    async with httpx.AsyncClient() as client:
        total = 0.0
        found = None
        per_chain = {}
        for c in CHAINS:
            code = f'(coin.get-balance "{address}")'
            try:
                res = await pact_local(client, c, code)
                val = res["result"]["data"]
                if isinstance(val, (int, float)) and val > 0:
                    per_chain[c] = float(val)
                    total += float(val)
                    if found is None:
                        found = c
            except Exception:
                continue
        # fallback: kalau semua chain 0, cuba chain 0
        if total == 0.0:
            try:
                res = await pact_local(client, 0, f'(coin.get-balance "{address}")')
                val = res["result"]["data"]
                total = float(val) if isinstance(val, (int, float)) else 0.0
                found = 0
                per_chain[0] = total
            except Exception:
                total = 0.0
                found = None
        return total, found, per_chain

async def get_tx_count_24h(address: str) -> Optional[int]:
    # --- USE KADINDEXER IF API KEY PRESENT ---
    if KADINDEXER_API_KEY:
        url = f"{KADINDEXER_BASE}account/{address}/txcount24h"
        headers = {"x-api-key": KADINDEXER_API_KEY}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, headers=headers, timeout=API_TIMEOUT)
                if resp.status_code == 200:
                    data = resp.json()
                    return int(data.get("txcount24h", 0))
        except Exception:
            pass  # fallback ke public explorer bawah

    # --- DEFAULT: PUBLIC EXPLORER ---
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
    except Exception:
        return None

async def is_contract_address(address: str) -> Optional[bool]:
    # MVP: always False (stub)
    return False
