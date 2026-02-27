from fastapi import APIRouter, Depends, Form, Request
from pydantic import SecretStr

from app.auth.auth_exception import AuthException
from app.auth.auth_module import AuthModule, get_auth_module
from app.routers.utils.http_excption_creator import create_http_exception

from ..schemas import RefreshTokenRequest, Token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/token", response_model=Token)
def login_for_access_token(
    request: Request,
    username: str = Form(),
    password: SecretStr = Form(),
    auth_module: AuthModule = Depends(get_auth_module),
) -> Token:
    try:
        token, uid = auth_module.login_for_access_token(username, password)
        request.state.uid = uid
        return token
    except AuthException as auth_exception:
        raise create_http_exception(auth_exception)


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    request: Request,
    refresh_token_request: RefreshTokenRequest,
    auth_module: AuthModule = Depends(get_auth_module),
) -> Token:
    try:
        token, uid = auth_module.refresh_access_token(refresh_token_request.refresh_token)
        request.state.uid = uid
        return token
    except AuthException as auth_exception:
        raise create_http_exception(auth_exception)
