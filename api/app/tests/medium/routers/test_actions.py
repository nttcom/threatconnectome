import pytest
from fastapi.testclient import TestClient

from app import schemas
from app.main import app
from app.tests.medium.constants import (
    ACTION1,
    PTEAM1,
    TOPIC1,
    USER1,
    USER2,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    assert_200,
    assert_204,
    create_pteam,
    create_topic,
    create_user,
    headers,
)

client = TestClient(app)


def test_delete_action():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    def _get_action_by_id(action: dict) -> dict:
        return assert_200(client.get(f"/actions/{action['action_id']}", headers=headers(USER1)))

    def _get_pteam_actions(pteam: schemas.PTeamInfo, topic: schemas.TopicResponse) -> list[dict]:
        data = assert_200(
            client.get(
                f"/topics/{topic.topic_id}/actions/pteam/{pteam.pteam_id}",
                headers=headers(USER1),
            )
        )
        return data.get("actions", [])

    def _cmp_actions(req: dict | None, resp: dict) -> bool:
        if not req:
            return False
        for key, val in req.items():
            if key == "action_id":
                if not resp[key]:
                    return False
            else:
                if req[key] != resp[key]:
                    return False
        return True

    def _find_action(actions: list[dict], target: dict) -> dict | None:
        return next(filter(lambda x: _cmp_actions(x, target), actions), {})

    ## topic1: not tagged
    topic1 = create_topic(USER1, {**TOPIC1, "tags": []})
    assert _get_pteam_actions(pteam1, topic1) == []

    # add action1
    request = {
        **ACTION1,
        "topic_id": str(topic1.topic_id),
    }
    action1 = assert_200(client.post("/actions", headers=headers(USER1), json=request))
    assert _cmp_actions(request, action1)
    assert _cmp_actions(request, _get_action_by_id(action1))

    # delete action by not a creator: ok
    assert_204(client.delete(f"/actions/{action1['action_id']}", headers=headers(USER2)))

    with pytest.raises(HTTPError, match=r"404: Not Found: No such topic action"):
        _get_action_by_id(action1)
    all_actions = _get_pteam_actions(pteam1, topic1)
    assert len(all_actions) == 0
