import json
import tempfile
from typing import Any, Type

import pytest
from fastapi.testclient import TestClient

from app import models, schemas
from app.constants import (
    SYSTEM_EMAIL,
    SYSTEM_UUID,
)
from app.main import app
from app.tests.medium.constants import (
    PTEAM1,
    TAG1,
    TAG2,
    TOPIC1,
    USER1,
)
from app.tests.medium.utils import (
    assert_200,
    assert_204,
    create_action,
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    file_upload_headers,
    headers,
    upload_pteam_tags,
)

client = TestClient(app)


def test_auto_close_topic():
    create_user(USER1)
    tag1 = create_tag(USER1, "test:tag:alpha")
    ext_tag1 = {
        "tag_name": tag1.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.3",
                "group": "Threatconnectome",
            },
            {"target": "api2/Pipfile.lock", "version": "1.4", "group": "Flashsense"},
        ],
    }
    tag2 = create_tag(USER1, "test:tag:bravo")
    ext_tag2 = {
        "tag_name": tag2.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.2.5",
                "group": "Threatconnectome",
            },
            {"target": "api2/Pipfile.lock", "version": "3.0.0", "group": "Threatconnectome"},
        ],
    }
    tag3 = create_tag(USER1, "test:tag:charlie")
    ext_tag3 = {
        "tag_name": tag3.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.0",
                "group": "Threatconnectome",
            },
            {
                "target": "api/Pipfile.lock",  # version is None
                "group": "Threatconnectome",
            },
        ],
    }
    tag4 = create_tag(USER1, "test:tag:delta")
    ext_tag4 = {
        "tag_name": tag4.tag_name,
        "references": [
            {
                "target": "",
                "version": "",
                "group": "fake group",
            },
        ],  # fake references
    }

    def _extract_ext_tags(
        _ext_tags: list[dict],
    ) -> tuple[
        dict[str, dict[str, list[tuple[str, str]]]],  # {group: {tag: [(refs tuple)...]}}
        dict[str, list[dict]],  # {tag: [references,...]}
    ]:
        _group_to_tags: dict[str, dict[str, list[tuple[str, str]]]] = {}
        _tag_to_refs_list: dict[str, list[dict]] = {}
        for _ext_tag in _ext_tags:
            _tag_name = _ext_tag["tag_name"]
            for _ref in _ext_tag["references"]:
                _group = _ref["group"]
                _target = _ref.get("target", "")
                _version = _ref.get("version", "")

                _tag_to_refs_dict = _group_to_tags.get(_group, {})
                _refs_tuples = _tag_to_refs_dict.get(_tag_name, [])
                _refs_tuples.append((_target, _version))
                _tag_to_refs_dict[_tag_name] = _refs_tuples
                _group_to_tags[_group] = _tag_to_refs_dict

                _refs_dict = _tag_to_refs_list.get(_tag_name, [])
                _refs_dict.append({"group": _group, "target": _target, "version": _version})
                _tag_to_refs_list[_tag_name] = _refs_dict
        return _group_to_tags, _tag_to_refs_list

    pteam1 = create_pteam(USER1, PTEAM1)
    req_tags, resp_tags = _extract_ext_tags([ext_tag1, ext_tag2, ext_tag3, ext_tag4])
    for group, refs in req_tags.items():
        upload_pteam_tags(USER1, pteam1.pteam_id, group, refs)

    action1 = {
        "action": "update alpha to version 1.3.1.",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.tag_name],
            "vulnerable_versions": {
                tag1.tag_name: [">=0 <1.3.1"],  # defined and match
            },
        },
    }
    action2 = {
        "action": "update bravo to version 1.2.4.",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag2.tag_name],
            "vulnerable_versions": {
                tag2.tag_name: [">=0 <1.2.4"],  # defined but not match
            },
        },
    }
    action3 = {
        "action": "uninstall charlie",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag3.tag_name],  # no vulnerable versions
        },
    }
    action4 = {
        "action": "update delta to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag4.tag_name],
            "vulnerable_versions": {
                tag4.tag_name: [">=0 <1.1"],  # defined (but missing pteamtags.versions)
            },
        },
    }
    action5 = {
        "action": "update bravo to version 2.0.1",
        "action_type": "mitigation",
        "recommended": False,
        "ext": {
            "tags": [tag2.tag_name],  # 2nd action for tag2
            "vulnerable_versions": {
                tag2.tag_name: [">= 2, <2.0.1"],  # defined but not match
            },
        },
    }
    actions = [action1, action2, action3, action4, action5]
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [tag1.tag_name, tag2.tag_name, tag3.tag_name, tag4.tag_name],
            "actions": actions,
        },
    )

    def actionlogs_find(logs_, target_):
        keys = ["action", "action_type", "recommended"]
        for log_ in logs_:
            if all((log_[key] == target_[key]) for key in keys):
                return log_
        return None

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 2
    log_2 = actionlogs_find(data["action_logs"], action2)
    assert log_2
    assert log_2["topic_id"] == str(topic1.topic_id)
    assert log_2["pteam_id"] == str(pteam1.pteam_id)
    assert log_2["user_id"] == str(SYSTEM_UUID)
    assert log_2["email"] == SYSTEM_EMAIL
    log_5 = actionlogs_find(data["action_logs"], action5)
    assert log_5
    assert log_5["topic_id"] == str(topic1.topic_id)
    assert log_5["pteam_id"] == str(pteam1.pteam_id)
    assert log_5["user_id"] == str(SYSTEM_UUID)
    assert log_5["email"] == SYSTEM_EMAIL

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag3.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag4.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0


