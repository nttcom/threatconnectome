import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app import models
from app.main import app
from app.tests.medium.constants import (
    PTEAM1,
    TOPIC1,
    USER1,
)
from app.tests.medium.utils import (
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    get_service_by_service_name,
    headers,
    update_topic,
    upload_pteam_tags,
)

client = TestClient(app)


class TestFixThreatsForTopic:

    @pytest.mark.parametrize(
        "dep_version, vuln_versions, should_exist_threat, should_exist_ticket",
        [
            ("1.2", ["< 2.0"], True, True),  # vulnerable and actionable
            ("1.2", ["< 1.0"], True, False),  # not vulnerable
            ("1.2", ["< 1.0", "> 3.0"], True, False),  # not vulnerable
            ("1.2", ["< 1.0", "> 3.0 || = 1.2"], True, True),  # vulnerable and actionable
            ("1.2", [], True, False),  # cannot detect vulnerable
            ("1.2", ["< uncomparable_range"], True, False),  # cannot detect vulnerable
            ("uncomparable version", ["< 2.0"], True, False),  # cannot detect vulnerable
            ("uncomparable version", [], True, False),  # cannot detect vulnerable
        ],
    )
    def test_threat_ticket_creation_on_creating_topic(
        self, testdb, dep_version, vuln_versions, should_exist_threat, should_exist_ticket
    ):
        create_user(USER1)
        tag1 = create_tag(USER1, "foobar:ubuntu-24.04:")
        pteam1 = create_pteam(USER1, PTEAM1)
        refs0 = {tag1.tag_name: [("test target", dep_version)]}
        service_name = "test service"
        upload_pteam_tags(USER1, pteam1.pteam_id, service_name, refs0)

        action1 = {
            "action": "test action",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [tag1.tag_name],
                "vulnerable_versions": {tag1.tag_name: vuln_versions},
            },
        }
        topic1 = create_topic(USER1, {**TOPIC1, "tags": [tag1.tag_name], "actions": [action1]})

        db_dependency1 = testdb.scalars(
            select(models.Dependency)
            .join(models.Service)
            .where(models.Service.pteam_id == str(pteam1.pteam_id))
        ).one()

        if should_exist_threat:
            assert len(db_dependency1.threats) == 1
            db_threat1 = db_dependency1.threats[0]
            assert db_threat1.topic_id == str(topic1.topic_id)
            if should_exist_ticket:
                assert db_threat1.ticket
            else:
                assert db_threat1.ticket is None
        else:
            assert len(db_dependency1.threats) == 0

    @pytest.mark.parametrize(
        "dep_version, should_exist_threat, should_exist_ticket",
        [
            ("1.2", True, False),  # vulnerable but no actions
            ("uncomparable version", True, False),  # cannot detect vulnerable
        ],
    )
    def test_threat_ticket_creation_on_updating_topic__to_have_matched_tag(
        self, testdb, dep_version, should_exist_threat, should_exist_ticket
    ):
        create_user(USER1)
        tag1 = create_tag(USER1, "foobar:ubuntu-24.04:")
        tag2 = create_tag(USER1, "foobar:ubuntu-22.04:")
        pteam1 = create_pteam(USER1, PTEAM1)
        refs0 = {tag1.tag_name: [("test target", dep_version)]}  # dependency has tag1
        service_name = "test service"
        upload_pteam_tags(USER1, pteam1.pteam_id, service_name, refs0)

        # create topic1 with tag2 -- no threats at this time
        topic1 = create_topic(USER1, {**TOPIC1, "tags": [tag2.tag_name], "actions": []})

        # update topic1 to have tag1
        topic1 = update_topic(USER1, topic1, {"tags": [tag1.tag_name]})

        db_dependency1 = testdb.scalars(
            select(models.Dependency)
            .join(models.Service)
            .where(models.Service.pteam_id == str(pteam1.pteam_id))
        ).one()

        if should_exist_threat:
            assert len(db_dependency1.threats) == 1
            db_threat1 = db_dependency1.threats[0]
            assert db_threat1.topic_id == str(topic1.topic_id)
            if should_exist_ticket:
                assert db_threat1.ticket
            else:
                assert db_threat1.ticket is None
        else:
            assert len(db_dependency1.threats) == 0

    @pytest.mark.parametrize(
        "dep_version, vuln_versions, should_exist_threat, should_exist_ticket",
        [
            ("1.2", ["< 2.0"], False, False),  # vulnerable and actionable
            ("1.2", ["< 1.0"], False, False),  # not vulnerable
            ("1.2", [], False, False),  # cannot detect vulnerable
            ("1.2", ["< uncomparable_range"], False, False),  # cannot detect vulnerable
            ("uncomparable version", ["< 2.0"], False, False),  # cannot detect vulnerable
            ("uncomparable version", [], False, False),  # cannot detect vulnerable
        ],
    )
    def test_threat_ticket_creation_on_updating_topic__to_lose_matched_tag(
        self, testdb, dep_version, vuln_versions, should_exist_threat, should_exist_ticket
    ):
        create_user(USER1)
        tag1 = create_tag(USER1, "foobar:ubuntu-24.04:")
        tag2 = create_tag(USER1, "foobar:ubuntu-18.04:")
        pteam1 = create_pteam(USER1, PTEAM1)
        refs0 = {tag1.tag_name: [("test target", dep_version)]}  # dependency has tag1
        service_name = "test service"
        upload_pteam_tags(USER1, pteam1.pteam_id, service_name, refs0)

        action1 = {
            "action": "test action",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [tag1.tag_name],
                "vulnerable_versions": {tag1.tag_name: vuln_versions},
            },
        }
        # create topic1 with actionable tag1 -- having threat & ticket at this time
        topic1 = create_topic(USER1, {**TOPIC1, "tags": [tag1.tag_name], "actions": [action1]})

        # update topic1 to have tag2 only -- lose tag1
        topic1 = update_topic(USER1, topic1, {"tags": [tag2.tag_name]})

        db_dependency1 = testdb.scalars(
            select(models.Dependency)
            .join(models.Service)
            .where(models.Service.pteam_id == str(pteam1.pteam_id))
        ).one()

        if should_exist_threat:
            assert len(db_dependency1.threats) == 1
            db_threat1 = db_dependency1.threats[0]
            assert db_threat1.topic_id == str(topic1.topic_id)
            if should_exist_ticket:
                assert db_threat1.ticket
            else:
                assert db_threat1.ticket is None
        else:
            assert len(db_dependency1.threats) == 0

    @staticmethod
    def create_ticket_and_delete_action(
        dep_version,
        vuln_versions_1,
        vuln_versions_2,
        delete_action_1,
        delete_action_2,
    ) -> tuple[str, str]:
        create_user(USER1)
        tag1 = create_tag(USER1, "foobar:ubuntu-24.04:")
        pteam1 = create_pteam(USER1, PTEAM1)
        refs0 = {tag1.tag_name: [("test target", dep_version)]}  # dependency has tag1
        service_name = "test service"
        upload_pteam_tags(USER1, pteam1.pteam_id, service_name, refs0)

        action1 = {
            "action": "test action",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [tag1.tag_name],
                "vulnerable_versions": {tag1.tag_name: vuln_versions_1},
            },
        }
        action2 = {
            "action": "test action2",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [tag1.tag_name],
                "vulnerable_versions": {tag1.tag_name: vuln_versions_2},
            },
        }
        # create topic1 with actionable tag1 -- having threat & ticket at this time
        topic1 = create_topic(
            USER1, {**TOPIC1, "tags": [tag1.tag_name], "actions": [action1, action2]}
        )

        if delete_action_1:
            client.delete(
                f"/actions/{topic1.actions[0].action_id}",
                headers=headers(USER1),
            )
        if delete_action_2:
            client.delete(
                f"/actions/{topic1.actions[1].action_id}",
                headers=headers(USER1),
            )

        return (str(pteam1.pteam_id), str(topic1.topic_id))

    @pytest.mark.parametrize("delete_action_1", [False, True])
    def test_ticket_should_be_deleted_when_delete_action_which_has_affected_version(
        self,
        testdb,
        delete_action_1,
    ):
        pteam_id, topic_id = TestFixThreatsForTopic.create_ticket_and_delete_action(
            "1.2", ["< 1.0"], ["< 1.5"], delete_action_1, True
        )

        db_dependency1 = testdb.scalars(
            select(models.Dependency)
            .join(models.Service)
            .where(models.Service.pteam_id == pteam_id)
        ).one()

        assert len(db_dependency1.threats) == 1
        db_threat1 = db_dependency1.threats[0]
        assert db_threat1.topic_id == topic_id
        assert db_threat1.ticket is None

    def test_ticket_should_not_be_deleted_when_delete_action_which_has_not_affected_version(
        self,
        testdb,
    ):
        pteam_id, topic_id = TestFixThreatsForTopic.create_ticket_and_delete_action(
            "1.2", ["< 1.5"], ["< 1.0"], False, True
        )

        db_dependency1 = testdb.scalars(
            select(models.Dependency)
            .join(models.Service)
            .where(models.Service.pteam_id == pteam_id)
        ).one()

        assert len(db_dependency1.threats) == 1
        db_threat1 = db_dependency1.threats[0]
        assert db_threat1.topic_id == topic_id
        assert db_threat1.ticket is not None


