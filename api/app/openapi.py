from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute


def custom_openapi(original_app: FastAPI):
    """
    Generates a complete OpenAPI schema that includes paths with
    `include_in_schema=False` by merging public and internal routes.

    Args:
        original_app: The FastAPI application instance.

    Returns:
        The consolidated OpenAPI schema dictionary.
    """
    if original_app.extra.get("internal_openapi_schema"):
        return original_app.extra["internal_openapi_schema"]

    original_schema = get_openapi(
        title=original_app.title,
        version=original_app.version,
        routes=[r for r in original_app.routes if isinstance(r, BaseRoute)],
    )

    internal_app = FastAPI()
    internal_routes = [
        route
        for route in original_app.routes
        if isinstance(route, APIRoute) and not route.include_in_schema
    ]
    for internal_route in internal_routes:
        internal_app.router.routes.append(
            APIRoute(
                path=internal_route.path,
                endpoint=internal_route.endpoint,
                methods=internal_route.methods,
                response_model=internal_route.response_model,
                status_code=internal_route.status_code,
                tags=internal_route.tags,
                dependencies=internal_route.dependencies,
                summary=internal_route.summary,
                description=internal_route.description,
                include_in_schema=True,  # Force set to True
                operation_id=internal_route.operation_id,
            )
        )

    internal_schema = get_openapi(
        title=original_app.title,
        version=original_app.version,
        routes=[r for r in internal_app.routes if isinstance(r, BaseRoute)],
    )

    for path, methods_definition in internal_schema.get("paths", {}).items():
        if path in original_schema["paths"]:
            original_schema["paths"][path].update(methods_definition)
        else:
            original_schema["paths"][path] = methods_definition
    if "components" in internal_schema and "schemas" in internal_schema["components"]:
        original_schema.setdefault("components", {}).setdefault("schemas", {}).update(
            internal_schema["components"]["schemas"]
        )

    original_app.extra["internal_openapi_schema"] = original_schema
    return original_schema