def test_auto_close_topic__parent():
    create_user(USER1)
    tag1 = create_tag(USER1, "test:tag1:alpha")
    ext_tag1 = {
        "tag_name": tag1.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.3",
                "group": "Threatconnectome",
            },
            {"target": "api2/Pipfile.lock", "version": "1.4", "group": "Flashsense"},
        ],
    }
    tag2 = create_tag(USER1, "test:tag2:bravo")
    ext_tag2 = {
        "tag_name": tag2.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.2.5",
                "group": "Threatconnectome",
            },
            {"target": "api2/Pipfile.lock", "version": "3.0.0", "group": "Threatconnectome"},
        ],
    }
    tag3 = create_tag(USER1, "test:tag3:charlie")
    ext_tag3 = {
        "tag_name": tag3.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.0",
                "group": "Threatconnectome",
            },
            {
                "target": "api/Pipfile.lock",  # version is None
                "group": "Threatconnectome",
            },
        ],
    }
    tag4 = create_tag(USER1, "test:tag4:delta")
    ext_tag4 = {
        "tag_name": tag4.tag_name,
        "references": [
            {
                "target": "",
                "version": "",
                "group": "fake group",
            },
        ],  # fake references
    }

    def _extract_ext_tags(
        _ext_tags: list[dict],
    ) -> tuple[
        dict[str, dict[str, list[tuple[str, str]]]],  # {group: {tag: [(refs tuple)...]}}
        dict[str, list[dict]],  # {tag: [references,...]}
    ]:
        _group_to_tags: dict[str, dict[str, list[tuple[str, str]]]] = {}
        _tag_to_refs_list: dict[str, list[dict]] = {}
        for _ext_tag in _ext_tags:
            _tag_name = _ext_tag["tag_name"]
            for _ref in _ext_tag["references"]:
                _group = _ref["group"]
                _target = _ref.get("target", "")
                _version = _ref.get("version", "")

                _tag_to_refs_dict = _group_to_tags.get(_group, {})
                _refs_tuples = _tag_to_refs_dict.get(_tag_name, [])
                _refs_tuples.append((_target, _version))
                _tag_to_refs_dict[_tag_name] = _refs_tuples
                _group_to_tags[_group] = _tag_to_refs_dict

                _refs_dict = _tag_to_refs_list.get(_tag_name, [])
                _refs_dict.append({"group": _group, "target": _target, "version": _version})
                _tag_to_refs_list[_tag_name] = _refs_dict
        return _group_to_tags, _tag_to_refs_list

    pteam1 = create_pteam(USER1, PTEAM1)
    req_tags, resp_tags = _extract_ext_tags([ext_tag1, ext_tag2, ext_tag3, ext_tag4])
    for group, refs in req_tags.items():
        upload_pteam_tags(USER1, pteam1.pteam_id, group, refs)

    action1 = {
        "action": "update alpha to version 1.3.1.",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.parent_name],
            "vulnerable_versions": {
                tag1.parent_name: [">=0 <1.3.1"],  # defined and match
            },
        },
    }
    action2 = {
        "action": "update bravo to version 1.2.4.",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag2.parent_name],
            "vulnerable_versions": {
                tag2.parent_name: [">=0 <1.2.4"],  # defined but not match
            },
        },
    }
    action3 = {
        "action": "uninstall charlie",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag3.parent_name],  # no vulnerable versions
        },
    }
    action4 = {
        "action": "update delta to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag4.parent_name],
            "vulnerable_versions": {
                tag4.parent_name: [">=0 <1.1"],  # defined (but missing pteamtags.versions)
            },
        },
    }
    action5 = {
        "action": "update bravo to version 2.0.1",
        "action_type": "mitigation",
        "recommended": False,
        "ext": {
            "tags": [tag2.parent_name],  # 2nd action for tag2
            "vulnerable_versions": {
                tag2.parent_name: [">= 2, <2.0.1"],  # defined but not match
            },
        },
    }
    actions = [action1, action2, action3, action4, action5]
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [
                tag1.parent_name,
                tag2.parent_name,
                tag3.parent_name,
                tag4.parent_name,
            ],
            "actions": actions,
        },
    )

    def actionlogs_find(logs_, target_):
        keys = ["action", "action_type", "recommended"]
        for log_ in logs_:
            if all((log_[key] == target_[key]) for key in keys):
                return log_
        return None

    data = assert_200(
        client.get(
            f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
            headers=headers(USER1),
        )
    )
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 2
    log_2 = actionlogs_find(data["action_logs"], action2)
    assert log_2
    assert log_2["topic_id"] == str(topic1.topic_id)
    assert log_2["pteam_id"] == str(pteam1.pteam_id)
    assert log_2["user_id"] == str(SYSTEM_UUID)
    assert log_2["email"] == SYSTEM_EMAIL
    log_5 = actionlogs_find(data["action_logs"], action5)
    assert log_5
    assert log_5["topic_id"] == str(topic1.topic_id)
    assert log_5["pteam_id"] == str(pteam1.pteam_id)
    assert log_5["user_id"] == str(SYSTEM_UUID)
    assert log_5["email"] == SYSTEM_EMAIL

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag3.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag4.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0


