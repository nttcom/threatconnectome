from typing import List, Sequence
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

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


class TestPTeamHasParentTag:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        # create pteam with parent_tag
        create_user(USER1)
        self.parent_tag1 = create_tag(USER1, "pkg1:info1:")

        pteam_params = {
            "pteam_name": "pteam1",
            "alert_slack": {
                "enable": True,
                "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + "1",
            },
            "alert_mail": {
                "enable": True,
                "address": "account1@example.com",
            },
            "alert_threat_impact": DEFAULT_ALERT_THREAT_IMPACT,
        }

        pteam = create_pteam(USER1, pteam_params)
        ext_tags = {self.parent_tag1.tag_name: [("api/Pipfile.lock", "1.0.0")]}
        upload_pteam_tags(USER1, pteam.pteam_id, GROUP1, ext_tags)

    # common functions used in tests
    def _gen_topic_params(self, tag: schemas.TagResponse) -> dict:
        topic_id = str(uuid4())
        return {
            "topic_id": topic_id,
            "title": "test topic " + topic_id,
            "abstract": "test abstract " + topic_id,
            "threat_impact": 1,
            "tags": [tag],
            "misp_tags": [],
            "actions": [],
        }

    # common functions used in tests
    def _find_expected(
        self,
        _targets: Sequence[models.CurrentPTeamTopicTagStatus],
        tag: schemas.TagResponse,
    ) -> bool:
        return any(_tgt.tag.tag_name == tag.tag_name for _tgt in _targets)

    @pytest.mark.parametrize(
        "parent_tag, expected",
        # parent_tag: Tags used when creating topics
        # expected: Ture if an alert is received, False if not
        [
            ("pkg1:info1:", True),
        ],
    )
    def test_it_should_alert_when_topic_with_same_parenttag_is_created(
        self, testdb, parent_tag, expected
    ):
        topic = create_topic(USER1, self._gen_topic_params(parent_tag))
        alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
        assert self._find_expected(alert_targets, self.parent_tag1) == expected

    @pytest.mark.parametrize(
        "child_tag, expected",
        # parent_tag: Tags used when creating topics
        # expected: Ture if an alert is received, False if not
        [
            ("pkg1:info1:mgr1", False),
        ],
    )
    def test_it_should_not_alert_when_topic_with_related_childtag_is_created(
        self, testdb, child_tag, expected
    ):
        topic = create_topic(USER1, self._gen_topic_params(child_tag))
        alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
        assert self._find_expected(alert_targets, self.parent_tag1) == expected


class TestPTeamHasChildTag:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        # create pteam with child_tag
        create_user(USER1)
        self.child_tag1 = create_tag(USER1, "pkg1:info1:mgr1")

        pteam_params = {
            "pteam_name": "pteam1",
            "alert_slack": {
                "enable": True,
                "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + "1",
            },
            "alert_mail": {
                "enable": True,
                "address": "account1@example.com",
            },
            "alert_threat_impact": DEFAULT_ALERT_THREAT_IMPACT,
        }

        pteam = create_pteam(USER1, pteam_params)
        ext_tags = {self.child_tag1.tag_name: [("api/Pipfile.lock", "1.0.0")]}
        upload_pteam_tags(USER1, pteam.pteam_id, GROUP1, ext_tags)

    # common functions used in tests
    def _gen_topic_params(self, tag: schemas.TagResponse) -> dict:
        topic_id = str(uuid4())
        return {
            "topic_id": topic_id,
            "title": "test topic " + topic_id,
            "abstract": "test abstract " + topic_id,
            "threat_impact": 1,
            "tags": [tag],
            "misp_tags": [],
            "actions": [],
        }

    # common functions used in tests
    def _find_expected(
        self,
        _targets: Sequence[models.CurrentPTeamTopicTagStatus],
        tag: schemas.TagResponse,
    ) -> bool:
        return any(_tgt.tag.tag_name == tag.tag_name for _tgt in _targets)

    @pytest.mark.parametrize(
        "parent_tag, expected",
        # parent_tag: Tags used when creating topics
        # expected: Ture if an alert is received, False if not
        [
            ("pkg1:info1:", True),
        ],
    )
    def test_it_should_alert_when_topic_with_related_parenttag_is_created(
        self, testdb, parent_tag, expected
    ):
        topic = create_topic(USER1, self._gen_topic_params(parent_tag))
        alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
        assert self._find_expected(alert_targets, self.child_tag1) == expected

    @pytest.mark.parametrize(
        "child_tag, expected",
        # parent_tag: Tags used when creating topics
        # expected: Ture if an alert is received, False if not
        [
            ("pkg1:info1:mgr1", True),
        ],
    )
    def test_it_should_alert_when_topic_with_asme_childtag_is_created(
        self, testdb, child_tag, expected
    ):
        topic = create_topic(USER1, self._gen_topic_params(child_tag))
        alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
        assert self._find_expected(alert_targets, self.child_tag1) == expected


