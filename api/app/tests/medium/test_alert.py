from typing import List, Sequence
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app import models, schemas
from app.alert import (
    _pick_alert_targets_for_new_topic,
    create_mail_alert_for_new_topic,
)
from app.constants import DEFAULT_ALERT_THREAT_IMPACT, SYSTEM_EMAIL
from app.main import app
from app.tests.medium.constants import (
    GROUP1,
    SAMPLE_SLACK_WEBHOOK_URL,
    USER1,
)
from app.tests.medium.utils import (
    assert_200,
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    headers,
    upload_pteam_tags,
)

client = TestClient(app)


def test_pick_alert_target_for_new_topic__tags(testdb) -> None:
    create_user(USER1)
    parent_tag1 = create_tag(USER1, "pkg1:info1:")
    child_tag11 = create_tag(USER1, "pkg1:info1:mgr1")
    child_tag12 = create_tag(USER1, "pkg1:info1:mgr2")
    parent_tag2 = create_tag(USER1, "pkg2:info1:")
    child_tag21 = create_tag(USER1, "pkg2:info1:mgr1")

    pteam_tags_patterns: List[List[schemas.TagResponse]] = [
        [],  # 0
        [parent_tag1],  # 1
        [child_tag11],  # 2
        [child_tag12],  # 3
        [parent_tag2],  # 4
        [child_tag21],  # 5
        [parent_tag1, child_tag11],  # 6
        [parent_tag1, parent_tag2],  # 7
        [parent_tag1, child_tag21],  # 8
        [parent_tag2, child_tag11],  # 9
        [parent_tag2, child_tag21],  # 10
        [parent_tag1],  # 11 (for disabled)
    ]

    def _gen_pteam_params(idx: int) -> dict:
        return {
            "pteam_name": f"pteam{idx}",
            "alert_slack": {
                "enable": True,
                "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx),
            },
            "alert_mail": {
                "enable": True,
                "address": f"account{idx}@example.com",
            },
            "alert_threat_impact": DEFAULT_ALERT_THREAT_IMPACT,
        }

    def _gen_topic_params(tags: List[schemas.TagResponse]) -> dict:
        topic_id = str(uuid4())
        return {
            "topic_id": topic_id,
            "title": "test topic " + topic_id,
            "abstract": "test abstract " + topic_id,
            "threat_impact": 1,
            "tags": [tag.tag_name for tag in tags],
            "misp_tags": [],
            "actions": [],
        }

    def _find_expected(
        _targets: Sequence[models.CurrentPTeamTopicTagStatus],
        idx: int,
        tag: schemas.TagResponse,
    ) -> bool:
        return any(
            _tgt.pteam.pteam_name == f"pteam{idx}" and _tgt.tag.tag_name == tag.tag_name
            for _tgt in _targets
        )

    pteams: List[schemas.PTeamInfo] = []
    for idx in range(len(pteam_tags_patterns)):
        pteams.append(create_pteam(USER1, _gen_pteam_params(idx)))
        if pteam_tags := pteam_tags_patterns[idx]:
            ext_tags = {tag.tag_name: [("api/Pipfile.lock", "1.0.0")] for tag in pteam_tags}
            upload_pteam_tags(USER1, pteams[idx].pteam_id, GROUP1, ext_tags)
    # disable pteams[11]
    db_pteam11 = testdb.execute(
        select(models.PTeam).where(models.PTeam.pteam_id == str(pteams[11].pteam_id))
    ).one()[0]
    db_pteam11.disabled = True
    testdb.add(db_pteam11)
    testdb.commit()

    # topic0: no tags
    topic = create_topic(USER1, _gen_topic_params([]))
    alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
    assert alert_targets == []

    # topic1: has parent_tag1  --> alerted to watching parent_tag1 or child_tag1*
    topic = create_topic(USER1, _gen_topic_params([parent_tag1]))
    alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
    assert len(alert_targets) == 8
    assert _find_expected(alert_targets, 1, parent_tag1)
    assert _find_expected(alert_targets, 2, child_tag11)
    assert _find_expected(alert_targets, 3, child_tag12)
    assert _find_expected(alert_targets, 6, parent_tag1)
    assert _find_expected(alert_targets, 6, child_tag11)  # matches multiple
    assert _find_expected(alert_targets, 7, parent_tag1)
    assert _find_expected(alert_targets, 8, parent_tag1)
    assert _find_expected(alert_targets, 9, child_tag11)

    # topic2: has child_tag11  --> alerted to watching child_tag11
    topic = create_topic(USER1, _gen_topic_params([child_tag11]))
    alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
    assert len(alert_targets) == 3
    assert _find_expected(alert_targets, 2, child_tag11)
    assert _find_expected(alert_targets, 6, child_tag11)
    assert _find_expected(alert_targets, 9, child_tag11)

    # topic3: has child_tag12 + parent_tag2  --> alerted to child_tag12, parent_tag2, child_tag2*
    topic = create_topic(USER1, _gen_topic_params([child_tag12, parent_tag2]))
    alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
    assert len(alert_targets) == 8
    assert _find_expected(alert_targets, 3, child_tag12)
    assert _find_expected(alert_targets, 4, parent_tag2)
    assert _find_expected(alert_targets, 5, child_tag21)
    assert _find_expected(alert_targets, 7, parent_tag2)
    assert _find_expected(alert_targets, 8, child_tag21)
    assert _find_expected(alert_targets, 9, parent_tag2)
    assert _find_expected(alert_targets, 10, parent_tag2)
    assert _find_expected(alert_targets, 10, child_tag21)  # matches multiple