def test_auto_close_by_pteamtags():
    create_user(USER1)
    tag1 = create_tag(USER1, "test:tag:alpha")
    ext_tag1 = {
        "tag_name": tag1.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.3",
                "group": "Threatconnectome",
            },
            {"target": "api2/Pipfile.lock", "version": "1.4", "group": "Flashsense"},
        ],
    }
    tag2 = create_tag(USER1, "test:tag:bravo")
    ext_tag2 = {
        "tag_name": tag2.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.2.5",
                "group": "Threatconnectome",
            },
            {"target": "api2/Pipfile.lock", "version": "3.0.0", "group": "Threatconnectome"},
        ],
    }
    tag3 = create_tag(USER1, "test:tag:charlie")
    ext_tag3 = {
        "tag_name": tag3.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.0",
                "group": "Threatconnectome",
            },
            {
                "target": "api/Pipfile.lock",  # version is None
                "group": "Threatconnectome",
            },
        ],
    }
    tag4 = create_tag(USER1, "test:tag:delta")
    ext_tag4 = {
        "tag_name": tag4.tag_name,
        "references": [
            {
                "target": "",
                "version": "",
                "group": "fake group",
            },
        ],
    }

    action1 = {
        "action": "update alpha to version 1.3.1.",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.tag_name],
            "vulnerable_versions": {
                tag1.tag_name: [">=0 <1.3.1"],  # defined and match
            },
        },
    }
    action2 = {
        "action": "update bravo to version 1.2.4.",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag2.tag_name],
            "vulnerable_versions": {
                tag2.tag_name: [">=0 <1.2.4"],  # defined but not match
            },
        },
    }
    action3 = {
        "action": "uninstall charlie",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag3.tag_name],  # no vulnerable versions
        },
    }
    action4 = {
        "action": "update delta to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag4.tag_name],
            "vulnerable_versions": {
                tag4.tag_name: [">=0 <1.1"],  # defined (but missing pteamtags.versions)
            },
        },
    }
    action5 = {
        "action": "update bravo to version 2.0.1",
        "action_type": "mitigation",
        "recommended": False,
        "ext": {
            "tags": [tag2.tag_name],  # 2nd action for tag2
            "vulnerable_versions": {
                tag2.tag_name: [">= 2, <2.0.1"],  # defined but not match
            },
        },
    }
    actions = [action1, action2, action3, action4, action5]
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [tag1.tag_name, tag2.tag_name, tag3.tag_name, tag4.tag_name],
            "actions": actions,
        },
    )

    def _extract_ext_tags(
        _ext_tags: list[dict],
    ) -> tuple[
        dict[str, dict[str, list[tuple[str, str]]]],  # {group: {tag: [(refs tuple)...]}}
        dict[str, list[dict]],  # {tag: [references,...]}
    ]:
        _group_to_tags: dict[str, dict[str, list[tuple[str, str]]]] = {}
        _tag_to_refs_list: dict[str, list[dict]] = {}
        for _ext_tag in _ext_tags:
            _tag_name = _ext_tag["tag_name"]
            for _ref in _ext_tag["references"]:
                _group = _ref["group"]
                _target = _ref.get("target", "")
                _version = _ref.get("version", "")

                _tag_to_refs_dict = _group_to_tags.get(_group, {})
                _refs_tuples = _tag_to_refs_dict.get(_tag_name, [])
                _refs_tuples.append((_target, _version))
                _tag_to_refs_dict[_tag_name] = _refs_tuples
                _group_to_tags[_group] = _tag_to_refs_dict

                _refs_dict = _tag_to_refs_list.get(_tag_name, [])
                _refs_dict.append({"group": _group, "target": _target, "version": _version})
                _tag_to_refs_list[_tag_name] = _refs_dict
        return _group_to_tags, _tag_to_refs_list

    # create pteam after creating topic
    pteam1 = create_pteam(USER1, PTEAM1)
    req_tags, resp_tags = _extract_ext_tags([ext_tag1, ext_tag2, ext_tag3, ext_tag4])
    for group, refs in req_tags.items():
        upload_pteam_tags(USER1, pteam1.pteam_id, group, refs)

    def actionlogs_find(logs_, target_):
        keys = ["action", "action_type", "recommended"]
        for log_ in logs_:
            if all((log_[key] == target_[key]) for key in keys):
                return log_
        return None

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 2
    log_2 = actionlogs_find(data["action_logs"], action2)
    assert log_2
    assert log_2["topic_id"] == str(topic1.topic_id)
    assert log_2["pteam_id"] == str(pteam1.pteam_id)
    assert log_2["user_id"] == str(SYSTEM_UUID)
    assert log_2["email"] == SYSTEM_EMAIL
    log_5 = actionlogs_find(data["action_logs"], action5)
    assert log_5
    assert log_5["topic_id"] == str(topic1.topic_id)
    assert log_5["pteam_id"] == str(pteam1.pteam_id)
    assert log_5["user_id"] == str(SYSTEM_UUID)
    assert log_5["email"] == SYSTEM_EMAIL

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag3.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag4.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0


