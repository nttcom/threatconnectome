import json

import pytest

from app.tests.common.constants import USER1
from app.tests.common.utils import client, create_user, headers
from app.utility.api_logging_middleware import INVALID_JSON_BODY, ApiLoggingMiddleware

# Note: "api_logger" is disabled by alembic's fileConfig() during test setup,
# so the module-level logger is mocked instead of relying on caplog.
LOGGER_PATH = "app.utility.api_logging_middleware.logger"


class TestApiLoggingMiddleware:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        self.user1 = create_user(USER1)
        # Obtain the token beforehand so that /auth/token is not logged in each test.
        self.headers = headers(USER1)

    def test_it_should_log_uid_of_current_user(self, mocker):
        # Given
        mock_logger = mocker.patch(LOGGER_PATH)

        # When
        response = client.get("/users/me", headers=self.headers)

        # Then
        assert response.status_code == 200
        mock_logger.info.assert_called_once()
        log_dict = json.loads(mock_logger.info.call_args.args[0])
        assert log_dict["http_status"] == 200
        assert log_dict["method"] == "GET"
        assert log_dict["path"] == "/users/me"
        assert log_dict["uid"] == self.user1.uid
        mock_logger.exception.assert_not_called()

    def test_it_should_store_uid_instead_of_orm_object_in_request_state(self, mocker):
        # Given
        captured_states = []
        original = ApiLoggingMiddleware.create_log

        def spy(self, request, response, body_bytes):
            captured_states.append(request.state)
            return original(self, request, response, body_bytes)

        mocker.patch.object(ApiLoggingMiddleware, "create_log", spy)

        # When
        response = client.get("/users/me", headers=self.headers)

        # Then
        assert response.status_code == 200
        assert len(captured_states) == 1
        assert getattr(captured_states[0], "uid", None) == self.user1.uid
        assert getattr(captured_states[0], "current_user", None) is None

    def test_it_should_keep_response_when_logging_fails(self, mocker):
        # Given
        mock_logger = mocker.patch(LOGGER_PATH)
        mocker.patch.object(
            ApiLoggingMiddleware,
            "create_log_for_common_api",
            side_effect=RuntimeError("logging failed"),
        )

        # When
        response = client.get("/users/me", headers=self.headers)

        # Then
        assert response.status_code == 200
        assert response.json()["uid"] == self.user1.uid
        mock_logger.exception.assert_called_once()
        message, method, path = mock_logger.exception.call_args.args
        assert "Failed to write API log" in message
        assert method == "GET"
        assert path == "/users/me"

    @pytest.mark.parametrize(
        "body",
        [
            b'{"code": "print(1)" "x"}',  # JSONDecodeError
            b"\xff\xfe\xfa",  # UnicodeDecodeError
            b"[" * 100000,  # RecursionError
        ],
        ids=["json_decode_error", "unicode_decode_error", "recursion_error"],
    )
    def test_it_should_return_original_status_and_log_when_json_body_is_malformed(
        self, mocker, body
    ):
        # Given: a request with a malformed JSON body to a non-existent path (e.g. from a scanner)
        mock_logger = mocker.patch(LOGGER_PATH)

        # When
        response = client.post(
            "/api/v1/code/blocks/exec/start",
            content=body,
            headers={"Content-Type": "application/json"},
        )

        # Then: the original 404 is returned and the access log is still written
        assert response.status_code == 404
        mock_logger.exception.assert_not_called()
        mock_logger.info.assert_called_once()
        log_dict = json.loads(mock_logger.info.call_args.args[0])
        assert log_dict["http_status"] == 404
        assert log_dict["path"] == "/api/v1/code/blocks/exec/start"
        assert log_dict["request_body"] == INVALID_JSON_BODY
        assert log_dict["uid"] is None