@pytest.mark.parametrize(
    "alert_threat_impact, threshold, expected",
    # alert_threat_impact: pteam notification settings
    # threshold:  threat value at topic creation
    # expected: Ture if an alert is received, False if not
    [
        (1, 1, True),
        (1, 2, False),
        (1, 3, False),
        (1, 4, False),
        (2, 1, True),
        (2, 2, True),
        (2, 3, False),
        (2, 4, False),
        (3, 1, True),
        (3, 2, True),
        (3, 3, True),
        (3, 4, False),
        (4, 1, True),
        (4, 2, True),
        (4, 3, True),
        (4, 4, True),
    ],
)
def test_pick_alert_when_the_threat_impact_of_a_topic_is_less_than_the_alert_threat_impact_of_pteam(
    testdb, alert_threat_impact, threshold, expected
) -> None:
    create_user(USER1)
    parent_tag1 = create_tag(USER1, "pkg1:info1:")
    child_tag11 = create_tag(USER1, "pkg1:info1:mgr1")

    pteam_params = {
        "pteam_name": "pteam1",
        "alert_slack": {
            "enable": True,
            "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + "1",
        },
        "alert_mail": {
            "enable": True,
            "address": "account1@example.com",
        },
        "alert_threat_impact": alert_threat_impact,
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
        tag: schemas.TagResponse,
    ) -> bool:
        return any(_tgt.tag.tag_name == tag.tag_name for _tgt in _targets)

    # create pteam and upload pteam tags
    pteam = create_pteam(USER1, pteam_params)
    ext_tags = {child_tag11.tag_name: [("api/Pipfile.lock", "1.0.0")]}
    upload_pteam_tags(USER1, pteam.pteam_id, GROUP1, ext_tags)

    # create topic and verification of alerts
    topic = create_topic(USER1, _gen_topic_params(threshold))
    alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
    assert _find_expected(alert_targets, child_tag11) == expected


