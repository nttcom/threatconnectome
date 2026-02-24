import json
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api_logger")
endpoint_allow_list = ["update_user", "get_dependencies"]


class CustomMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        body = None
        if request.method == "PUT" or request.method == "POST":
            try:
                body_bytes = await request.body()
                body = json.loads(body_bytes) if body_bytes else None
            except Exception:
                body = "Binary or Unparseable Body"

        response = await call_next(request)
        route = request.scope.get("route")
        endpoint_name = getattr(route, "name", None) if route else None

        if endpoint_name in endpoint_allow_list:
            user = getattr(request.state, "current_user", None)
            uid = user.uid if user else None
            log_dict = {
                "http_status": response.status_code,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "request_body": body,
                "uid": uid,
            }
            logger.info(json.dumps(log_dict))

        return response
