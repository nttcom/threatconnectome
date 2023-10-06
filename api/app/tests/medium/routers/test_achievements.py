import json
from datetime import datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app import models, schemas
from app.main import app
from app.tests.medium.constants import (
    ACTION1,
    BADGE1,
    BADGE2,
    BADGE3,
    INVALID_METADATA,
    METADATA1,
    PTEAM1,
    PTEAM2,
    RANDOM_METADATA1,
    RANDOM_METADATA2,
    TOPIC1,
    USER1,
    USER2,
)
from app.tests.medium.utils import (
    accept_pteam_invitation,
    create_actionlog,
    create_badge,
    create_pteam,
    create_topic,
    create_user,
    headers,
    invite_to_pteam,
)

client = TestClient(app)


def test_create_secbadge():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    request = {
        "recipient": str(user1.user_id),
        "metadata": METADATA1,
        "badge_type": [models.BadgeType.skill],
        "certifier_type": models.CertifierType.trusted_third_party,
        "pteam_id": str(pteam1.pteam_id),
    }

    response = client.post("/achievements", headers=headers(USER1), json=request)

    assert response.status_code == 200
    data = response.json()
    metadata = json.loads(data["metadata_json"])
    assert data["image_url"] == METADATA1["image"]
    assert metadata["name"] == METADATA1["name"]
    assert UUID(data["user_id"]) == user1.user_id
    assert UUID(data["created_by"]) == user1.user_id
    assert data["badge_type"] == request["badge_type"]
    assert data["certifier_type"] == request["certifier_type"]
    assert UUID(data["pteam_id"]) == pteam1.pteam_id


def test_create_secbadge_by_invalid_user_id():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    request = {
        "recipient": str(uuid4()),
        "metadata": METADATA1,
        "badge_type": [models.BadgeType.skill],
        "certifier_type": models.CertifierType.trusted_third_party,
        "pteam_id": str(pteam1.pteam_id),
    }

    response = client.post("/achievements", headers=headers(USER1), json=request)

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid recipient userID"


def test_create_secbadge_by_invalid_priority():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    request = {
        "recipient": str(user1.user_id),
        "metadata": METADATA1,
        "priority": 65536,
        "badge_type": [models.BadgeType.skill],
        "certifier_type": models.CertifierType.trusted_third_party,
        "pteam_id": str(pteam1.pteam_id),
    }

    response = client.post("/achievements", headers=headers(USER1), json=request)

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Priority must be in the range of 0 to 65535."


def test_create_secbadge_with_status_id():
    user = create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)
    tag = pteam.tags[0]
    topic = create_topic(USER1, TOPIC1)

    request1 = {
        "topic_status": "scheduled",
    }

    response1 = client.post(
        f"/pteams/{pteam.pteam_id}/topicstatus/{topic.topic_id}/{tag.tag_id}",
        headers=headers(USER1),
        json=request1,
    )
    topic_status = schemas.TopicStatusResponse(**response1.json())

    metadata = {
        "name": f"he reason of {topic.title} has been found!",
        "status_id": str(topic_status.status_id),
    }

    request2 = {
        "recipient": str(user.user_id),
        "metadata": metadata,
        "badge_type": [models.BadgeType.performance],
        "certifier_type": models.CertifierType.system,
        "pteam_id": str(pteam.pteam_id),
    }

    response2 = client.post("/achievements", headers=headers(USER1), json=request2)

    assert response2.status_code == 200
    data = response2.json()
    metadata = json.loads(data["metadata_json"])
    assert data["image_url"] == ""
    assert metadata["name"] == metadata["name"]
    assert metadata["status_id"] == metadata["status_id"]
    assert UUID(data["user_id"]) == user.user_id
    assert UUID(data["pteam_id"]) == pteam.pteam_id


def test_create_secbadge_with_random_status_id():
    # RANDOM_METADATA1 is with a random pteam topic status id
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    request = {
        "recipient": str(user1.user_id),
        "metadata": RANDOM_METADATA1,
        "badge_type": [models.BadgeType.performance],
        "certifier_type": models.CertifierType.system,
        "pteam_id": str(pteam1.pteam_id),
    }

    response = client.post("/achievements", headers=headers(USER1), json=request)

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "PTeam topic status id is wrong"


