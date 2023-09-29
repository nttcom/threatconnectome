import os

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import get_current_user, token_scheme
from app.models import Account
from app.schemas import FsServerInfo, SlackCheckRequest
from app.slack import post_message, validate_slack_webhook_url

router = APIRouter(prefix="/external", tags=["external"])


@router.post("/slack/check")
def check_webhook_url(data: SlackCheckRequest, current_user: Account = Depends(get_current_user)):
    """
    Send test message to slack used by incomming webhook url
    """
    validate_slack_webhook_url(data.slack_webhook_url)
    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "test message from Threatconnectome"},
        }
    ]
    response = post_message(data.slack_webhook_url, blocks)
    if response is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.body)


@router.post("/flashsense/check")
def check_fs(
    token: HTTPAuthorizationCredentials = Depends(token_scheme),
    current_user: Account = Depends(get_current_user),
):
    """
    Check connection with Flashsense server.
    User must have valid flashsense account.
    """
    fs_api = os.environ["FLASHSENSE_API_URL"]
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token.credentials}",
    }
    try:
        response = requests.get(f"{fs_api}/users", headers=headers, timeout=30)
    except requests.exceptions.Timeout as flashsense_timeout:
        print(flashsense_timeout)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not connect to flashsense",
        ) from flashsense_timeout

    if response.status_code == 401:
        print(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your account is not valid in flashsense",
        )
    if response.status_code != 200:
        print(response)
        raise HTTPException(status_code=response.status_code, detail="Something went wrong")

    return Response(status_code=status.HTTP_200_OK)


@router.get("/flashsense/info", response_model=FsServerInfo)
def get_fs_info(current_user: Account = Depends(get_current_user)):
    """
    Get flashsense server info.
    """
    return FsServerInfo(api_url=os.environ["FLASHSENSE_API_URL"])
