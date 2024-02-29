import json
from typing import List
from uuid import uuid4

import httpretty

from app import models, schemas
from app.constants import DEFAULT_ALERT_THREAT_IMPACT
from app.slack import (
    _create_blocks_for_ateam,
    _create_blocks_for_pteam,
    _pick_alert_targets_for_pteam,
    alert_new_topic,
    alert_to_ateam,
)
from app.tests.medium.constants import (
    ACTION1,
    ACTION2,
    ATEAM1,
    GROUP1,
    GTEAM1,
    PTEAM1,
    SAMPLE_SLACK_WEBHOOK_URL,
    TAG1,
    TOPIC1,
    USER1,
)
from app.tests.medium.utils import (
    accept_watching_request,
    create_action,
    create_ateam,
    create_gteam,
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    create_watching_request,
    create_zone,
    upload_pteam_tags,
)


def test_alert_new_topics(testdb):
    create_user(USER1)

    PTEAM1_WITH_SLACK_WEBHOOK_URL = {
        **PTEAM1,
        "alert_slack": {"enable": True, "webhook_url": SAMPLE_SLACK_WEBHOOK_URL},
    }
    pteam1 = create_pteam(USER1, PTEAM1_WITH_SLACK_WEBHOOK_URL)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("api/Pipfile.lock", "1.0.0")]}, True)
    create_topic(
        USER1,
        TOPIC1,
        actions=[ACTION1, ACTION2],
    )
    topic = testdb.query(models.Topic).first()
    testdb.query(models.Account).first()
    pteam = testdb.query(models.PTeam).first()

    with httpretty.enabled():
        httpretty.register_uri(
            httpretty.POST, PTEAM1_WITH_SLACK_WEBHOOK_URL["alert_slack"]["webhook_url"], body="OK"
        )
        alert_new_topic(testdb, topic)
        assert httpretty.last_request().method == "POST"
        assert (
            httpretty.last_request().url
            == PTEAM1_WITH_SLACK_WEBHOOK_URL["alert_slack"]["webhook_url"]
        )

        # assert posted data contains results of _create_blocks_for_pteam
        expected_blocks = _create_blocks_for_pteam(
            pteam_id=pteam.pteam_id,
            pteam_name=pteam.pteam_name,
            tag_id=topic.tags[0].tag_id,
            tag_name=topic.tags[0].tag_name,
            topic_id=topic.topic_id,
            title=topic.title,
            threat_impact=topic.threat_impact,
        )
        assert (
            json.loads(httpretty.last_request().body.decode("utf-8"))["blocks"] == expected_blocks
        )


def test_alert_new_topics__auto_closed(testdb):
    create_user(USER1)
    tag1 = create_tag(USER1, "testpkg:testinfo:testmgr")

    pteam1 = create_pteam(
        USER1, {**PTEAM1, "alert_slack": {"enable": True, "webhook_url": SAMPLE_SLACK_WEBHOOK_URL}}
    )
    refs0 = {tag1.tag_name: [("test/target1", "1.0")]}
    upload_pteam_tags(USER1, pteam1.pteam_id, "test group", refs0)

    action1 = {
        "action": "update testpkg to version 1.0",
        "action_type": "elimination",
        "recommended": True,
        "ext": {
            "tags": [tag1.tag_name],
            "vulnerable_versions": {
                tag1.tag_name: [">0 <1.0"],
            },
        },
    }
    create_topic(USER1, {**TOPIC1, "tags": [tag1.parent_name], "actions": [action1]})
    db_topic1 = testdb.query(models.Topic).one()

    current_status = (
        testdb.query(models.CurrentPTeamTopicTagStatus.topic_status)
        .filter(
            models.CurrentPTeamTopicTagStatus.topic_id == db_topic1.topic_id,
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam1.pteam_id),
            models.CurrentPTeamTopicTagStatus.tag_id == str(tag1.tag_id),
        )
        .scalar()
    )
    assert current_status == models.TopicStatusType.completed  # auto closed

    with httpretty.enabled():
        httpretty.register_uri(httpretty.POST, pteam1.alert_slack.webhook_url, body="OK")
        alert_new_topic(testdb, db_topic1)
        assert not httpretty.has_request()


