from fastapi import HTTPException, status

from app.auth.auth_exception import AuthErrorType, AuthException


def get_status_code(error_type: AuthErrorType):
    match error_type:
        case AuthErrorType.UNAUTHORIZED:
            return status.HTTP_401_UNAUTHORIZED
        case AuthErrorType.INTERNAL_SERVER_ERROR:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        case AuthErrorType.SERVICE_UNAVAILABLE:
            return status.HTTP_503_SERVICE_UNAVAILABLE


def create_http_exception(auth_exception: AuthException) -> HTTPException:
    return HTTPException(
        status_code=get_status_code(auth_exception.error_type),
        detail=auth_exception.message,
        headers={"WWW-Authenticate": "Bearer"},
    )