def test_create_secbadge_with_logging_id():
    user = create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)
    topic = create_topic(USER1, TOPIC1, actions=[ACTION1])
    action = topic.actions[0]
    now = datetime.now()

    actionlog = create_actionlog(
        USER1, action.action_id, topic.topic_id, user.user_id, pteam.pteam_id, now
    )

    metadata = {
        "image": "",
        "name": f"{topic.title} has been solved!",
        "logging_id": str(actionlog.logging_id),
    }

    request = {
        "recipient": str(user.user_id),
        "metadata": metadata,
        "badge_type": [models.BadgeType.skill],
        "certifier_type": models.CertifierType.myself,
        "pteam_id": str(pteam.pteam_id),
    }

    response = client.post("/achievements", headers=headers(USER1), json=request)

    assert response.status_code == 200
    data = response.json()
    metadata = json.loads(data["metadata_json"])
    assert data["image_url"] == metadata["image"]
    assert metadata["name"] == metadata["name"]
    assert metadata["logging_id"] == metadata["logging_id"]
    assert UUID(data["user_id"]) == user.user_id
    assert UUID(data["pteam_id"]) == pteam.pteam_id


def test_create_secbadge_with_random_logging_id():
    # RANDOM_METADATA2 is with a random logging id
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    request = {
        "recipient": str(user1.user_id),
        "metadata": RANDOM_METADATA2,
        "badge_type": [models.BadgeType.skill],
        "certifier_type": models.CertifierType.myself,
        "pteam_id": str(pteam1.pteam_id),
    }

    response = client.post("/achievements", headers=headers(USER1), json=request)

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Logging_id is wrong"


def test_create_secbadge_by_invalid_metadata():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    request = {
        "recipient": str(user1.user_id),
        "metadata": INVALID_METADATA,
        "badge_type": [models.BadgeType.skill],
        "certifier_type": models.CertifierType.trusted_third_party,
        "pteam_id": str(pteam1.pteam_id),
    }

    response = client.post("/achievements", headers=headers(USER1), json=request)

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid metadata: parameter 'name' is wrong or missing"


def test_create_secbadge_by_invalid_pteam():
    user1 = create_user(USER1)
    create_pteam(USER1, PTEAM1)

    request = {
        "recipient": str(user1.user_id),
        "metadata": METADATA1,
        "badge_type": [models.BadgeType.skill],
        "certifier_type": models.CertifierType.trusted_third_party,
        "pteam_id": str(uuid4()),
    }

    response = client.post("/achievements", headers=headers(USER1), json=request)

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "No such pteam"


def test_create_secbadge__requester_and_recipient_are_pteam_member():
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)

    request = {
        "recipient": str(user2.user_id),
        "metadata": METADATA1,
        "badge_type": [models.BadgeType.performance],
        "certifier_type": models.CertifierType.coworker,
        "pteam_id": str(pteam1.pteam_id),
    }

    response = client.post("/achievements", headers=headers(USER1), json=request)

    assert response.status_code == 200


def test_create_secbadge__requester_is_not_pteam_member():
    create_user(USER1)
    create_pteam(USER1, PTEAM1)
    user2 = create_user(USER2)
    pteam2 = create_pteam(USER2, PTEAM2)

    request = {
        "recipient": str(user2.user_id),
        "metadata": METADATA1,
        "badge_type": [models.BadgeType.performance],
        "certifier_type": models.CertifierType.coworker,
        "pteam_id": str(pteam2.pteam_id),
    }

    response = client.post("/achievements", headers=headers(USER1), json=request)

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not a pteam member"


def test_create_secbadge__recipient_is_not_pteam_member():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    user2 = create_user(USER2)
    create_pteam(USER2, PTEAM2)

    request = {
        "recipient": str(user2.user_id),
        "metadata": METADATA1,
        "badge_type": [models.BadgeType.performance],
        "certifier_type": models.CertifierType.coworker,
        "pteam_id": str(pteam1.pteam_id),
    }

    response = client.post("/achievements", headers=headers(USER1), json=request)

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Not a pteam member"