def test_pick_alert_targets__tags(testdb) -> None:
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
            "alert_slack": {"enable": True, "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx)},
            "alert_threat_impact": DEFAULT_ALERT_THREAT_IMPACT,
        }

    def _gen_topic_params(tags: List[schemas.TagResponse]) -> dict:
        return {
            "topic_id": uuid4(),
            "title": "test topic",
            "abstract": "test abstract",
            "threat_impact": 1,
            "tags": [tag.tag_name for tag in tags],
            "misp_tags": [],
            "zone_names": [],
            "actions": [],
        }

    def _select_topic(topic: schemas.TopicCreateResponse) -> models.Topic:
        return testdb.query(models.Topic).filter(models.Topic.topic_id == str(topic.topic_id)).one()

    pteams: List[schemas.PTeamInfo] = []
    for idx in range(len(pteam_tags_patterns)):
        pteams.append(create_pteam(USER1, _gen_pteam_params(idx)))
        ext_tags = {}
        for tag in pteam_tags_patterns[idx]:
            ext_tags[tag.tag_name] = [("api/Pipfile.lock", "1.0.0")]
        if len(pteam_tags_patterns[idx]) != 0:
            upload_pteam_tags(USER1, pteams[idx].pteam_id, GROUP1, ext_tags, True)
    # disable pteams[11]
    db_pteam11 = (
        testdb.query(models.PTeam).filter(models.PTeam.pteam_id == str(pteams[11].pteam_id)).one()
    )
    db_pteam11.disabled = True
    testdb.add(db_pteam11)
    testdb.commit()

    def _expected_alert_target(idx: int, tag: schemas.TagResponse) -> dict:
        return {
            "pteam_name": f"pteam{idx}",
            "slack_webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx),
            "pteam_id": str(pteams[idx].pteam_id),
            "tag_id": str(tag.tag_id),
            "tag_name": tag.tag_name,
        }

    # TOPIC0: no tags
    topic = create_topic(USER1, _gen_topic_params([]))
    db_topic = _select_topic(topic)
    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 0

    # TOPIC1: parent_tag1  -> parent_tag1 & child_tag1*
    topic = create_topic(USER1, _gen_topic_params([parent_tag1]))
    db_topic = _select_topic(topic)
    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 8
    assert _expected_alert_target(1, parent_tag1) in alert_targets
    assert _expected_alert_target(2, child_tag11) in alert_targets
    assert _expected_alert_target(3, child_tag12) in alert_targets
    assert _expected_alert_target(6, parent_tag1) in alert_targets
    assert _expected_alert_target(6, child_tag11) in alert_targets  # matches multiple
    assert _expected_alert_target(7, parent_tag1) in alert_targets
    assert _expected_alert_target(8, parent_tag1) in alert_targets
    assert _expected_alert_target(9, child_tag11) in alert_targets

    # TOPIC2: child_tag11  -> child_tag11 only
    topic = create_topic(USER1, _gen_topic_params([child_tag11]))
    db_topic = _select_topic(topic)
    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 3
    assert _expected_alert_target(2, child_tag11) in alert_targets
    assert _expected_alert_target(6, child_tag11) in alert_targets
    assert _expected_alert_target(9, child_tag11) in alert_targets

    # TOPIC3: child_tag12 + parent_tag2 -> child_tag12, parent_tag2 & child_tag2*
    topic = create_topic(USER1, _gen_topic_params([child_tag12, parent_tag2]))
    db_topic = _select_topic(topic)
    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 8
    assert _expected_alert_target(3, child_tag12) in alert_targets
    assert _expected_alert_target(4, parent_tag2) in alert_targets
    assert _expected_alert_target(5, child_tag21) in alert_targets
    assert _expected_alert_target(7, parent_tag2) in alert_targets
    assert _expected_alert_target(8, child_tag21) in alert_targets
    assert _expected_alert_target(9, parent_tag2) in alert_targets
    assert _expected_alert_target(10, parent_tag2) in alert_targets
    assert _expected_alert_target(10, child_tag21) in alert_targets  # matched multiple


