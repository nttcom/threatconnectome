import os
from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials, initialize_app
from sqlalchemy.orm import Session

from app import persistence

from .database import get_db
from .models import Account

token_scheme = HTTPBearer(scheme_name=None, description=None, auto_error=False)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def setup_firebase_auth():
    cred = credentials.Certificate(os.environ["FIREBASE_CRED"])
    initialize_app(cred)
    return cred


def get_firebase_credentials():
    return credentials.Certificate(os.environ["FIREBASE_CRED"])


def verify_id_token(
    token: HTTPAuthorizationCredentials = Depends(token_scheme),
    firebase_credentials=Depends(get_firebase_credentials),
) -> Dict[str, Any]:
    if firebase_credentials is None or token is None:
        raise credentials_exception
    try:
        decoded_token: Dict[str, Any] = auth.verify_id_token(token.credentials, check_revoked=True)
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
        raise credentials_exception from error

    # check email verified if not using firebase emulator
    emulator_host = os.getenv("FIREBASE_AUTH_EMULATOR_HOST", "")
    if emulator_host == "":
        user_info = auth.get_user(decoded_token["uid"])
        if user_info.email_verified is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email is not verified. Try logging in on UI and verify email.",
            )

    return decoded_token


def get_current_user(
    decoded_token: Dict[str, Any] = Depends(verify_id_token), db: Session = Depends(get_db)
) -> Account:
    user = persistence.get_account_by_firebase_uid(db, decoded_token["uid"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such user",
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user
