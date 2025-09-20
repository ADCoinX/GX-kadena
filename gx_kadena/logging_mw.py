import uuid
import logging
from fastapi import Request

logger = logging.getLogger("gx_kadena")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '{"ts":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s","request_id":"%(request_id)s"}'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    setattr(request.state, "request_id", request_id)
    logger.info("Request received", extra={"request_id": request_id})
    response = await call_next(request)
    logger.info("Request completed", extra={"request_id": request_id})
    return response