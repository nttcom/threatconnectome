import pytest
from sqlalchemy import select

from app import models
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
    update_topic,
    upload_pteam_tags,
)


class TestFixThreatsForTopic:

    @pytest.mark.parametrize(
        "dep_version, vuln_versions, should_exist_threat, should_exist_ticket",
        [
            ("1.2", ["< 2.0"], True, True),  # vulnerable and actionable
            ("1.2", ["< 1.0"], False, False),  # not vulnerable
            ("1.2", ["< 1.0", "> 3.0"], False, False),  # not vulnerable
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


class TestFixThreatsForDependency:

    @pytest.mark.parametrize(
        "dep_version, vuln_versions, should_exist_threat, should_exist_ticket",
        [
            ("1.2", ["< 2.0"], True, True),  # vulnerable and actionable
            ("1.2", ["< 1.0"], False, False),  # not vulnerable
            ("1.2", ["< 1.0", "> 3.0"], False, False),  # not vulnerable
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
