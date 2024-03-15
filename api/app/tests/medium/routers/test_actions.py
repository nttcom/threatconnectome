from typing import List, Optional
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app import models, schemas
from app.main import app
from app.tests.medium.constants import (
    ACTION1,
    ACTION2,
    ACTION3,
    PTEAM1,
    TOPIC1,
    TOPIC2,
    USER1,
    USER2,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    assert_200,
    assert_204,
    common_put,
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    headers,
)

client = TestClient(app)


def test_create_action__tags():
    user1 = create_user(USER1)
    parent_tag1 = create_tag(USER1, "alpha:info1:")
    child_tag11 = create_tag(USER1, "alpha:info1:mgr1")
    parent_tag2 = create_tag(USER1, "bravo:info2:")
    child_tag21 = create_tag(USER1, "bravo:info2:mgr1")
    pteam1 = create_pteam(USER1, PTEAM1)

    def _get_action_by_id(action: dict) -> dict:
        return assert_200(client.get(f"/actions/{action['action_id']}", headers=headers(USER1)))

    def _get_pteam_actions(pteam: schemas.PTeamInfo, topic: schemas.TopicResponse) -> List[dict]:
        data = assert_200(
            client.get(
                f"/topics/{topic.topic_id}/actions/pteam/{pteam.pteam_id}",
                headers=headers(USER1),
            )
        )
        return data.get("actions", [])

    def _cmp_actions(req: Optional[dict], resp: dict) -> bool:
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

    def _find_action(actions: List[dict], target: dict) -> Optional[dict]:
        return next(filter(lambda x: _cmp_actions(x, target), actions), {})

    ## topic1: not tagged
    topic1 = create_topic(USER1, {**TOPIC1, "tags": []})
    assert _get_pteam_actions(pteam1, topic1) == []

    # no tagged action: ok
    request = {**ACTION1, "topic_id": str(topic1.topic_id)}
    action11 = assert_200(client.post("/actions", headers=headers(USER1), json=request))
    assert _cmp_actions(request, action11)
    assert _cmp_actions(request, _get_action_by_id(action11))
    assert UUID(action11["created_by"]) == user1.user_id

    all_actions = _get_pteam_actions(pteam1, topic1)
    assert len(all_actions) == 1
    assert _find_action(all_actions, action11)

    # tagged action: ng
    request = {
        **ACTION2,
        "topic_id": str(topic1.topic_id),
        "ext": {"tags": [child_tag11.tag_name]},
    }
    with pytest.raises(HTTPError, match=r"400: Bad Request: Action Tag mismatch with Topic Tag"):
        assert_200(client.post("/actions", headers=headers(USER1), json=request))

    ## topic2: tagged parent1
    topic2 = create_topic(USER1, {**TOPIC2, "tags": [parent_tag1.tag_name]})
    assert _get_pteam_actions(pteam1, topic2) == []

    # tagged (different parent) action: ng
    request = {
        **ACTION1,
        "topic_id": str(topic2.topic_id),
        "ext": {"tags": [parent_tag2.tag_name]},
    }
    with pytest.raises(HTTPError, match=r"400: Bad Request: Action Tag mismatch with Topic Tag"):
        assert_200(client.post("/actions", headers=headers(USER1), json=request))

    # tagged (different child) action: ng
    request = {
        **ACTION1,
        "topic_id": str(topic2.topic_id),
        "ext": {"tags": [child_tag21.tag_name]},
    }
    with pytest.raises(HTTPError, match=r"400: Bad Request: Action Tag mismatch with Topic Tag"):
        assert_200(client.post("/actions", headers=headers(USER1), json=request))

    # no tagged action: ok
    request = {**ACTION1, "topic_id": str(topic2.topic_id)}
    action21 = assert_200(client.post("/actions", headers=headers(USER1), json=request))
    assert _cmp_actions(request, action21)
    assert _cmp_actions(request, _get_action_by_id(action21))

    all_actions = _get_pteam_actions(pteam1, topic2)
    assert len(all_actions) == 1
    assert _find_action(all_actions, action21)

    # tagged (parent) action: ok
    request = {
        **ACTION2,
        "topic_id": str(topic2.topic_id),
        "ext": {"tags": [parent_tag1.tag_name]},
    }
    action22 = assert_200(client.post("/actions", headers=headers(USER1), json=request))
    assert _cmp_actions(request, action22)
    assert _cmp_actions(request, _get_action_by_id(action22))

    all_actions = _get_pteam_actions(pteam1, topic2)
    assert len(all_actions) == 2
    assert _find_action(all_actions, action21)
    assert _find_action(all_actions, action22)

    # tagged (child) action: ok
    request = {
        **ACTION3,
        "topic_id": str(topic2.topic_id),
        "ext": {"tags": [child_tag11.tag_name]},
    }
    action23 = assert_200(client.post("/actions", headers=headers(USER1), json=request))
    assert _cmp_actions(request, action23)
    assert _cmp_actions(request, _get_action_by_id(action23))

    all_actions = _get_pteam_actions(pteam1, topic2)
    assert len(all_actions) == 3
    assert _find_action(all_actions, action21)
    assert _find_action(all_actions, action22)
    assert _find_action(all_actions, action23)