def test_pick_alert_targets__threshold(testdb) -> None:
    create_user(USER1)
    parent_tag1 = create_tag(USER1, "pkg1:info1:")
    child_tag11 = create_tag(USER1, "pkg1:info1:mgr1")

    def _gen_pteam_params(idx: int) -> dict:
        return {
            "pteam_name": f"pteam{idx}",
            "alert_slack": {
                "enable": True,
                "webhook_url": "" if idx == 0 else SAMPLE_SLACK_WEBHOOK_URL + str(idx),
            },
            "alert_threat_impact": idx if idx in range(1, 5) else DEFAULT_ALERT_THREAT_IMPACT,
        }

    def _gen_topic_params(impact: int) -> dict:
        return {
            "topic_id": uuid4(),
            "title": "test topic",
            "abstract": "test abstract",
            "threat_impact": impact,
            "tags": [parent_tag1.tag_name],
            "misp_tags": [],
            "zone_names": [],
            "actions": [],
        }

    def _select_topic(topic: schemas.TopicCreateResponse) -> models.Topic:
        return testdb.query(models.Topic).filter(models.Topic.topic_id == str(topic.topic_id)).one()

    pteams: List[schemas.PTeamInfo] = []
    for idx in range(0, 6):  # 0 for no webhook_url, 5 for disable
        pteams.append(create_pteam(USER1, _gen_pteam_params(idx)))
        upload_pteam_tags(
            USER1,
            pteams[idx].pteam_id,
            GROUP1,
            {child_tag11.tag_name: [("api/Pipfile.lock", "1.0.0")]},
            True,
        )
    # disable pteams[5]
    db_pteam5 = (
        testdb.query(models.PTeam).filter(models.PTeam.pteam_id == str(pteams[5].pteam_id)).one()
    )
    db_pteam5.disabled = True
    testdb.add(db_pteam5)
    testdb.commit()

    def _expected_alert_target(idx: int) -> dict:
        return {
            "pteam_name": f"pteam{idx}",
            "slack_webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx),
            "pteam_id": str(pteams[idx].pteam_id),
            "tag_id": str(child_tag11.tag_id),
            "tag_name": child_tag11.tag_name,
        }

    # TOPIC0: impact=1
    topic = create_topic(USER1, _gen_topic_params(1))
    db_topic = _select_topic(topic)
    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 4
    assert _expected_alert_target(1) in alert_targets
    assert _expected_alert_target(2) in alert_targets
    assert _expected_alert_target(3) in alert_targets
    assert _expected_alert_target(4) in alert_targets

    # TOPIC1: impact=2
    topic = create_topic(USER1, _gen_topic_params(2))
    db_topic = _select_topic(topic)
    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 3
    assert _expected_alert_target(2) in alert_targets
    assert _expected_alert_target(3) in alert_targets
    assert _expected_alert_target(4) in alert_targets

    # TOPIC2: impact=3
    topic = create_topic(USER1, _gen_topic_params(3))
    db_topic = _select_topic(topic)
    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 2
    assert _expected_alert_target(3) in alert_targets
    assert _expected_alert_target(4) in alert_targets

    # TOPIC3: impact=4
    topic = create_topic(USER1, _gen_topic_params(4))
    db_topic = _select_topic(topic)
    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 1
    assert _expected_alert_target(4) in alert_targets


