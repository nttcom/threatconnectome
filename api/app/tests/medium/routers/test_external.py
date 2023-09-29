import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import FsServerInfo
from app.tests.medium.constants import USER1
from app.tests.medium.utils import create_user, headers

client = TestClient(app)


@pytest.mark.skip(reason="TODO: should be tested with slack")  # TODO
def test_check_slack():
    pass


def test_check_slack__with_wrong_url():
    create_user(USER1)

    request = {
        "slack_webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
    }

    response = client.post("/external/slack/check", headers=headers(USER1), json=request)
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"
    data = response.json()
    assert data["detail"] == "no_team"  # returned detail from slack incomming webhook


def test_check_slack__with_invalid_url():
    create_user(USER1)

    request = {"slack_webhook_url": "https://hooooks.slack.com/services"}

    response = client.post("/external/slack/check", headers=headers(USER1), json=request)
    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"
    data = response.json()
    assert data["detail"] == "Invalid slack webhook url"


@pytest.mark.skip(reason="TODO: should be tested with flashsense server")  # TODO
def test_check_fs():
    pass


def test_get_fs_info():
    create_user(USER1)
    response = client.get("/external/flashsense/info", headers=headers(USER1))
    assert response.status_code == 200
    fs_server_info = FsServerInfo(**response.json())
    assert isinstance(fs_server_info.api_url, str)