def test_create_action__with_action_id():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    def _get_action_by_id(action_id: str) -> dict:
        return assert_200(client.get(f"/actions/{action_id}", headers=headers(USER1)))

    def _get_pteam_actions(pteam: schemas.PTeamInfo, topic: schemas.TopicResponse) -> List[dict]:
        data = assert_200(
            client.get(
                f"/topics/{topic.topic_id}/actions/pteam/{pteam.pteam_id}",
                headers=headers(USER1),
            )
        )
        return data.get("actions", [])

    def _cmp_actions(req: Optional[dict], resp: dict) -> bool:
        if not req:
            return False
        for key, val in req.items():
            if req[key] != resp[key]:
                return False
        return True

    def _find_action(actions: List[dict], target: dict) -> Optional[dict]:
        return next(filter(lambda x: _cmp_actions(x, target), actions), {})

    topic1 = create_topic(USER1, {**TOPIC1, "actions": []})
    assert _get_pteam_actions(pteam1, topic1) == []

    # create action with action_id
    action_id1 = str(uuid4())
    request = {**ACTION1, "topic_id": str(topic1.topic_id), "action_id": action_id1}
    action1 = assert_200(client.post("/actions", headers=headers(USER1), json=request))
    assert _cmp_actions(request, action1)
    assert _cmp_actions(request, _get_action_by_id(action_id1))

    # duplicated action_id
    request = {**ACTION2, "topic_id": str(topic1.topic_id), "action_id": action_id1}
    with pytest.raises(HTTPError, match=r"400: Bad Request: Action id already exists"):
        assert_200(client.post("/actions", headers=headers(USER1), json=request))


def test_create_action__with_new_tags():
    create_user(USER1)
    topic1 = create_topic(USER1, TOPIC1)
    tag_str1 = "testtag:alpha:one"
    tag_str2 = "testtag:bravo:one"

    with pytest.raises(HTTPError, match=rf"400: Bad Request: No such tags: {tag_str1}"):
        assert_200(
            client.post(
                "/actions",
                headers=headers(USER1),
                json={
                    "topic_id": str(topic1.topic_id),
                    **ACTION1,
                    "ext": {"tags": [tag_str1]},
                },
            )
        )

    with pytest.raises(HTTPError, match=rf"400: Bad Request: No such tags: {tag_str1}, {tag_str2}"):
        assert_200(
            client.post(
                "/actions",
                headers=headers(USER1),
                json={
                    "topic_id": str(topic1.topic_id),
                    **ACTION1,
                    "ext": {"tags": [tag_str2, tag_str1]},
                },
            )
        )


