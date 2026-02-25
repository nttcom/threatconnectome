import json
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api_logger")
common_api_list = ["update_user", "get_dependencies"]
upload_api_list = [
    "upload_service_thumbnail",
    "upload_pteam_sbom_file",
    "upload_pteam_packages_file",
]
auth_api_list = ["login_for_access_token", "refresh_access_token"]


class CustomMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        body_bytes = None
        if request.headers.get("content-type", "").startswith("application/json"):
            try:
                body_bytes = await request.body()
            except Exception:
                body_bytes = None

        response = await call_next(request)
        route = request.scope.get("route")
        endpoint_name = getattr(route, "name", None) if route else None

        match endpoint_name:
            case _endpoint_name if _endpoint_name in common_api_list:
                self.create_log_for_common_api(request, response, body_bytes)
                return response
            case _endpoint_name if _endpoint_name in upload_api_list:
                return response
            case _endpoint_name if _endpoint_name in auth_api_list:
                return response
            case "invited_pteam":
                return response
            case "create_user":
                return response
            case __:
                return response

    def create_log_for_common_api(self, request: Request, response, body_bytes):
        user = getattr(request.state, "current_user", None)
        uid = user.uid if user else None
        body = json.loads(body_bytes) if body_bytes else None
        log_dict = {
            "http_status": response.status_code,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "request_body": body,
            "uid": uid,
        }
        logger.info(json.dumps(log_dict))
