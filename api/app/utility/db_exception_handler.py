import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

# Seconds a client should wait before retrying (sent as the Retry-After header).
DB_UNAVAILABLE_RETRY_AFTER_SECONDS = 5
DB_UNAVAILABLE_DETAIL = "Database is temporarily unavailable. Please retry later."


async def db_operational_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Convert DB operational errors into 503 Service Unavailable.

    OperationalError covers connection and resource errors that are mostly transient,
    such as "server closed the connection unexpectedly", "SSL SYSCALL error: EOF detected",
    statement timeouts, deadlocks and serialization failures.
    Returning 503 with Retry-After tells clients that the request may succeed on retry,
    instead of an opaque 500.
    The session is rolled back and closed by get_db() when the exception propagates.

    Note: this handler is not applied to errors raised in background tasks, because the
    response has already been sent. Starlette re-raises such errors wrapped in RuntimeError
    ("Caught handled exception, but response already started.") with the original
    OperationalError as __cause__.
    """
    assert isinstance(exc, OperationalError)
    logger.error(
        "Database operational error: method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": DB_UNAVAILABLE_DETAIL},
        headers={"Retry-After": str(DB_UNAVAILABLE_RETRY_AFTER_SECONDS)},
    )