def test_update_action():
    user1 = create_user(USER1)
    create_user(USER2)
    parent_tag1 = create_tag(USER1, "alpha:info1:")
    child_tag11 = create_tag(USER1, "alpha:info1:mgr1")
    child_tag12 = create_tag(USER1, "alpha:info1:mgr2")
    parent_tag2 = create_tag(USER1, "bravo:info2:")
    pteam1 = create_pteam(USER1, PTEAM1)

    def _get_action_by_id(action: dict) -> dict:
        return assert_200(client.get(f"/actions/{action['action_id']}", headers=headers(USER1)))

    def _get_pteam_actions(pteam: schemas.PTeamInfo, topic: schemas.TopicResponse) -> List[dict]:
        data = assert_200(
            client.get(
                f"/topics/{topic.topic_id}/actions/pteam/{pteam.pteam_id}",
                headers=headers(USER1),
            )
        )
        return data.get("actions", [])

    def _cmp_actions(req: Optional[dict], resp: dict) -> bool:
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

    def _find_action(actions: List[dict], target: dict) -> Optional[dict]:
        return next(filter(lambda x: _cmp_actions(x, target), actions), {})

    ## topic1: not tagged
    topic1 = create_topic(USER1, {**TOPIC1, "tags": []})
    assert _get_pteam_actions(pteam1, topic1) == []

    # not tagged action1
    request = {**ACTION1, "topic_id": str(topic1.topic_id)}
    action11 = assert_200(client.post("/actions", headers=headers(USER1), json=request))
    assert _cmp_actions(request, action11)
    assert _cmp_actions(request, _get_action_by_id(action11))

    # update with tag: ng
    request = {**action11, "ext": {"tags": [child_tag11.tag_name]}}
    with pytest.raises(HTTPError, match=r"400: Bad Request: Action Tag mismatch with Topic Tag"):
        assert_200(
            client.put(f"/actions/{action11['action_id']}", headers=headers(USER1), json=request)
        )

    # update without tag: ok
    request = {
        "action": "updated action one",
        "action_type": "detection",
        "recommended": not request["recommended"],
        "ext": {},  # not modified
    }
    action11b = assert_200(
        client.put(f"/actions/{action11['action_id']}", headers=headers(USER1), json=request)
    )
    assert action11b["action_id"] == action11["action_id"]
    assert UUID(action11["created_by"]) == UUID(action11b["created_by"]) == user1.user_id
    assert action11["created_at"] == action11b["created_at"]
    assert _cmp_actions(request, action11b)
    assert _cmp_actions(request, _get_action_by_id(action11))

    all_actions = _get_pteam_actions(pteam1, topic1)
    assert len(all_actions) == 1
    assert _find_action(all_actions, action11b)

    ## topic2: tagged parent1
    topic2 = create_topic(USER1, {**TOPIC2, "tags": [parent_tag1.tag_name]})
    assert _get_pteam_actions(pteam1, topic2) == []

    # tagged (child11)
    request = {
        **ACTION1,
        "topic_id": str(topic2.topic_id),
        "ext": {"tags": [child_tag11.tag_name]},
    }
    action21 = assert_200(client.post("/actions", headers=headers(USER1), json=request))
    assert _cmp_actions(request, action21)
    assert _cmp_actions(request, _get_action_by_id(action21))

    # update with tag (another child 12): ok
    request = {
        "action": "updated action two",
        "action_type": "rejection",
        "recommended": not request["recommended"],
        "ext": {"tags": [child_tag12.tag_name]},
    }
    action21b = assert_200(
        client.put(f"/actions/{action21['action_id']}", headers=headers(USER1), json=request)
    )
    assert action21b["action_id"] == action21["action_id"]
    assert _cmp_actions(request, action21b)
    assert _cmp_actions(request, _get_action_by_id(action21))

    all_actions = _get_pteam_actions(pteam1, topic2)
    assert len(all_actions) == 1
    assert _find_action(all_actions, action21b)

    # change tag (another parent): ng
    request = {
        **request,
        "ext": {"tags": [parent_tag2.tag_name]},
    }
    with pytest.raises(HTTPError, match=r"400: Bad Request: Action Tag mismatch with Topic Tag"):
        assert_200(
            client.put(f"/actions/{action21['action_id']}", headers=headers(USER1), json=request)
        )

    # remove tag: ok
    request = {
        **request,
        "ext": {},
    }
    action21c = assert_200(
        client.put(f"/actions/{action21['action_id']}", headers=headers(USER1), json=request)
    )
    assert action21c["action_id"] == action21["action_id"]
    assert _cmp_actions(request, action21c)
    assert _cmp_actions(request, _get_action_by_id(action21))

    all_actions = _get_pteam_actions(pteam1, topic2)
    assert len(all_actions) == 1
    assert _find_action(all_actions, action21c)


