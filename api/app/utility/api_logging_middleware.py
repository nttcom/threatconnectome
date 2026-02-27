import json
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api_logger")
COMMON_API_LIST = ["update_user", "get_dependencies", "invited_pteam"]
UPLOAD_API_LIST = [
    "upload_service_thumbnail",
    "upload_pteam_sbom_file",
    "upload_pteam_packages_file",
]
AUTH_API_LIST = ["login_for_access_token", "refresh_access_token"]
CREATE_USER = "create_user"


class ApiLoggingMiddleware(BaseHTTPMiddleware):

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

        if endpoint_name in COMMON_API_LIST:
            self.create_log_for_common_api(request, response, body_bytes)
        elif endpoint_name in UPLOAD_API_LIST:
            self.create_log_for_upload_api(request, response)
        elif endpoint_name in AUTH_API_LIST:
            self.create_log_for_auth_api(request, response)
        elif endpoint_name == CREATE_USER:
            self.create_log_for_create_user(request, response, body_bytes)
        else:
            pass

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

    def create_log_for_upload_api(self, request: Request, response):
        user = getattr(request.state, "current_user", None)
        file_info = getattr(request.state, "file_info", {})
        log_dict = {
            "http_status": response.status_code,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "file_name": file_info.get("file_name", None),
            "file_size": f"{file_info['file_size']}byte" if "file_size" in file_info else None,
            "content_type": file_info.get("content_type", None),
            "uid": user.uid if user else None,
        }
        logger.info(json.dumps(log_dict))

    def create_log_for_create_user(self, request: Request, response, body_bytes):
        body = json.loads(body_bytes) if body_bytes else None
        log_dict = {
            "http_status": response.status_code,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "request_body": body,
            "uid": getattr(request.state, "uid", None),
        }
        logger.info(json.dumps(log_dict))

    def create_log_for_auth_api(self, request: Request, response):
        uid = getattr(request.state, "uid", None)
        log_dict = {
            "http_status": response.status_code,
            "method": request.method,
            "path": request.url.path,
            "uid": uid,
        }
        logger.info(json.dumps(log_dict))
