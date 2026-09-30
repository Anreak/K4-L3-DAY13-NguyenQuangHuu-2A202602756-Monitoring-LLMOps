from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        clear_contextvars()

        supplied_id = request.headers.get("x-request-id", "")
        if len(supplied_id) == 12 and supplied_id.startswith("req-") and all(
            char in "0123456789abcdefABCDEF" for char in supplied_id[4:]
        ):
            correlation_id = supplied_id.lower()
        else:
            correlation_id = f"req-{uuid.uuid4().hex[:8]}"

        bind_contextvars(correlation_id=correlation_id)
        
        request.state.correlation_id = correlation_id
        
        start = time.perf_counter()
        response = await call_next(request)
        
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = f"{elapsed_ms:.2f}"
        
        return response