def test_pick_alert_targets__zones(testdb) -> None:
    create_user(USER1)
    parent_tag1 = create_tag(USER1, "pkg1:info1:")
    child_tag11 = create_tag(USER1, "pkg1:info1:mgr1")
    gteam1 = create_gteam(USER1, GTEAM1)

    def _gen_zone_params(idx: int) -> dict:
        return {
            "zone_name": f"test zone {idx}",
            "zone_info": f"test zone info {idx}",
        }

    zone1 = create_zone(USER1, gteam1.gteam_id, _gen_zone_params(1))
    zone2 = create_zone(USER1, gteam1.gteam_id, _gen_zone_params(2))
    zone3 = create_zone(USER1, gteam1.gteam_id, _gen_zone_params(3))

    pteam_zones_patterns: List[List[schemas.ZoneInfo]] = [
        [],  # 0
        [zone1],  # 1
        [zone2],  # 2
        [zone3],  # 3
        [zone1, zone2],  # 4
        [zone1, zone3],  # 5
        [zone2, zone3],  # 6
        [zone1, zone2, zone3],  # 7
        [zone1, zone2, zone3],  # 8 (for disabled)
    ]

    def _gen_pteam_params(idx: int) -> dict:
        zones = pteam_zones_patterns[idx]
        return {
            "pteam_name": f"pteam{idx}",
            "alert_slack": {"enable": True, "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx)},
            "alert_threat_impact": DEFAULT_ALERT_THREAT_IMPACT,
            "zone_names": [zone.zone_name for zone in zones],
        }

    def _gen_topic_params(zones: List[schemas.ZoneInfo]) -> dict:
        return {
            "topic_id": uuid4(),
            "title": "test topic",
            "abstract": "test abstract",
            "threat_impact": 1,
            "tags": [parent_tag1.tag_name],
            "misp_tags": [],
            "zone_names": [zone.zone_name for zone in zones],
            "actions": [],
        }

    def _select_topic(topic: schemas.TopicCreateResponse) -> models.Topic:
        return testdb.query(models.Topic).filter(models.Topic.topic_id == str(topic.topic_id)).one()

    pteams: List[schemas.PTeamInfo] = []
    for idx in range(len(pteam_zones_patterns)):
        pteams.append(create_pteam(USER1, _gen_pteam_params(idx)))
        upload_pteam_tags(
            USER1,
            pteams[idx].pteam_id,
            GROUP1,
            {child_tag11.tag_name: [("api/Pipfile.lock", "1.0.0")]},
            True,
        )
    # disable pteams[8]
    db_pteam8 = (
        testdb.query(models.PTeam).filter(models.PTeam.pteam_id == str(pteams[8].pteam_id)).one()
    )
    db_pteam8.disabled = True
    testdb.add(db_pteam8)
    testdb.commit()

    def _expected_alert_target(idx: int) -> dict:
        return {
            "pteam_name": f"pteam{idx}",
            "slack_webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx),
            "pteam_id": str(pteams[idx].pteam_id),
            "tag_id": str(child_tag11.tag_id),
            "tag_name": child_tag11.tag_name,
        }

    # TOPIC0: no zone
    topic = create_topic(USER1, _gen_topic_params([]))
    db_topic = _select_topic(topic)
    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 8
    assert _expected_alert_target(0) in alert_targets
    assert _expected_alert_target(1) in alert_targets
    assert _expected_alert_target(2) in alert_targets
    assert _expected_alert_target(3) in alert_targets
    assert _expected_alert_target(4) in alert_targets
    assert _expected_alert_target(5) in alert_targets
    assert _expected_alert_target(6) in alert_targets
    assert _expected_alert_target(7) in alert_targets

    # TOPIC1: zone1
    topic = create_topic(USER1, _gen_topic_params([zone1]))
    db_topic = _select_topic(topic)
    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 4
    assert _expected_alert_target(1) in alert_targets
    assert _expected_alert_target(4) in alert_targets
    assert _expected_alert_target(5) in alert_targets
    assert _expected_alert_target(7) in alert_targets

    # TOPIC1: zone1 & zone2
    topic = create_topic(USER1, _gen_topic_params([zone1, zone2]))
    db_topic = _select_topic(topic)
    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 6
    assert _expected_alert_target(1) in alert_targets
    assert _expected_alert_target(2) in alert_targets
    assert _expected_alert_target(4) in alert_targets  # distinct
    assert _expected_alert_target(5) in alert_targets
    assert _expected_alert_target(6) in alert_targets
    assert _expected_alert_target(7) in alert_targets  # distinct


def test_pick_alert_targets__disabled(testdb):
    create_user(USER1)
    parent_tag1 = create_tag(USER1, "pkg1:info1:")
    child_tag11 = create_tag(USER1, "pkg1:info1:mgr1")

    def _gen_pteam_params(idx: int) -> dict:
        return {
            "pteam_name": f"pteam{idx}",
            "alert_slack": {
                "enable": True,
                "webhook_url": "" if idx == 0 else SAMPLE_SLACK_WEBHOOK_URL + str(idx),
            },
            "alert_threat_impact": DEFAULT_ALERT_THREAT_IMPACT,
        }

    def _gen_topic_params(impact: int) -> dict:
        return {
            "topic_id": uuid4(),
            "title": "test topic",
            "abstract": "test abstract",
            "threat_impact": impact,
            "tags": [parent_tag1.tag_name],
            "misp_tags": [],
            "zone_names": [],
            "actions": [],
        }

    def _select_topic(topic: schemas.TopicCreateResponse) -> models.Topic:
        return testdb.query(models.Topic).filter(models.Topic.topic_id == str(topic.topic_id)).one()

    pteam = create_pteam(USER1, _gen_pteam_params(0))
    upload_pteam_tags(
        USER1,
        pteam.pteam_id,
        GROUP1,
        {child_tag11.tag_name: [("api/Pipfile.lock", "1.0.0")]},
        True,
    )

    # TOPIC0
    topic = create_topic(USER1, _gen_topic_params(1))
    db_topic = _select_topic(topic)
    db_topic.disabled = True
    testdb.add(db_topic)
    testdb.commit()
    testdb.refresh(db_topic)
    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 0


def test_pick_alert_targets__auto_closed(testdb):
    create_user(USER1)
    parent_tag1 = create_tag(USER1, "pkg1:info1:")
    child_tag11 = create_tag(USER1, "pkg1:info1:mgr1")
    parent_tag2 = create_tag(USER1, "pkg2:info1:")
    child_tag21 = create_tag(USER1, "pkg2:info1:mgr1")

    def _gen_pteam_params(idx: int) -> dict:
        return {
            "pteam_name": f"pteam{idx}",
            "alert_slack": {"enable": True, "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx)},
            "alert_threat_impact": DEFAULT_ALERT_THREAT_IMPACT,
        }

    def _gen_topic_params(tags: List[schemas.TagResponse]) -> dict:
        return {
            "topic_id": uuid4(),
            "title": "test topic",
            "abstract": "test abstract",
            "threat_impact": 1,
            "tags": [tag.tag_name for tag in tags],
            "misp_tags": [],
            "zone_names": [],
            "actions": [],
        }

    def _select_topic(topic: schemas.TopicCreateResponse) -> models.Topic:
        return testdb.query(models.Topic).filter(models.Topic.topic_id == str(topic.topic_id)).one()

    pteam0 = create_pteam(USER1, _gen_pteam_params(0))
    upload_pteam_tags(
        USER1,
        pteam0.pteam_id,
        GROUP1,
        {
            child_tag11.tag_name: [("api/Pipfile.lock", "1.0.0")],
            child_tag21.tag_name: [("api/Pipfile.lock", "1.0.0")],
        },
        True,
    )

    def _expected_alert_target(idx: int, tag: schemas.TagResponse) -> dict:
        return {
            "pteam_name": f"pteam{idx}",
            "slack_webhook_url": SAMPLE_SLACK_WEBHOOK_URL + str(idx),
            "pteam_id": str(pteam0.pteam_id),
            "tag_id": str(tag.tag_id),
            "tag_name": tag.tag_name,
        }

    # TOPIC0: parent_tag1
    topic = create_topic(USER1, _gen_topic_params([parent_tag1]))
    db_topic = _select_topic(topic)

    db_current_status = (
        testdb.query(models.CurrentPTeamTopicTagStatus)
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam0.pteam_id),
            models.CurrentPTeamTopicTagStatus.topic_id == db_topic.topic_id,
            models.CurrentPTeamTopicTagStatus.tag_id == str(child_tag11.tag_id),
        )
        .one()
    )
    assert db_current_status.topic_status == models.TopicStatusType.alerted
    db_current_status.topic_status = models.TopicStatusType.completed  # emulate closed
    testdb.add(db_current_status)
    testdb.commit()

    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 0

    # TOPIC1: parent_tag1 + parent_tag2
    topic = create_topic(USER1, _gen_topic_params([parent_tag1, parent_tag2]))
    db_topic = _select_topic(topic)

    # close child_tag11 only, child_tag21 is still alerted
    db_current_status = (
        testdb.query(models.CurrentPTeamTopicTagStatus)
        .filter(
            models.CurrentPTeamTopicTagStatus.pteam_id == str(pteam0.pteam_id),
            models.CurrentPTeamTopicTagStatus.topic_id == db_topic.topic_id,
            models.CurrentPTeamTopicTagStatus.tag_id == str(child_tag11.tag_id),
        )
        .one()
    )
    assert db_current_status.topic_status == models.TopicStatusType.alerted
    db_current_status.topic_status = models.TopicStatusType.completed  # emulate closed
    testdb.add(db_current_status)
    testdb.commit()

    alert_targets = _pick_alert_targets_for_pteam(testdb, db_topic)
    assert len(alert_targets) == 1
    assert _expected_alert_target(0, child_tag21) in alert_targets