def test_auto_close__on_upload_pteam_tags_file():
    create_user(USER1)
    pteam1 = create_pteam(USER1, {**PTEAM1, "tags": []})
    tag1 = create_tag(USER1, "test:tag:alpha")
    ext_tag1 = {
        "tag_name": tag1.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.1",  # not vulnerable
                "group": "Threatconnectome",
            }
        ],
    }
    tag2 = create_tag(USER1, "test:tag:bravo")
    ext_tag2 = {
        "tag_name": tag2.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.0",  # vulnerable
                "group": "Threatconnectome",
            }
        ],
    }
    action1 = {
        "action": "update alpha to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.tag_name],
            "vulnerable_versions": {
                tag1.tag_name: [">=0 <1.1"],
            },
        },
    }
    action2 = {
        "action": "update bravo to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag2.tag_name],
            "vulnerable_versions": {
                tag2.tag_name: [">=0 <1.1"],
            },
        },
    }
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [tag1.tag_name, tag2.tag_name],
            "actions": [action1, action2],
        },
    )
    params = {"group": "threatconnectome"}
    # first time
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tags_file:
        tags_file.writelines(json.dumps(ext_tag1) + "\n")  # none -> not vulnerable
        tags_file.writelines(json.dumps(ext_tag2) + "\n")  # none -> vulnerable
        tags_file.flush()
        tags_file.seek(0)
        with open(tags_file.name, "rb") as tags:
            response = client.post(
                f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                headers=file_upload_headers(USER1),
                files={"file": tags},
                params=params,
            )
    assert response.status_code == 200

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag1.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["topic_id"] == str(topic1.topic_id)
    assert data["action_logs"][0]["pteam_id"] == str(pteam1.pteam_id)
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)
    assert data["action_logs"][0]["email"] == SYSTEM_EMAIL
    last_executed_at = data["action_logs"][0]["executed_at"]

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    # second time (update)

    ext_tag2["references"][0]["version"] = "1.1"
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tags_file:
        tags_file.writelines(json.dumps(ext_tag1) + "\n")  # not changed (not vulnerable)
        tags_file.writelines(json.dumps(ext_tag2) + "\n")  # vulnerable -> not vulnerable
        tags_file.flush()
        tags_file.seek(0)
        with open(tags_file.name, "rb") as tags:
            response = client.post(
                f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                headers=file_upload_headers(USER1),
                files={"file": tags},
                params=params,
            )
    assert response.status_code == 200

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag1.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["topic_id"] == str(topic1.topic_id)
    assert data["action_logs"][0]["pteam_id"] == str(pteam1.pteam_id)
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)
    assert data["action_logs"][0]["email"] == SYSTEM_EMAIL
    assert data["action_logs"][0]["executed_at"] == last_executed_at  # not modified

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["topic_id"] == str(topic1.topic_id)
    assert data["action_logs"][0]["pteam_id"] == str(pteam1.pteam_id)
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)
    assert data["action_logs"][0]["email"] == SYSTEM_EMAIL


