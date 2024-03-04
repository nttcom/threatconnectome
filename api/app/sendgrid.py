import os

import sendgrid
from python_http_client import exceptions
from sendgrid.helpers.mail import Content, Email, Mail, To


def send_email(to_email: str, subject: str, content: str):
    try:
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
        from_email = Email(os.environ.get("SYSTEM_EMAIL"))

        mail = Mail(from_email, To(to_email), subject, Content("text/plain", content))
        response = sg.client.mail.send.post(request_body=mail.get())
        if response.status_code != 202:
            print("failed response to send email with sendgrid")
            print(response.body)
            return None
        return response
    except exceptions.HTTPError as e:
        print("failed to send email with sendgrid")
        print(e)
        return None
