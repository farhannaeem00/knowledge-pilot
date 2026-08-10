"""
Attaches a unique request_id to every incoming request and echoes it back
in the response header. Combined with structured logging, this lets you
trace a single request across logs — essential once there are background
jobs (Celery) and multiple services involved later.
"""
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
