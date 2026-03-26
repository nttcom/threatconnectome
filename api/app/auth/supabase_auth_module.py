import logging
import os

from supabase import create_client

from app.auth.auth_exception import AuthErrorType, AuthException
from app.auth.auth_module import AuthModule

from ..schemas import Token

log = logging.getLogger(__name__)


class SupabaseAuthModule(AuthModule):
    def __init__(self):
        super().__init__()

        url = os.getenv("SUPABASE_URL")
        if url is None:
            raise Exception(f"Unsupported SUPABASE_URL: {url}")
        key = os.getenv("SUPABASE_ANON_KEY")
        if key is None:
            raise Exception(f"Unsupported SUPABASE_ANON_KEY: {key}")

        self.supabase = create_client(url, key)

    def login_for_access_token(self, username, password) -> tuple[Token, str | None]:
        payload = {
            "email": username,
            "password": password.get_secret_value(),
        }

        try:
            user_data = self.supabase.auth.sign_in_with_password(payload)
            user_model = user_data.model_dump()
            session = user_model.get("session")
            user = user_model.get("user")
            user_id = user.get("id") if user else None
        except Exception as error:
            log.error(f"Failed to login: {error}")
            raise AuthException(
                AuthErrorType.INTERNAL_SERVER_ERROR, "Error get access token"
            ) from error

        return (
            Token(
                access_token=session.get("access_token"),
                token_type="bearer",
                refresh_token=session.get("refresh_token"),
            ),
            user_id,
        )

    def refresh_access_token(self, refresh_token) -> tuple[Token, str | None]:
        try:
            response_data = self.supabase.auth.refresh_session(refresh_token)
            response_model = response_data.model_dump()
            session = response_model.get("session")
            user = session.get("user")
            user_id = user.get("id") if user else None
        except Exception as error:
            log.error(f"Failed to refresh: {error}")
            raise AuthException(
                AuthErrorType.INTERNAL_SERVER_ERROR, "Could not refresh token"
            ) from error

        return (
            Token(
                access_token=session.get("access_token"),
                token_type="bearer",
                refresh_token=session.get("refresh_token"),
            ),
            user_id,
        )

    def check_and_get_user_info(self, token):
        super().check_token(token)

        try:
            user_data = self.supabase.auth.get_user(token.credentials)
            user = user_data.model_dump().get("user")
        except Exception as error:
            log.error(f"Failed to get user: {error}")
            raise AuthException(
                AuthErrorType.INTERNAL_SERVER_ERROR, "Error get user info"
            ) from error

        return user.get("id"), user.get("email")

    def delete_user(self, uid):
        url = os.getenv("SUPABASE_URL")
        if url is None:
            raise Exception(f"Unsupported SUPABASE_URL: {url}")
        key = os.getenv("SERVICE_ROLE_KEY")
        if key is None:
            raise Exception(f"Unsupported SERVICE_ROLE_KEY: {key}")

        try:
            supabase1 = create_client(url, key)
            supabase1.auth.admin.delete_user(uid)
        except Exception as error:
            log.error(f"Failed to delete user: {error}")
            raise AuthException(
                AuthErrorType.INTERNAL_SERVER_ERROR, "Error deleting user"
            ) from error
