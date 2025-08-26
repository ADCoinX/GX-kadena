"""Failover HTTP client with retry, timeout, TTL cache (tx/age modes)."""
import os, time, json, httpx
from typing import Any, Optional
from datetime import datetime, timezone

# Tunable via ENV
TIMEOUT = float(os.getenv("REQUEST_TIMEOUT_SEC", "4"))
RETRY_PER_SOURCE = int(os.getenv("RETRY_PER_SOURCE", "1"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

_cache: dict[str, tuple[int, float]] = {}   # key -> (val, ts)

def _to_int(v: Any) -> Optional[int]:
    if v is None: return None
    if isinstance(v, bool): return int(v)
    if isinstance(v, (int, float)): return int(v)
    if isinstance(v, str):
        s = "".join(ch for ch in v if ch.isdigit())
        return int(s) if s else None
    return None

def _age_days_from_first_seen(v: Any) -> Optional[int]:
    # support ISO string "2023-01-01T..." or epoch ms/seconds
    try:
        if isinstance(v, (int, float)):  # epoch ms or s
            ts = float(v) / (1000.0 if v > 10_000_000_000 else 1.0)
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        elif isinstance(v, str):
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        else:
            return None
        days = (datetime.now(timezone.utc) - dt).days
        return max(days, 0)
    except Exception:
        return None

def _extract_tx_count(obj: Any) -> Optional[int]:
    # common: txCount / transactions / count / list length
    if obj is None: return None
    if isinstance(obj, list): return len(obj)
    if isinstance(obj, dict):
        for k in ("txCount", "transactions", "tx_count", "count"):
            if k in obj:
                n = _to_int(obj[k])
                if n is not None: return n
        # dive shallow
        for v in obj.values():
            n = _extract_tx_count(v)
            if n is not None: return n
    # primitives
    return _to_int(obj)

def _extract_age_days(obj: Any) -> Optional[int]:
    if obj is None: return None
    if isinstance(obj, dict):
        for k in ("firstSeen", "first_seen", "ageDays", "age_days", "age", "days"):
            if k in obj:
                n = _age_days_from_first_seen(obj[k]) if "first" in k else _to_int(obj[k])
                if n is not None: return n
        # dive shallow
        for v in obj.values():
            n = _extract_age_days(v)
            if n is not None: return n
    # primitives (already days)
    return _to_int(obj)

def _get_json(url: str, params: dict) -> Optional[Any]:
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.get(url, params=params)
        if 200 <= r.status_code < 300:
            try:
                return r.json()
            except Exception:
                return None
        if DEBUG:
            print(f"[fallback] {url} -> status {r.status_code}")
    return None

def try_sources(sources: list[str], params: dict, ttl: int = 900, mode: str = "tx") -> int:
    """
    mode="tx"  -> extract transaction count
    mode="age" -> extract age in days (from firstSeen/age* fields)
    """
    cache_key = json.dumps({"s": sources, "p": params, "m": mode}, sort_keys=True)
    now = time.time()
    if cache_key in _cache and now - _cache[cache_key][1] < ttl:
        return _cache[cache_key][0]

    extractor = _extract_tx_count if mode == "tx" else _extract_age_days

    for raw in sources:
        url = raw
        for _ in range(max(1, RETRY_PER_SOURCE)):
            try:
                data = _get_json(url, params)
                if data is None:
                    continue
                val = extractor(data)
                if val is not None:
                    val = int(val)
                    _cache[cache_key] = (val, now)
                    return val
            except Exception as e:
                if DEBUG:
                    print(f"[fallback] {url} exception: {e}")
                continue
        time.sleep(0.05)

    _cache[cache_key] = (0, now)
    return 0