def test_pick_alert_target_for_new_topic__threshold(testdb) -> None:
    create_user(USER1)
    parent_tag1 = create_tag(USER1, "pkg1:info1:")
    child_tag11 = create_tag(USER1, "pkg1:info1:mgr1")

    def _gen_pteam_params(idx: int) -> dict:
        return {
            "pteam_name": f"pteam{idx}",
            "alert_slack": {
                "enable": True,
                "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx),
            },
            "alert_mail": {
                "enable": True,
                "address": f"account{idx}@example.com",
            },
            "alert_threat_impact": idx if idx in range(1, 5) else DEFAULT_ALERT_THREAT_IMPACT,
        }

    def _gen_topic_params(impact: int) -> dict:
        topic_id = str(uuid4())
        return {
            "topic_id": topic_id,
            "title": "test topic " + topic_id,
            "abstract": "test abstract " + topic_id,
            "threat_impact": impact,
            "tags": [parent_tag1.tag_name],
            "misp_tags": [],
            "actions": [],
        }

    def _find_expected(
        _targets: Sequence[models.CurrentPTeamTopicTagStatus],
        idx: int,
        tag: schemas.TagResponse,
    ) -> bool:
        return any(
            _tgt.pteam.pteam_name == f"pteam{idx}" and _tgt.tag.tag_name == tag.tag_name
            for _tgt in _targets
        )

    pteams: List[schemas.PTeamInfo] = []
    for idx in range(0, 5):  # 0 for disabled
        pteams.append(create_pteam(USER1, _gen_pteam_params(idx)))
        ext_tags = {child_tag11.tag_name: [("api/Pipfile.lock", "1.0.0")]}
        upload_pteam_tags(USER1, pteams[idx].pteam_id, GROUP1, ext_tags)
    # disable pteams[0]
    db_pteam0 = testdb.execute(
        select(models.PTeam).where(models.PTeam.pteam_id == str(pteams[0].pteam_id))
    ).one()[0]
    db_pteam0.disabled = True
    testdb.add(db_pteam0)
    testdb.commit()

    # topic0: threshold=1
    topic = create_topic(USER1, _gen_topic_params(1))
    alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
    assert len(alert_targets) == 4
    assert _find_expected(alert_targets, 1, child_tag11)
    assert _find_expected(alert_targets, 2, child_tag11)
    assert _find_expected(alert_targets, 3, child_tag11)
    assert _find_expected(alert_targets, 4, child_tag11)

    # topic0: threshold=2
    topic = create_topic(USER1, _gen_topic_params(2))
    alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
    assert len(alert_targets) == 3
    assert _find_expected(alert_targets, 2, child_tag11)
    assert _find_expected(alert_targets, 3, child_tag11)
    assert _find_expected(alert_targets, 4, child_tag11)

    # topic0: threshold=3
    topic = create_topic(USER1, _gen_topic_params(3))
    alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
    assert len(alert_targets) == 2
    assert _find_expected(alert_targets, 3, child_tag11)
    assert _find_expected(alert_targets, 4, child_tag11)

    # topic0: threshold=4
    topic = create_topic(USER1, _gen_topic_params(4))
    alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
    assert len(alert_targets) == 1
    assert _find_expected(alert_targets, 4, child_tag11)


