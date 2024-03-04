import os

import sendgrid
from python_http_client import exceptions
from sendgrid.helpers.mail import Content, Email, Mail, To


class SendgridFailStatusError(Exception):
    pass


class SendgridHttpError(Exception):
    pass


def send_email(to_email: str, subject: str, content: str):
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
    if SENDGRID_API_KEY is None:
        raise ValueError("SENDGRID_API_KEY is not set")

    SYSTEM_EMAIL = os.environ.get("SYSTEM_EMAIL")
    if SYSTEM_EMAIL is None:
        raise ValueError("SYSTEM_EMAIL is not set")

    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        mail = Mail(Email(SYSTEM_EMAIL), To(to_email), subject, Content("text/plain", content))

        response = sg.client.mail.send.post(request_body=mail.get())
        if response.status_code != 202:
            print(response.body)
            raise SendgridFailStatusError(response.body)
        return response
    except exceptions.HTTPError as err:
        print(err)
        raise SendgridHttpError(err)
