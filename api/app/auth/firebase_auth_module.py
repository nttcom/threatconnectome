import os

from fastapi import HTTPException, status
from firebase_admin import auth, credentials, initialize_app

from app.auth.auth_module import AuthModule


class FirebaseAuthModule(AuthModule):
    def __init__(self):
        super().__init__()
        self.cred = credentials.Certificate(os.environ["FIREBASE_CRED"])
        initialize_app(self.cred)

    def check_and_get_user_info(self, token):
        try:
            decoded_token = auth.verify_id_token(token.credentials, check_revoked=True)
        except auth.ExpiredIdTokenError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            ) from error
        except auth.RevokedIdTokenError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has revoked",
            ) from error
        except auth.CertificateFetchError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to obtain required credentials",
            ) from error
        except auth.UserDisabledError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Disabled user",
            ) from error
        except (auth.InvalidIdTokenError, ValueError) as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from error

        user_info = auth.get_user(decoded_token["uid"])

        # check email verified if not using firebase emulator
        emulator_host = os.getenv("FIREBASE_AUTH_EMULATOR_HOST", "")
        if emulator_host == "" and user_info.email_verified is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email is not verified. Try logging in on UI and verify email.",
            )

        email = user_info.email
        # if user_info.email is empty, get email from auth provider data
        if email is None:
            if len(user_info.provider_data) > 0:
                email = user_info.provider_data[0].email

        return user_info.uid, email