def test_auto_close__on_upload_pteam_tags_file__parent():
    create_user(USER1)
    pteam1 = create_pteam(USER1, {**PTEAM1, "tags": []})
    tag1 = create_tag(USER1, "test:tag1:alpha")
    ext_tag1 = {
        "tag_name": tag1.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.1",  # not vulnerable
                "group": "Threatconnectome",
            }
        ],
    }
    tag2 = create_tag(USER1, "test:tag2:bravo")
    ext_tag2 = {
        "tag_name": tag2.tag_name,
        "references": [
            {
                "target": "api/Pipfile.lock",
                "version": "1.0",  # vulnerable
                "group": "Threatconnectome",
            }
        ],
    }
    action1 = {
        "action": "update alpha to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.parent_name],
            "vulnerable_versions": {
                tag1.parent_name: [">=0 <1.1"],
            },
        },
    }
    action2 = {
        "action": "update bravo to version 1.1",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag2.parent_name],
            "vulnerable_versions": {
                tag2.parent_name: [">=0 <1.1"],
            },
        },
    }
    topic1 = create_topic(
        USER1,
        {
            **TOPIC1,
            "tags": [tag1.parent_name, tag2.parent_name],
            "actions": [action1, action2],
        },
    )
    params = {"group": "threatconnectome"}
    # first time
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tags_file:
        tags_file.writelines(json.dumps(ext_tag1) + "\n")  # none -> not vulnerable
        tags_file.writelines(json.dumps(ext_tag2) + "\n")  # none -> vulnerable
        tags_file.flush()
        tags_file.seek(0)
        with open(tags_file.name, "rb") as tags:
            response = client.post(
                f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                headers=file_upload_headers(USER1),
                files={"file": tags},
                params=params,
            )
    assert response.status_code == 200

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag1.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["topic_id"] == str(topic1.topic_id)
    assert data["action_logs"][0]["pteam_id"] == str(pteam1.pteam_id)
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)
    assert data["action_logs"][0]["email"] == SYSTEM_EMAIL
    last_executed_at = data["action_logs"][0]["executed_at"]

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] in {"alerted", None}
    assert len(data["action_logs"]) == 0

    # second time (update)

    ext_tag2["references"][0]["version"] = "1.1"
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tags_file:
        tags_file.writelines(json.dumps(ext_tag1) + "\n")  # not changed (not vulnerable)
        tags_file.writelines(json.dumps(ext_tag2) + "\n")  # vulnerable -> not vulnerable
        tags_file.flush()
        tags_file.seek(0)
        with open(tags_file.name, "rb") as tags:
            response = client.post(
                f"/pteams/{pteam1.pteam_id}/upload_tags_file",
                headers=file_upload_headers(USER1),
                files={"file": tags},
                params=params,
            )
    assert response.status_code == 200

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag1.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag1.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["topic_id"] == str(topic1.topic_id)
    assert data["action_logs"][0]["pteam_id"] == str(pteam1.pteam_id)
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)
    assert data["action_logs"][0]["email"] == SYSTEM_EMAIL
    assert data["action_logs"][0]["executed_at"] == last_executed_at  # not modified

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/topicstatus/{topic1.topic_id}/{tag2.tag_id}",
        headers=headers(USER1),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic_id"] == str(topic1.topic_id)
    assert data["pteam_id"] == str(pteam1.pteam_id)
    assert data["tag_id"] == str(tag2.tag_id)
    assert data["topic_status"] == "completed"
    assert data["note"] == "auto closed by system"
    assert data["user_id"] == str(SYSTEM_UUID)
    assert len(data["action_logs"]) == 1
    assert data["action_logs"][0]["topic_id"] == str(topic1.topic_id)
    assert data["action_logs"][0]["pteam_id"] == str(pteam1.pteam_id)
    assert data["action_logs"][0]["user_id"] == str(SYSTEM_UUID)
    assert data["action_logs"][0]["email"] == SYSTEM_EMAIL


