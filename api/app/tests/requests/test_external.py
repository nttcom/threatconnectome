from fastapi.testclient import TestClient

from app.main import app
from app.notification.sendgrid import SendgridFailStatusError, SendgridHttpError
from app.tests.medium.constants import USER1
from app.tests.medium.utils import create_user, headers

client = TestClient(app)


class TestCheckSlack:
    """Tests for /external/slack/check endpoint"""

    def test_return_200_with_successful_slack_send(self, mocker):
        """Test successful Slack message sending with mocked Slack communication"""
        # Given
        create_user(USER1)
        request_data = {
            "slack_webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/valid_token"
        }

        # Mock successful Slack response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mocker.patch("app.routers.external.send_slack", return_value=mock_response)

        # When
        response = client.post("/external/slack/check", headers=headers(USER1), json=request_data)

        # Then
        assert response.status_code == 200

    def test_return_400_with_invalid_character_limits(self):
        """Test that invalid webhook URL character limits are rejected"""
        # Given
        webhook_url_value = "https://hooks.slack.com/services/" + "a" * 223
        create_user(USER1)
        request_data = {"slack_webhook_url": webhook_url_value}

        # When
        response = client.post("/external/slack/check", headers=headers(USER1), json=request_data)

        # Then
        assert response.status_code == 400
        detail = response.json().get("detail", "")
        assert detail == (
            "Too long Slack webhook URL. Max length is 255 in half-width or 127 in full-width"
        )

    def test_return_400_with_wrong_url(self):
        """Test error handling with wrong but valid URL format"""
        # Given
        create_user(USER1)
        request_data = {
            "slack_webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
        }

        # When
        response = client.post("/external/slack/check", headers=headers(USER1), json=request_data)

        # Then
        assert response.status_code == 400
        assert response.reason_phrase == "Bad Request"
        data = response.json()
        assert data["detail"] == "no_team"  # returned detail from slack incoming webhook

    def test_return_400_with_invalid_url_format(self):
        """Test error handling with invalid URL format"""
        # Given
        create_user(USER1)
        request_data = {"slack_webhook_url": "https://hooooks.slack.com/services"}

        # When
        response = client.post("/external/slack/check", headers=headers(USER1), json=request_data)

        # Then
        assert response.status_code == 400
        assert response.reason_phrase == "Bad Request"
        data = response.json()
        assert data["detail"] == "Invalid slack webhook url"


class TestCheckEmail:
    """Tests for /external/email/check endpoint"""

    def test_return_400_with_invalid_character_limits(self):
        """Test that invalid email character limits are rejected"""
        # Given
        create_user(USER1)
        email_value = "a" * 247 + "@test.com"
        request_data = {"email": email_value}

        # When
        response = client.post("/external/email/check", headers=headers(USER1), json=request_data)

        # Then
        assert response.status_code == 400
        detail = response.json().get("detail", "")
        assert detail == (
            "Too long email address. Max length is 255 in half-width or 127 in full-width"
        )

    def test_return_200_with_successful_email_send(self, mocker):
        """Test successful email sending with actual validation but mocked SendGrid communication"""
        # Given
        create_user(USER1)
        request_data = {"email": "test@example.com"}

        # Only mock external SendGrid communication, keep email validation logic
        mocker.patch("app.routers.external.ready_to_send_email", return_value=True)
        mocker.patch("app.routers.external.send_email", return_value=None)
        # Note: validate_email is NOT mocked - we want to test actual email format validation

        # When
        response = client.post("/external/email/check", headers=headers(USER1), json=request_data)

        # Then
        assert response.status_code == 200
        assert response.text == "OK"

    def test_return_500_when_sendgrid_not_ready(self, mocker):
        """Test error handling when SendGrid is not configured properly"""
        # Given
        create_user(USER1)
        request_data = {"email": "test@example.com"}

        # Mock SendGrid to simulate not ready state
        mocker.patch("app.routers.external.ready_to_send_email", return_value=False)

        # When
        response = client.post("/external/email/check", headers=headers(USER1), json=request_data)

        # Then
        assert response.status_code == 500
        detail = response.json().get("detail", "")
        assert detail == "Sendgrid not ready (maybe missing api_key)"

    def test_return_500_when_system_email_invalid(self, mocker):
        """Test error handling when SYSTEM_EMAIL is invalid"""
        # Given
        create_user(USER1)
        request_data = {"email": "test@example.com"}

        # Mock SendGrid functions
        mocker.patch("app.routers.external.ready_to_send_email", return_value=True)
        mocker.patch("app.routers.external.validate_email", side_effect=ValueError("Invalid email"))

        # When
        response = client.post("/external/email/check", headers=headers(USER1), json=request_data)

        # Then
        assert response.status_code == 500
        detail = response.json().get("detail", "")
        assert detail == "Sendgrid not ready (missing SYSTEM_EMAIL)"

    def test_return_500_when_sendgrid_fail_status_error(self, mocker):
        """Test error handling when SendGrid returns failure status"""
        # Given
        create_user(USER1)
        request_data = {"email": "test@example.com"}

        # Mock SendGrid functions
        mocker.patch("app.routers.external.ready_to_send_email", return_value=True)
        mocker.patch("app.routers.external.validate_email", return_value=True)
        mocker.patch(
            "app.routers.external.send_email",
            side_effect=SendgridFailStatusError("Sendgrid API returned error status"),
        )

        # When
        response = client.post("/external/email/check", headers=headers(USER1), json=request_data)

        # Then
        assert response.status_code == 500
        detail = response.json().get("detail", "")
        assert detail == "sendgrid fail status error: Sendgrid API returned error status"

    def test_return_500_when_sendgrid_http_error(self, mocker):
        """Test error handling when SendGrid HTTP error occurs"""
        # Given
        create_user(USER1)
        request_data = {"email": "test@example.com"}

        # Mock SendGrid functions
        mocker.patch("app.routers.external.ready_to_send_email", return_value=True)
        mocker.patch("app.routers.external.validate_email", return_value=True)
        mocker.patch(
            "app.routers.external.send_email",
            side_effect=SendgridHttpError("HTTP connection error"),
        )

        # When
        response = client.post("/external/email/check", headers=headers(USER1), json=request_data)

        # Then
        assert response.status_code == 500
        detail = response.json().get("detail", "")
        assert detail == "sendgrid http error: HTTP connection error"