def test_pick_alert_target_for_new_topic__auto_closed(testdb) -> None:
    create_user(USER1)
    parent_tag1 = create_tag(USER1, "pkg1:info1:")
    child_tag11 = create_tag(USER1, "pkg1:info1:mgr1")
    parent_tag2 = create_tag(USER1, "pkg2:info1:")
    child_tag21 = create_tag(USER1, "pkg2:info1:mgr1")

    def _gen_pteam_params(idx: int) -> dict:
        return {
            "pteam_name": f"pteam{idx}",
            "alert_slack": {
                "enable": True,
                "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx),
            },
            "alert_mail": {
                "enable": True,
                "address": f"account{idx}@example.com",
            },
            "alert_threat_impact": DEFAULT_ALERT_THREAT_IMPACT,
        }

    def _gen_topic_params(tags: List[schemas.TagResponse]) -> dict:
        topic_id = str(uuid4())
        return {
            "topic_id": topic_id,
            "title": "test topic " + topic_id,
            "abstract": "test abstract " + topic_id,
            "threat_impact": 1,
            "tags": [tag.tag_name for tag in tags],
            "misp_tags": [],
            "actions": [],
        }

    def _find_expected(
        _targets: Sequence[models.CurrentPTeamTopicTagStatus],
        idx: int,
        tag: schemas.TagResponse,
    ) -> bool:
        return any(
            _tgt.pteam.pteam_name == f"pteam{idx}" and _tgt.tag.tag_name == tag.tag_name
            for _tgt in _targets
        )

    pteam0 = create_pteam(USER1, _gen_pteam_params(0))
    ext_tags = {
        child_tag11.tag_name: [("api/Pipfile.lock", "1.0.0")],
        child_tag21.tag_name: [("api/Pipfile.lock", "1.0.0")],
    }
    upload_pteam_tags(USER1, pteam0.pteam_id, GROUP1, ext_tags)

    action1_closable = {
        "action": "action one",
        "action_type": models.ActionType.elimination,
        "recommended": True,
        "ext": {
            "tags": [child_tag11.tag_name],
            "vulnerable_versions": {child_tag11.tag_name: ["< 1.0.0"]},  # closable
        },
    }
    action2_unclosable = {
        "action": "action two",
        "action_type": models.ActionType.elimination,
        "recommended": True,
        "ext": {
            "tags": [child_tag21.tag_name],
            "vulnerable_versions": {child_tag21.tag_name: ["< 2.0.0"]},  # unclosable
        },
    }

    # topic0: has parent_tag1 with closable action1
    topic = create_topic(USER1, _gen_topic_params([parent_tag1]), actions=[action1_closable])
    alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
    assert alert_targets == []

    # topic1: has parent_tag2 with unclosable action2
    topic = create_topic(USER1, _gen_topic_params([parent_tag2]), actions=[action2_unclosable])
    alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
    assert len(alert_targets) == 1
    assert _find_expected(alert_targets, 0, child_tag21)

    # topic2: complex
    topic = create_topic(
        USER1,
        _gen_topic_params([parent_tag1, parent_tag2]),
        actions=[action1_closable, action2_unclosable],
    )
    alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
    assert len(alert_targets) == 1
    assert _find_expected(alert_targets, 0, child_tag21)  # alert only uncompleted


