from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQ_COUNT = Counter("gx_requests_total", "Total requests", ["path"])
LATENCY = Histogram("gx_latency_seconds", "Request latency", ["path"])

async def metrics_mw(request, call_next):
    import time
    start = time.time()
    resp = await call_next(request)
    LATENCY.labels(request.url.path).observe(time.time() - start)
    REQ_COUNT.labels(request.url.path).inc()
    return resp

def get_metrics():
    return generate_latest(), CONTENT_TYPE_LATEST