class TestTopicHasVersion:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        create_user(USER1)
        self.parent_tag1 = create_tag(USER1, "pkg1:info1:")
        self.child_tag11 = create_tag(USER1, "pkg1:info1:mgr1")
        self.parent_tag2 = create_tag(USER1, "pkg2:info1:")
        self.child_tag21 = create_tag(USER1, "pkg2:info1:mgr1")

        pteam_params = {
            "pteam_name": "pteam1",
            "alert_slack": {
                "enable": True,
                "webhook_url": SAMPLE_SLACK_WEBHOOK_URL + "1",
            },
            "alert_mail": {
                "enable": True,
                "address": "account@example.com",
            },
            "alert_threat_impact": DEFAULT_ALERT_THREAT_IMPACT,
        }

        self.pteam = create_pteam(USER1, pteam_params)

    # common functions used in tests
    def _gen_topic_params(self, tags: List[schemas.TagResponse]) -> dict:
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

    # common functions used in tests
    def _find_expected(
        self,
        _targets: Sequence[models.CurrentPTeamTopicTagStatus],
        tag: schemas.TagResponse,
    ) -> bool:
        return any(_tgt.tag.tag_name == tag.tag_name for _tgt in _targets)

    @pytest.mark.parametrize(
        "vulnerable_versions, expected",
        # vulnerable_versions: Vulnerable versions when creating topics
        # expected: Ture if an alert is received, False if not
        [("< 1.0.0", False)],
    )
    def test_it_should_not_alert_when_version_of_topic_is_lower_than_version_registered_in_pteam(
        self, testdb, vulnerable_versions, expected
    ):
        ext_tags = {
            self.child_tag11.tag_name: [("api/Pipfile.lock", "1.0.0")],
        }
        upload_pteam_tags(USER1, self.pteam.pteam_id, GROUP1, ext_tags)
        action = {
            "action": "action one",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [self.child_tag11.tag_name],
                "vulnerable_versions": {self.child_tag11.tag_name: [vulnerable_versions]},
            },
        }

        # create topic and verification of alerts
        topic = create_topic(USER1, self._gen_topic_params([self.parent_tag1]), actions=[action])
        alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
        assert self._find_expected(alert_targets, self.child_tag11) == expected

    @pytest.mark.parametrize(
        "vulnerable_versions, expected",
        # vulnerable_versions: Vulnerable versions when creating topics
        # expected: Ture if an alert is received, False if not
        [("< 2.0.0", True)],
    )
    def test_it_should_alert_when_version_of_topic_is_higher_than_version_registered_in_pteam(
        self, testdb, vulnerable_versions, expected
    ):
        ext_tags = {
            self.child_tag11.tag_name: [("api/Pipfile.lock", "1.0.0")],
        }
        upload_pteam_tags(USER1, self.pteam.pteam_id, GROUP1, ext_tags)
        action = {
            "action": "action one",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [self.child_tag11.tag_name],
                "vulnerable_versions": {self.child_tag11.tag_name: [vulnerable_versions]},
            },
        }

        # create topic and verification of alerts
        topic = create_topic(USER1, self._gen_topic_params([self.parent_tag1]), actions=[action])
        alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
        assert self._find_expected(alert_targets, self.child_tag11) == expected

    @pytest.mark.parametrize(
        "vulnerable_versions1, vulnerable_versions2, expected",
        # vulnerable_versions1: closed vulnerable versions
        # vulnerable_versions2: unclosed vulnerable versions
        # expected: Ture if an alert is received, False if not
        [("< 1.0.0", "< 2.0.0", True)],
    )
    def test_it_should_alert_only_version_matched_tag_and_not_alert_unmattched(
        self, testdb, vulnerable_versions1, vulnerable_versions2, expected
    ):
        ext_tags = {
            self.child_tag11.tag_name: [("api/Pipfile.lock", "1.0.0")],
            self.child_tag21.tag_name: [("api/Pipfile.lock", "1.0.0")],
        }
        upload_pteam_tags(USER1, self.pteam.pteam_id, GROUP1, ext_tags)

        action1_closable = {
            "action": "action one",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [self.child_tag11.tag_name],
                "vulnerable_versions": {self.child_tag11.tag_name: [vulnerable_versions1]},
            },
        }
        action2_unclosable = {
            "action": "action two",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [self.child_tag21.tag_name],
                "vulnerable_versions": {self.child_tag21.tag_name: [vulnerable_versions2]},
            },
        }

        # complex
        topic = create_topic(
            USER1,
            self._gen_topic_params([self.parent_tag1, self.parent_tag2]),
            actions=[action1_closable, action2_unclosable],
        )
        alert_targets = _pick_alert_targets_for_new_topic(testdb, topic.topic_id)
        assert len(alert_targets) == 1

        # alert only uncompleted
        assert self._find_expected(alert_targets, self.child_tag21) == expected


def test_alert_by_mail_if_vulnerabilities_are_found_when_creating_topic(mocker) -> None:
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
