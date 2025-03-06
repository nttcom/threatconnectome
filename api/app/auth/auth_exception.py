import enum


class AuthErrorType(str, enum.Enum):
    UNAUTHORIZED = "unauthorized"
    INTERNAL_SERVER_ERROR = "internal_server_error"
    SERVICE_UNAVAILABLE = "service_unavailable"


class AuthException(Exception):
    def __init__(self, error_type: AuthErrorType, message: str):
        super().__init__()
        self.__error_type = error_type
        self.__message = message

    @property
    def error_type(self):
        return self.__error_type

    @property
    def message(self):
        return self.__message