class TestFixThreatsForDependency:

    @pytest.mark.parametrize(
        "dep_version, vuln_versions, should_exist_threat, should_exist_ticket",
        [
            ("1.2", ["< 2.0"], True, True),  # vulnerable and actionable
            ("1.2", ["< 1.0"], True, False),  # not vulnerable
            ("1.2", ["< 1.0", "> 3.0"], True, False),  # not vulnerable
            ("1.2", ["< 1.0", "> 3.0 || = 1.2"], True, True),  # vulnerable and actionable
            ("1.2", [], True, False),  # cannot detect vulnerable
            ("1.2", ["< uncomparable_range"], True, False),  # cannot detect vulnerable
            ("uncomparable version", ["< 2.0"], True, False),  # cannot detect vulnerable
            ("uncomparable version", [], True, False),  # cannot detect vulnerable
        ],
    )
    def test_threat_ticket_creation_on_adding_dependency(
        self, testdb, dep_version, vuln_versions, should_exist_threat, should_exist_ticket
    ):
        create_user(USER1)
        tag1 = create_tag(USER1, "foobar:ubuntu-24.04:")
        pteam1 = create_pteam(USER1, PTEAM1)
        action1 = {
            "action": "test action",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [tag1.tag_name],
                "vulnerable_versions": {tag1.tag_name: vuln_versions},
            },
        }
        topic1 = create_topic(USER1, {**TOPIC1, "tags": [tag1.tag_name], "actions": [action1]})

        refs0 = {tag1.tag_name: [("test target", dep_version)]}
        service_name = "test service"
        upload_pteam_tags(USER1, pteam1.pteam_id, service_name, refs0)

        db_topic1 = testdb.scalars(
            select(models.Topic).where(models.Topic.topic_id == str(topic1.topic_id))
        ).one()

        if should_exist_threat:
            assert len(db_topic1.threats) == 1
            db_threat1 = db_topic1.threats[0]
            if should_exist_ticket:
                assert db_threat1.ticket
            else:
                assert db_threat1.ticket is None
        else:
            assert len(db_topic1.threats) == 0

    @pytest.mark.parametrize(
        "dep_version, vuln_versions, should_exist_threat, should_exist_ticket",
        [
            ("1.2", ["< 2.0"], False, False),  # vulnerable and actionable
            ("1.2", ["< 1.0"], False, False),  # not vulnerable
            ("1.2", [], False, False),  # cannot detect vulnerable
            ("1.2", ["< uncomparable_range"], False, False),  # cannot detect vulnerable
            ("uncomparable version", ["< 2.0"], False, False),  # cannot detect vulnerable
            ("uncomparable version", [], False, False),  # cannot detect vulnerable
        ],
    )
    def test_threat_ticket_creation_on_deleting_dependency(
        self, testdb, dep_version, vuln_versions, should_exist_threat, should_exist_ticket
    ):
        create_user(USER1)
        tag1 = create_tag(USER1, "foobar:ubuntu-24.04:")
        tag2 = create_tag(USER1, "foobar:ubuntu-18.04:")
        pteam1 = create_pteam(USER1, PTEAM1)
        action1 = {
            "action": "test action",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [tag1.tag_name],
                "vulnerable_versions": {tag1.tag_name: vuln_versions},
            },
        }
        topic1 = create_topic(USER1, {**TOPIC1, "tags": [tag1.tag_name], "actions": [action1]})

        refs0 = {tag1.tag_name: [("test target", dep_version)]}
        service_name = "test service"
        upload_pteam_tags(USER1, pteam1.pteam_id, service_name, refs0)

        # upload tag2 only -- lose tag1
        refs2 = {tag2.tag_name: [("test target", dep_version)]}
        upload_pteam_tags(USER1, pteam1.pteam_id, service_name, refs2)

        db_topic1 = testdb.scalars(
            select(models.Topic).where(models.Topic.topic_id == str(topic1.topic_id))
        ).one()

        if should_exist_threat:
            assert len(db_topic1.threats) == 1
            db_threat1 = db_topic1.threats[0]
            if should_exist_ticket:
                assert db_threat1.ticket
            else:
                assert db_threat1.ticket is None
        else:
            assert len(db_topic1.threats) == 0


