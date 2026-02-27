from fastapi import HTTPException, status

from ..schemas import Token


def get_auth_module():
    return AuthModule(None)


class AuthModule:
    def __init__(self):
        pass

    def login_for_access_token(self, username, password) -> tuple[Token, str | None]:
        return Token(access_token="", token_type="bearer", refresh_token=""), ""

    def refresh_access_token(self, refresh_token) -> tuple[Token, str | None]:
        return Token(access_token="", token_type="bearer", refresh_token=""), ""

    def check_and_get_user_info(self, token):
        pass

    def check_token(self, token):
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def delete_user(self, uid):
        pass