def test_alert_new_topic__by_mail(mocker) -> None:
    create_user(USER1)
    parent_tag1 = create_tag(USER1, "pkg1:info1:")
    child_tag11 = create_tag(USER1, "pkg1:info1:mgr1")

    def _gen_pteam_params(idx: int) -> dict:
        return {
            "pteam_name": f"pteam{idx}",
            "alert_slack": {
                "enable": True,
                "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx),
            },
            "alert_mail": {
                "enable": True,
                "address": f"account{idx}@example.com",
            },
            "alert_threat_impact": DEFAULT_ALERT_THREAT_IMPACT,
        }

    def _gen_topic_params(tags: List[schemas.TagResponse]) -> dict:
        topic_id = str(uuid4())
        return {
            "topic_id": topic_id,
            "title": "test topic " + topic_id,
            "abstract": "test abstract " + topic_id,
            "threat_impact": 1,
            "tags": [tag.tag_name for tag in tags],
            "misp_tags": [],
            "actions": [],
        }

    def _find_expected(
        _targets: Sequence[models.CurrentPTeamTopicTagStatus],
        idx: int,
        tag: schemas.TagResponse,
    ) -> bool:
        return any(
            _tgt.pteam.pteam_name == f"pteam{idx}" and _tgt.tag.tag_name == tag.tag_name
            for _tgt in _targets
        )

    pteam0 = create_pteam(USER1, _gen_pteam_params(0))
    ext_tags = {child_tag11.tag_name: [("api/Pipfile.lock", "1.0.0")]}
    upload_pteam_tags(USER1, pteam0.pteam_id, GROUP1, ext_tags)

    # topic0: no tags
    send_email = mocker.patch("app.alert.send_email")
    create_topic(USER1, _gen_topic_params([]))
    send_email.assert_not_called()

    # topic1: parent_tag1
    send_email = mocker.patch("app.alert.send_email")  # reset
    topic1 = create_topic(USER1, _gen_topic_params([parent_tag1]))
    exp_to_email = pteam0.alert_mail.address
    exp_from_email = SYSTEM_EMAIL
    exp_subject, exp_body = create_mail_alert_for_new_topic(
        topic1.title,
        topic1.threat_impact,
        pteam0.pteam_name,
        pteam0.pteam_id,
        child_tag11.tag_name,  # pteamtag, not topictag
        child_tag11.tag_id,  # pteamtag, not topictag
        [GROUP1],
    )
    send_email.assert_called_once()
    send_email.assert_called_with(exp_to_email, exp_from_email, exp_subject, exp_body)

    # disable alert_mail
    request = {"alert_mail": {"enable": False, "address": pteam0.alert_mail.address}}
    assert_200(client.put(f"/pteams/{pteam0.pteam_id}", headers=headers(USER1), json=request))
    send_email = mocker.patch("app.alert.send_email")  # reset
    create_topic(USER1, _gen_topic_params([parent_tag1]))
    send_email.assert_not_called()

    # enable alert_mail again
    request = {"alert_mail": {"enable": True, "address": pteam0.alert_mail.address}}
    assert_200(client.put(f"/pteams/{pteam0.pteam_id}", headers=headers(USER1), json=request))
    send_email = mocker.patch("app.alert.send_email")  # reset
    topic3 = create_topic(USER1, _gen_topic_params([parent_tag1]))
    exp_to_email = pteam0.alert_mail.address
    exp_from_email = SYSTEM_EMAIL
    exp_subject, exp_body = create_mail_alert_for_new_topic(
        topic3.title,
        topic3.threat_impact,
        pteam0.pteam_name,
        pteam0.pteam_id,
        child_tag11.tag_name,  # pteamtag, not topictag
        child_tag11.tag_id,  # pteamtag, not topictag
        [GROUP1],
    )
    send_email.assert_called_once()
    send_email.assert_called_with(exp_to_email, exp_from_email, exp_subject, exp_body)
