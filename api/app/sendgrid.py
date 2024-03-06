import os

import sendgrid
from email_validator import validate_email
from python_http_client import exceptions
from sendgrid.helpers.mail import Content, Email, Mail, To

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")


def ready_to_send_email() -> bool:
    if not SENDGRID_API_KEY:
        return False
    return True


class SendgridFailStatusError(Exception):
    pass


class SendgridHttpError(Exception):
    pass


def send_email(to_email: str, from_email: str, subject: str, content: str):
    if not SENDGRID_API_KEY:
        raise ValueError("SENDGRID_API_KEY is not set")
    try:
        validate_email(to_email, check_deliverability=False)
    except ValueError as err:
        raise ValueError("Invalid to_email") from err
    try:
        validate_email(from_email, check_deliverability=False)
    except ValueError as err:
        raise ValueError("Invalid from_email") from err

    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        mail = Mail(Email(from_email), To(to_email), subject, Content("text/plain", content))

        response = sg.client.mail.send.post(request_body=mail.get())
        if response.status_code != 202:
            raise SendgridFailStatusError(response.body)
        return response
    except exceptions.HTTPError as err:
        raise SendgridHttpError(err)