class TestFixTicketSSVCPriority:

    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        create_user(USER1)
        pteam1 = create_pteam(USER1, PTEAM1)
        tag1 = create_tag(USER1, "foobar:ubuntu-24.04:")
        action1 = {
            "action": "test action",
            "action_type": models.ActionType.elimination,
            "recommended": True,
            "ext": {
                "tags": [tag1.tag_name],
                "vulnerable_versions": {tag1.tag_name: ["< 9999.99.99"]},
            },
        }
        create_topic(USER1, {**TOPIC1, "tags": [tag1.tag_name], "actions": [action1]})

        refs0 = {tag1.tag_name: [("test target", "1.2.3"), ("noise target", "1.2.3")]}
        service_name = "test service"
        upload_pteam_tags(USER1, pteam1.pteam_id, service_name, refs0)
        service1 = get_service_by_service_name(USER1, pteam1.pteam_id, service_name)
        request = {
            "service_mission_impact": models.MissionImpactEnum.DEGRADED,
            "service_safety_impact": models.SafetyImpactEnum.NEGLIGIBLE,
        }
        client.put(
            f"/pteams/{pteam1.pteam_id}/services/{service1['service_id']}",
            headers=headers(USER1),
            json=request,
        )
        # pteam1 should have 2 threats, and 1 ticket for each threat.

    @staticmethod
    def get_threat_by_dependency_target(testdb, target) -> models.Threat:
        return testdb.scalars(
            select(models.Threat).join(models.Dependency).where(models.Dependency.target == target)
        ).one_or_none()

    @pytest.mark.parametrize(
        "safety_impact, expected_ssvc_priority",
        [
            (models.SafetyImpactEnum.CATASTROPHIC, models.SSVCDeployerPriorityEnum.IMMEDIATE),
            (models.SafetyImpactEnum.CRITICAL, models.SSVCDeployerPriorityEnum.IMMEDIATE),
            (models.SafetyImpactEnum.MARGINAL, models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE),
            (models.SafetyImpactEnum.NEGLIGIBLE, models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE),
            (None, models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE),
        ],
    )
    def test_fix_priority_if_ticket_safety_impact_modified(
        self, testdb, safety_impact, expected_ssvc_priority
    ):
        not_modified_priority = models.SSVCDeployerPriorityEnum.OUT_OF_CYCLE

        # before modifying threat safety impact
        db_threat1 = self.get_threat_by_dependency_target(testdb, "test target")
        db_noise1 = self.get_threat_by_dependency_target(testdb, "noise target")

        assert db_threat1.ticket.ssvc_deployer_priority == not_modified_priority
        assert db_noise1.ticket.ssvc_deployer_priority == not_modified_priority

        # modify threat safety impact
        request = {
            "threat_safety_impact": safety_impact,
            "reason_safety_impact": "modify reason",
        }
        response = client.put(
            f"/threats/{db_threat1.threat_id}",
            headers=headers(USER1),
            json=request,
        )
        assert response.status_code == 200

        # after modifying threat safety impact
        db_threat2 = self.get_threat_by_dependency_target(testdb, "test target")
        db_noise2 = self.get_threat_by_dependency_target(testdb, "noise target")

        assert db_threat2.ticket.ssvc_deployer_priority == expected_ssvc_priority
        assert db_noise2.ticket.ssvc_deployer_priority == not_modified_priority
