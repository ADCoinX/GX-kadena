"""Failover HTTP client with retry, timeout, simple circuit, and TTL cache."""
import os, time, json, httpx
from typing import Any, Iterable, Optional

# Tunable via ENV
TIMEOUT = float(os.getenv("REQUEST_TIMEOUT_SEC", "4"))
RETRY_PER_SOURCE = int(os.getenv("RETRY_PER_SOURCE", "1"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

_cache: dict[str, tuple[int, float]] = {}   # key -> (val, ts)

# keys lazim dari explorer / API
POSSIBLE_KEYS = ["value", "txCount", "tx_count", "count",
                 "firstSeen", "first_seen", "ageDays", "age_days", "age", "days"]

def _extract_int(x: Any) -> Optional[int]:
    """Cuba dapatkan integer dari pelbagai bentuk JSON."""
    if x is None:
        return None
    if isinstance(x, bool):
        return int(x)
    if isinstance(x, (int, float)):
        return int(x)
    if isinstance(x, str):
        # cuba parse nombor yang muncul
        digits = "".join(ch for ch in x if ch.isdigit())
        return int(digits) if digits else None
    if isinstance(x, list):
        # ramai explorer pulangkan senarai tx → guna panjang
        return len(x)
    if isinstance(x, dict):
        # direct keys
        for k in POSSIBLE_KEYS:
            if k in x:
                got = _extract_int(x[k])
                if got is not None:
                    return got
        # cuba selongkar nested
        for v in x.values():
            got = _extract_int(v)
            if got is not None:
                return got
    return None

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

def try_sources(sources: list[str], params: dict, ttl: int = 900) -> int:
    """
    Cuba sumber-sumber dengan fallback + cache.
    - `sources`: senarai URL; boleh mengandungi {address} yang telah diformat di adapter,
                 atau guna `params={'address': 'k:...'}` kalau API perlukan query.
    - return integer (0 jika semua gagal).
    """
    # Cache key unik ikut URL list + params
    cache_key = json.dumps({"s": sources, "p": params}, sort_keys=True)
    now = time.time()
    if cache_key in _cache:
        val, ts = _cache[cache_key]
        if now - ts < ttl:
            return val

    for raw in sources:
        url = raw  # andaian adapter dah format {address} kalau perlu
        for _ in range(max(1, RETRY_PER_SOURCE)):
            try:
                data = _get_json(url, params)
                if data is None:
                    continue
                val = _extract_int(data)
                if val is not None:
                    _cache[cache_key] = (int(val), now)
                    return int(val)
            except Exception as e:
                if DEBUG:
                    print(f"[fallback] {url} exception: {e}")
                continue
        # kecilkan beban sebelum cuba source seterusnya
        time.sleep(0.05)

    # semua gagal
    _cache[cache_key] = (0, now)
    return 0