def test_alert_ateam(testdb):
    create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)
    ATEAM1_WITH_SLACK_WEBHOOK_URL = {
        **ATEAM1,
        "alert_slack": {"enable": True, "webhook_url": SAMPLE_SLACK_WEBHOOK_URL},
    }
    ateam = create_ateam(USER1, ATEAM1_WITH_SLACK_WEBHOOK_URL)
    watching_request = create_watching_request(USER1, ateam.ateam_id)
    accept_watching_request(USER1, watching_request.request_id, pteam.pteam_id)
    upload_pteam_tags(USER1, pteam.pteam_id, GROUP1, {TAG1: [("api/Pipfile.lock", "1.0.0")]}, True)
    topic = create_topic(USER1, TOPIC1, actions=[])
    create_action(USER1, ACTION1, topic_id=topic.topic_id)
    action = testdb.query(models.TopicAction).first()
    with httpretty.enabled():
        httpretty.register_uri(
            httpretty.POST, ATEAM1_WITH_SLACK_WEBHOOK_URL["alert_slack"]["webhook_url"], body="OK"
        )
        alert_to_ateam(testdb, action)
        assert httpretty.last_request().method == "POST"
        assert (
            httpretty.last_request().url
            == ATEAM1_WITH_SLACK_WEBHOOK_URL["alert_slack"]["webhook_url"]
        )

        # assert posted data contains results of _create_blocks_for_ateam
        expected_blocks = _create_blocks_for_ateam(
            ateam_id=ateam.ateam_id,
            ateam_name=ateam.ateam_name,
            title=action.topic.title,
            action=action.action,
            action_type=action.action_type,
        )
        assert (
            json.loads(httpretty.last_request().body.decode("utf-8"))["blocks"] == expected_blocks
        )


def test_send_webhook_when_action_creation(mocker):
    # use mock to test slack webhook
    # TODO: should check posted http requests
    m = mocker.patch("app.slack.post_message")
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    ateam1 = create_ateam(
        USER1, {**ATEAM1, "alert_slack": {"enable": True, "webhook_url": SAMPLE_SLACK_WEBHOOK_URL}}
    )
    watching_request = create_watching_request(USER1, ateam1.ateam_id)
    accept_watching_request(USER1, watching_request.request_id, pteam1.pteam_id)
    upload_pteam_tags(USER1, pteam1.pteam_id, GROUP1, {TAG1: [("api/Pipfile.lock", "1.0.0")]}, True)
    topic1 = create_topic(USER1, TOPIC1, actions=[ACTION2])
    action1 = create_action(USER1, ACTION1, topic_id=topic1.topic_id)

    blocks = _create_blocks_for_ateam(
        ateam1.ateam_id,
        ateam1.ateam_name,
        topic1.title,
        action1.action,
        action1.action_type,
    )
    m.assert_has_calls([mocker.call(SAMPLE_SLACK_WEBHOOK_URL, blocks)])