def test_update_action__with_new_tags():
    create_user(USER1)
    parent_tag1 = create_tag(USER1, "testtag:alpha:")
    child_tag11 = create_tag(USER1, "testtag:alpha:A")
    child_tag_str12 = "testtag:alpha:B"
    child_tag_str13 = "testtag:alpha:C"
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [parent_tag1.tag_name],
            "actions": [{**ACTION1, "ext": {"tags": [child_tag11.tag_name]}}],
        },
    )
    action1 = topic1.actions[0]

    with pytest.raises(HTTPError, match=rf"400: Bad Request: No such tags: {child_tag_str12}"):
        assert_200(
            client.put(
                f"actions/{action1.action_id}",
                headers=headers(USER1),
                json={
                    **ACTION1,
                    "action_id": str(action1.action_id),
                    "ext": {"tags": [child_tag_str12]},  # change tags
                },
            )
        )

    with pytest.raises(HTTPError, match=rf"400: Bad Request: No such tags: {child_tag_str12}"):
        assert_200(
            client.put(
                f"actions/{action1.action_id}",
                headers=headers(USER1),
                json={
                    **ACTION1,
                    "action_id": str(action1.action_id),
                    "ext": {"tags": [child_tag11.tag_name, child_tag_str12]},  # append tag
                },
            )
        )

    with pytest.raises(
        HTTPError,
        match=rf"400: Bad Request: No such tags: {child_tag_str12}, {child_tag_str13}",
    ):
        assert_200(
            client.put(
                f"actions/{action1.action_id}",
                headers=headers(USER1),
                json={
                    **ACTION1,
                    "action_id": str(action1.action_id),
                    "ext": {
                        "tags": [child_tag_str13, child_tag11.tag_name, child_tag_str12],
                    },  # append 2 tags unsorted
                },
            )
        )


class TestUpdatePartialAction:
    parent_tag1: schemas.TagResponse
    child_tag11: schemas.TagResponse
    child_tag12: schemas.TagResponse
    action1_api: str
    action_data1: dict

    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        create_user(USER1)
        self.parent_tag1 = create_tag(USER1, "alpha:info1:")
        self.child_tag11 = create_tag(USER1, "alpha:info1:mgr1")
        self.child_tag12 = create_tag(USER1, "alpha:info1:mgr2")

        action_id1 = str(uuid4())
        self.action1_api = f"/actions/{action_id1}"

        # create a topic with action1
        action1_request = {
            "topic_id": None,  # can be None in create_topic()
            "action_id": action_id1,
            "action": "Update package to latest version",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [self.child_tag11.tag_name],
            },
        }
        create_topic(
            USER1,
            {
                **TOPIC1,
                "tags": [self.parent_tag1.tag_name],
                "actions": [action1_request],
            },
        )

        # get action1 as base data to compare
        data = assert_200(client.get(self.action1_api, headers=headers(USER1)))
        assert data["action_id"] == action_id1
        for key in ["action", "action_type", "recommended", "ext"]:
            assert data[key] == action1_request[key]
        self.action_data1 = data

    def test_empty_update(self):
        data = common_put(USER1, self.action1_api)  # put request is empty dict
        assert data == self.action_data1

    # update one by one

    def test_update_action(self):
        new_action = "shutdown the service"
        data = common_put(USER1, self.action1_api, action=new_action)
        assert data == {**self.action_data1, "action": new_action}

    def test_update_action_type(self):
        new_action_type = models.ActionType.mitigation
        data = common_put(USER1, self.action1_api, action_type=new_action_type)
        assert data == {**self.action_data1, "action_type": new_action_type}

    def test_update_recommended(self):
        new_recommended = False
        data = common_put(USER1, self.action1_api, recommended=new_recommended)
        assert data == {**self.action_data1, "recommended": new_recommended}

    def test_update_ext(self):
        new_ext = {"tags": [self.child_tag12.tag_name]}
        data = common_put(USER1, self.action1_api, ext=new_ext)
        assert data == {**self.action_data1, "ext": new_ext}

    # update at once

    def test_multiple_update(self):
        update_request = {
            "action": "give up",
            "action_type": models.ActionType.acceptance,
            "recommended": False,
            "ext": {
                "tags": [self.child_tag11.tag_name, self.child_tag12.tag_name],
            },
        }
        data = common_put(USER1, self.action1_api, **update_request)
        for key in ["action_id", "topic_id"]:
            assert data[key] == self.action_data1[key]
        for key in ["action", "action_type", "recommended", "ext"]:
            assert data[key] == update_request[key]


def test_delete_action():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)

    def _get_action_by_id(action: dict) -> dict:
        return assert_200(client.get(f"/actions/{action['action_id']}", headers=headers(USER1)))

    def _get_pteam_actions(pteam: schemas.PTeamInfo, topic: schemas.TopicResponse) -> List[dict]:
        data = assert_200(
            client.get(
                f"/topics/{topic.topic_id}/actions/pteam/{pteam.pteam_id}",
                headers=headers(USER1),
            )
        )
        return data.get("actions", [])

    def _cmp_actions(req: Optional[dict], resp: dict) -> bool:
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

    def _find_action(actions: List[dict], target: dict) -> Optional[dict]:
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