def test_get_secbadges():
    user = create_user(USER1)
    pteam = create_pteam(USER1, PTEAM1)
    tag = pteam.tags[0]
    topic = create_topic(USER1, TOPIC1, actions=[ACTION1])
    actionlog = create_actionlog(
        USER1,
        topic.actions[0].action_id,
        topic.topic_id,
        user.user_id,
        pteam.pteam_id,
        datetime.now(),
    )

    request1 = {
        "topic_status": "scheduled",
    }
    response1 = client.post(
        f"/pteams/{pteam.pteam_id}/topicstatus/{topic.topic_id}/{tag.tag_id}",
        headers=headers(USER1),
        json=request1,
    )
    topic_status = schemas.TopicStatusResponse(**response1.json())

    metadata2 = {
        "image": "",
        "name": f"The reason of {topic.title} has been found!",
        "status_id": str(topic_status.status_id),
    }

    metadata3 = {
        "image": "",
        "name": f"{topic.title} has been solved!",
        "logging_id": str(actionlog.logging_id),
    }

    create_badge(USER1, str(user.user_id), METADATA1, BADGE1, str(pteam.pteam_id))
    create_badge(USER1, str(user.user_id), metadata2, BADGE2, str(pteam.pteam_id))
    create_badge(USER1, str(user.user_id), metadata3, BADGE3, str(pteam.pteam_id))

    response2 = client.get(f"/achievements/{str(user.user_id)}", headers=headers(USER1))
    assert response2.status_code == 200
    data = response2.json()
    metadatas = []
    for badge in data:
        metadatas.append(json.loads(badge["metadata_json"]))
        assert str(user.user_id) == badge["user_id"]
        assert str(pteam.pteam_id) == badge["pteam_id"]
    for meta in metadatas:
        if "logging_id" in meta:
            assert meta["logging_id"] == metadata3["logging_id"]
            assert meta["image"] == metadata3["image"]
            assert meta["name"] == metadata3["name"]
        elif "status_id" in meta:
            assert meta["status_id"] == metadata2["status_id"]
            assert meta["image"] == metadata2["image"]
            assert meta["name"] == metadata2["name"]
        else:
            assert meta["image"] == METADATA1["image"]
            assert meta["name"] == METADATA1["name"]


def test_delete_secbadge():
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    badge1 = create_badge(USER1, str(user1.user_id), METADATA1, BADGE1, str(pteam1.pteam_id))

    response = client.delete(f"/achievements/{badge1.badge_id}", headers=headers(USER1))
    assert response.status_code == 204


def test_delete_secbadge__by_badge_owner():
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    badge1 = create_badge(USER1, str(user2.user_id), METADATA1, BADGE1, str(pteam1.pteam_id))

    response = client.delete(f"/achievements/{badge1.badge_id}", headers=headers(USER2))
    assert response.status_code == 204


def test_delete_secbadge__by_badge_creator():
    create_user(USER1)
    user2 = create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    badge1 = create_badge(USER1, str(user2.user_id), METADATA1, BADGE1, str(pteam1.pteam_id))

    response = client.delete(f"/achievements/{badge1.badge_id}", headers=headers(USER1))
    assert response.status_code == 204


def test_delete_secbadge__by_pteambadge_manager():
    user1 = create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id, ["pteambadge_manage"])
    accept_pteam_invitation(USER2, invitation.invitation_id)
    badge1 = create_badge(USER1, str(user1.user_id), METADATA1, BADGE1, str(pteam1.pteam_id))

    response = client.delete(f"/achievements/{badge1.badge_id}", headers=headers(USER2))
    assert response.status_code == 204


def test_delete_secbadge__by_other_member():
    user1 = create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, invitation.invitation_id)
    badge1 = create_badge(USER1, str(user1.user_id), METADATA1, BADGE1, str(pteam1.pteam_id))

    response = client.delete(f"/achievements/{badge1.badge_id}", headers=headers(USER2))
    assert response.status_code == 403


def test_delete_secbadge__by_not_member():
    user1 = create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    badge1 = create_badge(USER1, str(user1.user_id), METADATA1, BADGE1, str(pteam1.pteam_id))

    response = client.delete(f"/achievements/{badge1.badge_id}", headers=headers(USER2))
    assert response.status_code == 403


def test_delete_secbadge_with_wrong_id():
    wrong_uuid = uuid4()
    user1 = create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    create_badge(USER1, str(user1.user_id), METADATA1, BADGE1, str(pteam1.pteam_id))

    response = client.delete(f"/achievements/{wrong_uuid}", headers=headers(USER1))
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "No such secbadge"
