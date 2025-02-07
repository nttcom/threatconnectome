from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

token_scheme = HTTPBearer(scheme_name=None, description=None, auto_error=False)


def get_credentials(token: HTTPAuthorizationCredentials = Depends(token_scheme)):
    return token.credentials


def get_auth_module():
    return AuthModule(None)


class AuthModule:
    def __init__(self):
        pass

    def check_and_get_user_info(self, token):
        pass
