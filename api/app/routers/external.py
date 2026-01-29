from email_validator import validate_email
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.auth.account import get_current_user
from app.constants import (
    MAX_EMAIL_ADDRESS_LENGTH_IN_HALF,
    MAX_WEBHOOK_URL_LENGTH_IN_HALF,
    SYSTEM_EMAIL,
)
from app.models import Account
from app.notification.sendgrid import (
    SendgridFailStatusError,
    SendgridHttpError,
    ready_to_send_email,
    send_email,
)
from app.notification.slack import (
    send_slack,
    validate_slack_webhook_url,
)
from app.routers.validators.field_validator import strip_and_validate_field_length
from app.schemas import EmailCheckRequest, SlackCheckRequest

router = APIRouter(prefix="/external", tags=["external"])

# Common error messages for external validation
WEBHOOK_URL_TOO_LONG_MESSAGE = (
    f"Too long Slack webhook URL. Max length is {MAX_WEBHOOK_URL_LENGTH_IN_HALF} "
    f"in half-width or {int(MAX_WEBHOOK_URL_LENGTH_IN_HALF / 2)} in full-width"
)
EMAIL_ADDRESS_TOO_LONG_MESSAGE = (
    f"Too long email address. Max length is {MAX_EMAIL_ADDRESS_LENGTH_IN_HALF} "
    f"in half-width or {int(MAX_EMAIL_ADDRESS_LENGTH_IN_HALF / 2)} in full-width"
)


@router.post("/slack/check")
def check_webhook_url(data: SlackCheckRequest, current_user: Account = Depends(get_current_user)):
    """
    Send test message to slack used by incoming webhook url
    """
    # validate webhook URL length
    webhook_url = strip_and_validate_field_length(
        data.slack_webhook_url,
        MAX_WEBHOOK_URL_LENGTH_IN_HALF,
        WEBHOOK_URL_TOO_LONG_MESSAGE,
    )

    validate_slack_webhook_url(webhook_url)
    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "test message from Threatconnectome"},
        }
    ]
    response = send_slack(webhook_url, blocks)
    if response is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.body)


@router.post("/email/check")
def check_email(data: EmailCheckRequest, current_user: Account = Depends(get_current_user)):
    """
    Send test email with sendgrid
    """
    # validate email address length
    email = strip_and_validate_field_length(
        data.email,
        MAX_EMAIL_ADDRESS_LENGTH_IN_HALF,
        EMAIL_ADDRESS_TOO_LONG_MESSAGE,
    )

    if not ready_to_send_email():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sendgrid not ready (maybe missing api_key)",
        )
    try:
        validate_email(SYSTEM_EMAIL, check_deliverability=False)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sendgrid not ready (missing SYSTEM_EMAIL)",
        )
    try:
        send_email(
            email,
            SYSTEM_EMAIL,
            "test message from Threatconnectome",
            "test message from Threatconnectome",
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
    except SendgridFailStatusError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"sendgrid fail status error: {str(err)}",
        )
    except SendgridHttpError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"sendgrid http error: {str(err)}",
        )

    return Response(status_code=status.HTTP_200_OK, content="OK")
