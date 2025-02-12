from fastapi import APIRouter, Depends, Form
from pydantic import SecretStr

from app.auth.auth_module import AuthModule, get_auth_module

from ..schemas import RefreshTokenRequest, Token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/token", response_model=Token)
def login_for_access_token(
    username: str = Form(),
    password: SecretStr = Form(),
    auth_module: AuthModule = Depends(get_auth_module),
) -> Token:
    return auth_module.login_for_access_token(username, password)


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    request: RefreshTokenRequest, auth_module: AuthModule = Depends(get_auth_module)
) -> Token:
    return auth_module.refresh_access_token(request.refresh_token)
