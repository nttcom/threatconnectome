import pytest
from sqlalchemy.exc import OperationalError

from app.tests.common.constants import USER1
from app.tests.common.utils import client, create_user, headers
from app.utility.db_exception_handler import (
    DB_UNAVAILABLE_DETAIL,
    DB_UNAVAILABLE_RETRY_AFTER_SECONDS,
)

# Note: loggers are disabled by alembic's fileConfig() during test setup,
# so the module-level logger is mocked instead of relying on caplog.
LOGGER_PATH = "app.utility.db_exception_handler.logger"


def _operational_error(message: str) -> OperationalError:
    return OperationalError("SELECT 1", {}, Exception(message))


class TestDbOperationalErrorHandler:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        create_user(USER1)
        self.headers = headers(USER1)

    @pytest.mark.parametrize(
        "db_error_message",
        [
            "server closed the connection unexpectedly",
            "SSL SYSCALL error: EOF detected",
        ],
    )
    def test_it_should_return_503_with_retry_after_when_db_connection_is_lost(
        self, mocker, db_error_message
    ):
        # Given
        mock_logger = mocker.patch(LOGGER_PATH)
        mocker.patch(
            "app.routers.vulns.command.get_vulns",
            side_effect=_operational_error(db_error_message),
        )

        # When
        response = client.get("/vulns", headers=self.headers)

        # Then
        assert response.status_code == 503
        assert response.json() == {"detail": DB_UNAVAILABLE_DETAIL}
        assert response.headers["Retry-After"] == str(DB_UNAVAILABLE_RETRY_AFTER_SECONDS)
        mock_logger.error.assert_called_once()
        assert mock_logger.error.call_args.args[1:] == ("GET", "/vulns")
        assert isinstance(mock_logger.error.call_args.kwargs["exc_info"], OperationalError)

    def test_it_should_not_expose_db_error_details_in_response(self, mocker):
        # Given
        mocker.patch(LOGGER_PATH)
        mocker.patch(
            "app.routers.vulns.command.get_vulns",
            side_effect=_operational_error("connection to server at 10.0.0.1 failed"),
        )

        # When
        response = client.get("/vulns", headers=self.headers)

        # Then
        assert response.status_code == 503
        assert "10.0.0.1" not in response.text
        assert "SELECT" not in response.text

    def test_it_should_return_503_when_db_connection_is_lost_in_dependency(self, mocker):
        # Given: the account lookup in get_current_user fails
        mock_logger = mocker.patch(LOGGER_PATH)
        mocker.patch(
            "app.auth.account.persistence.get_account_by_uid",
            side_effect=_operational_error("server closed the connection unexpectedly"),
        )

        # When
        response = client.get("/users/me", headers=self.headers)

        # Then
        assert response.status_code == 503
        assert response.json() == {"detail": DB_UNAVAILABLE_DETAIL}
        assert response.headers["Retry-After"] == str(DB_UNAVAILABLE_RETRY_AFTER_SECONDS)
        mock_logger.error.assert_called_once()
        assert mock_logger.error.call_args.args[1:] == ("GET", "/users/me")

    def test_it_should_not_change_other_exceptions(self, mocker):
        # Given
        mocker.patch(
            "app.routers.vulns.command.get_vulns",
            side_effect=ValueError("invalid sort key"),
        )

        # When
        response = client.get("/vulns", headers=self.headers)

        # Then: existing ValueError handling (400) is kept
        assert response.status_code == 400
        assert "Retry-After" not in response.headers
