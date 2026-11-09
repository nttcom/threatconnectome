import json
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api_logger")

UPLOAD_API_LIST = [
    "upload_service_thumbnail",
    "upload_pteam_sbom_file",
    "upload_pteam_packages_file",
]
AUTH_API_LIST = ["login_for_access_token", "refresh_access_token"]
CREATE_USER = "create_user"
INVALID_JSON_BODY = "<invalid json>"


def _parse_body(body_bytes: bytes | None):
    if not body_bytes:
        return None
    try:
        return json.loads(body_bytes)
    except ValueError:  # includes json.JSONDecodeError and UnicodeDecodeError
        # Malformed bodies (e.g. from scanners) are common; keep the access log without a traceback.
        return INVALID_JSON_BODY


class ApiLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        body_bytes = None
        if request.headers.get("content-type", "").startswith("application/json"):
            try:
                body_bytes = await request.body()
            except Exception:
                body_bytes = None

        response = await call_next(request)

        # Logging must never change the API response.
        try:
            self.create_log(request, response, body_bytes)
        except Exception:
            logger.exception(
                "Failed to write API log: method=%s path=%s", request.method, request.url.path
            )

        return response

    def create_log(self, request: Request, response, body_bytes):
        route = request.scope.get("route")
        endpoint_name = getattr(route, "name", None) if route else None

        if endpoint_name in UPLOAD_API_LIST:
            self.create_log_for_upload_api(request, response)
        elif endpoint_name in AUTH_API_LIST:
            self.create_log_for_auth_api(request, response)
        elif endpoint_name == CREATE_USER:
            self.create_log_for_create_user(request, response, body_bytes)
        else:
            self.create_log_for_common_api(request, response, body_bytes)

    def create_log_for_common_api(self, request: Request, response, body_bytes):
        body = _parse_body(body_bytes)
        log_dict = {
            "http_status": response.status_code,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "request_body": body,
            "uid": getattr(request.state, "uid", None),
        }
        logger.info(json.dumps(log_dict))

    def create_log_for_upload_api(self, request: Request, response):
        file_info = getattr(request.state, "file_info", {})
        log_dict = {
            "http_status": response.status_code,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "file_name": file_info.get("file_name", None),
            "file_size": f"{file_info['file_size']}byte" if "file_size" in file_info else None,
            "content_type": file_info.get("content_type", None),
            "uid": getattr(request.state, "uid", None),
        }
        logger.info(json.dumps(log_dict))

    def create_log_for_create_user(self, request: Request, response, body_bytes):
        body = _parse_body(body_bytes)
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