class TestAutoClose:
    class _Util:
        @staticmethod
        def get_topic_status(
            pteam: schemas.PTeamInfo,
            topic: schemas.Topic,
            tag: schemas.TagResponse,
        ) -> schemas.TopicStatusResponse:
            data = assert_200(
                client.get(
                    f"/pteams/{pteam.pteam_id}/topicstatus/{topic.topic_id}/{tag.tag_id}",
                    headers=headers(USER1),
                )
            )
            return schemas.TopicStatusResponse(**data)

        @staticmethod
        def gen_action_dict(**kwargs) -> dict:
            action = {
                "action": "update alpha to 2.0",
                "action_type": "elimination",
                "recommended": True,
                "ext": {
                    "tags": [TAG1],
                    "vulnerable_versions": {
                        TAG1: [">=1.0 <2.0"],
                    },
                },
                **kwargs,
            }
            return action

        @staticmethod
        def gen_simple_ext(tag: str, vulnerables: list[str] | None) -> dict:
            ext: dict[str, Any] = {"tags": [tag]}
            if vulnerables is not None:
                ext.update({"vulnerable_versions": {tag: vulnerables}})
            return ext

    class TestEndpointTopics:
        class TestOnCreateTopic:
            pass  # see other test_auto_close*
            # TODO: implement or move tests here

        class TestOnUpdateTopic:
            util: Type
            tag1: schemas.TagResponse
            topic1: schemas.Topic
            action1: schemas.ActionResponse

            @pytest.fixture(scope="function", autouse=True)
            def common_setup(self):
                self.util = TestAutoClose._Util
                create_user(USER1)
                self.tag1 = create_tag(USER1, TAG1)
                topic1 = create_topic(
                    USER1,
                    {
                        **TOPIC1,
                        "tags": [TAG1],
                        "actions": [TestAutoClose._Util.gen_action_dict()],
                    },
                )
                self.action1 = topic1.actions[0]
                self.topic1 = topic1

    class TestEndpointActions:
        class TestOnCreateAction:
            util: Type
            pteam1: schemas.PTeamInfo
            tag1: schemas.TagResponse
            topic1: schemas.Topic

            @pytest.fixture(scope="function", autouse=True)
            def common_setup(self):
                self.util = TestAutoClose._Util
                create_user(USER1)
                self.tag1 = create_tag(USER1, TAG1)
                self.tag2 = create_tag(USER1, TAG2)
                self.pteam1 = create_pteam(USER1, PTEAM1)
                refs0 = {self.tag1.tag_name: [("Pipfile.lock", "2.1")]}
                upload_pteam_tags(USER1, self.pteam1.pteam_id, "group1", refs0)
                self.topic1 = create_topic(
                    USER1,
                    {
                        **TOPIC1,
                        "tags": [TAG1, TAG2],
                        "actions": [],
                    },
                )

            def test_add_action__matched(self) -> None:
                # topic1 alerted because of having no actions
                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status in {models.TopicStatusType.alerted, None}

                # test auto-close triggerd when new action created
                action1_dict = self.util.gen_action_dict()
                action1 = create_action(USER1, action1_dict, self.topic1.topic_id)

                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status == models.TopicStatusType.completed
                assert len(status.action_logs) == 1
                log0 = status.action_logs[0]
                assert log0.action_id == action1.action_id

                # test auto-close not triggered if already completed
                action2_dict = {
                    **action1_dict,
                    "action": action1_dict["action"] + "xxx",  # not to conflict action_id
                }
                create_action(USER1, action2_dict, self.topic1.topic_id)
                # status should not overwritten by action2
                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status == models.TopicStatusType.completed
                assert len(status.action_logs) == 1
                log0 = status.action_logs[0]
                assert log0.action_id == action1.action_id

            def test_add_action__not_matched(self) -> None:
                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status in {models.TopicStatusType.alerted, None}

                # test auto-close aborted if tag-matched action not found
                action1_dict = self.util.gen_action_dict(
                    ext=self.util.gen_simple_ext(TAG2, [">=1.0 <2.0"])
                )
                create_action(USER1, action1_dict, self.topic1.topic_id)

                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status in {models.TopicStatusType.alerted, None}

                # test auto-close pick only matched actions
                action2_dict = {
                    **action1_dict,
                    "action": action1_dict["action"] + "xxx",  # not to conflict action_id
                    "ext": self.util.gen_simple_ext(TAG1, [">=1 <2.0"]),
                }
                action2 = create_action(USER1, action2_dict, self.topic1.topic_id)

                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status == models.TopicStatusType.completed
                assert len(status.action_logs) == 1
                log0 = status.action_logs[0]
                assert log0.action_id == action2.action_id

        class TestOnDeleteAction:
            util: Type
            pteam1: schemas.PTeamInfo
            tag1: schemas.TagResponse
            topic1: schemas.Topic

            @pytest.fixture(scope="function", autouse=True)
            def common_setup(self):
                self.util = TestAutoClose._Util
                create_user(USER1)
                self.tag1 = create_tag(USER1, TAG1)
                self.tag2 = create_tag(USER1, TAG2)
                self.pteam1 = create_pteam(USER1, PTEAM1)
                refs0 = {self.tag1.tag_name: [("Pipfile.lock", "2.1")]}
                upload_pteam_tags(USER1, self.pteam1.pteam_id, "group1", refs0)
                self.topic1 = create_topic(
                    USER1,
                    {
                        **TOPIC1,
                        "tags": [TAG1, TAG2],
                        "actions": [],
                    },
                )

            def test_delete_action(self) -> None:
                # topic1 alerted because of having no actions
                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status in {models.TopicStatusType.alerted, None}

                # new action created with uncomparable version
                action1_dict = self.util.gen_action_dict(
                    ext=self.util.gen_simple_ext(TAG1, [">=alpha <charlie"])
                )
                action1 = create_action(USER1, action1_dict, self.topic1.topic_id)

                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status in {models.TopicStatusType.alerted, None}

                # new action created with comparable version
                action2_dict = self.util.gen_action_dict(
                    ext=self.util.gen_simple_ext(TAG1, [">=1.0 <2.0"])
                )
                action2 = create_action(USER1, action2_dict, self.topic1.topic_id)
                # action1 still blocks auto-close
                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status in {models.TopicStatusType.alerted, None}

                # delete action1
                assert_204(client.delete(f"/actions/{action1.action_id}", headers=headers(USER1)))
                # now topic1 can be closed with action2
                status = self.util.get_topic_status(self.pteam1, self.topic1, self.tag1)
                assert status.topic_status == models.TopicStatusType.completed
                assert len(status.action_logs) == 1
                log0 = status.action_logs[0]
                assert log0.action_id == action2.action_id

    class TestEndpointPTeams:
        class TestOnCreatePTeam:
            pass  # see other test_auto_close*
            # TODO: implement or move tests here

        class TestOnUpdatePTeam:
            pass  # see other test_auto_close*
            # TODO: implement or move tests here

        class TestOnAddPTeamTag:
            pass  # see test_auto_close__on_add_pteamtag*
            # TODO: implement or move tests here

        class TestOnUpdatePTeamTag:
            pass  # see test_auto_close__on_update_pteamtag*
            # TODO: implement or move tests here

        class TestOnUploadTagsFile:
            pass  # see test_auto_close__on_upload_pteam_tags_file*
            # TODO: implement or move tests here
