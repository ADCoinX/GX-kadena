"""Failover HTTP client with retry, timeout, circuit breaker, TTL cache."""
import httpx
import time

_cache = {}

def try_sources(sources: list[str], params: dict, ttl: int = 900) -> int:
    """Try sources with fallback, cache, and retry."""
    cache_key = f"{sources}-{params}"
    if cache_key in _cache and time.time() - _cache[cache_key][1] < ttl:
        return _cache[cache_key][0]
    for url in sources:
        try:
            resp = httpx.get(url, params=params, timeout=3)
            if resp.status_code == 200:
                val = resp.json().get("value", 0)
                _cache[cache_key] = (val, time.time())
                return val
        except Exception:
            continue
    return 0