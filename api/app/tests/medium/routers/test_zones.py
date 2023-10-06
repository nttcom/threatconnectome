from datetime import datetime
from typing import List, Union
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app import schemas
from app.main import app
from app.tests.medium.constants import (
    ACTION1,
    ACTION2,
    ACTION3,
    ATEAM1,
    GTEAM1,
    GTEAM2,
    PTEAM1,
    PTEAM2,
    TOPIC1,
    TOPIC2,
    TOPIC3,
    TOPIC4,
    USER1,
    USER2,
    ZONE1,
    ZONE2,
    ZONE3,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    accept_gteam_invitation,
    accept_pteam_invitation,
    accept_watching_request,
    assert_200,
    assert_204,
    create_ateam,
    create_gteam,
    create_pteam,
    create_topic,
    create_user,
    create_watching_request,
    create_zone,
    headers,
    invite_to_gteam,
    invite_to_pteam,
)

client = TestClient(app)


def test_create_zone():
    user1 = create_user(USER1)
    user2 = create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    assert zone1.zone_name == ZONE1["zone_name"]
    assert zone1.zone_info == ZONE1["zone_info"]
    assert zone1.gteam_id == gteam1.gteam_id
    assert zone1.created_by == user1.user_id
    assert zone1.archived is False

    data = assert_200(
        client.get(f"/gteams/{gteam1.gteam_id}/zones/{ZONE1['zone_name']}", headers=headers(USER1))
    )
    assert data["zone_name"] == ZONE1["zone_name"]
    assert data["zone_info"] == ZONE1["zone_info"]
    assert UUID(data["gteam_id"]) == gteam1.gteam_id
    assert data["archived"] is False

    with pytest.raises(HTTPError, match="400: Bad Request: Already exists"):
        create_zone(USER1, gteam1.gteam_id, ZONE1)

    with pytest.raises(HTTPError, match="404: Not Found: No such gteam"):
        create_zone(USER1, user2.user_id, ZONE2)

    with pytest.raises(HTTPError, match="403: Forbidden: Not a gteam member"):
        create_zone(USER2, gteam1.gteam_id, ZONE2)

    invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, invitation.invitation_id)
    zone2 = create_zone(USER2, gteam1.gteam_id, ZONE2)
    assert zone2.zone_name == ZONE2["zone_name"]
    assert zone2.zone_info == ZONE2["zone_info"]
    assert zone2.gteam_id == gteam1.gteam_id

    data = assert_200(
        client.get(f"/gteams/{gteam1.gteam_id}/zones/{ZONE2['zone_name']}", headers=headers(USER2))
    )
    assert data["zone_name"] == ZONE2["zone_name"]
    assert data["zone_info"] == ZONE2["zone_info"]
    assert UUID(data["gteam_id"]) == gteam1.gteam_id
    assert UUID(data["created_by"]) == user2.user_id
    assert data["archived"] is False


def test_get_zones():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)

    def _pick_zone(zones_: List[dict], zone_name_: str) -> dict:
        return next(filter(lambda x: x["zone_name"] == zone_name_, zones_), {})

    data = assert_200(client.get("/zones", headers=headers(USER1)))
    assert len(data) == 0

    create_zone(USER1, gteam1.gteam_id, ZONE1)
    data = assert_200(client.get("/zones", headers=headers(USER1)))
    assert len(data) == 1
    assert (zone1 := _pick_zone(data, ZONE1["zone_name"]))
    assert zone1["zone_info"] == ZONE1["zone_info"]
    assert UUID(zone1["gteam_id"]) == gteam1.gteam_id

    create_zone(USER1, gteam1.gteam_id, ZONE2)
    data = assert_200(client.get("/zones", headers=headers(USER1)))
    assert len(data) == 2
    assert (zone1 := _pick_zone(data, ZONE1["zone_name"]))
    assert zone1["zone_info"] == ZONE1["zone_info"]
    assert UUID(zone1["gteam_id"]) == gteam1.gteam_id
    assert (zone2 := _pick_zone(data, ZONE2["zone_name"]))
    assert zone2["zone_info"] == ZONE2["zone_info"]
    assert UUID(zone2["gteam_id"]) == gteam1.gteam_id

    create_user(USER2)
    gteam2 = create_gteam(USER2, GTEAM2)
    create_zone(USER2, gteam2.gteam_id, ZONE3)
    data = assert_200(client.get("/zones", headers=headers(USER1)))
    assert len(data) == 3
    assert (zone1 := _pick_zone(data, ZONE1["zone_name"]))
    assert zone1["zone_info"] == ZONE1["zone_info"]
    assert UUID(zone1["gteam_id"]) == gteam1.gteam_id
    assert (zone2 := _pick_zone(data, ZONE2["zone_name"]))
    assert zone2["zone_info"] == ZONE2["zone_info"]
    assert UUID(zone2["gteam_id"]) == gteam1.gteam_id
    assert (zone3 := _pick_zone(data, ZONE3["zone_name"]))
    assert zone3["zone_info"] == ZONE3["zone_info"]
    assert UUID(zone3["gteam_id"]) == gteam2.gteam_id


def test_update_zone_info():
    create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    create_zone(USER1, gteam1.gteam_id, ZONE1)

    def _pick_zone(zones_: List[dict], zone_name_: str) -> dict:
        return next(filter(lambda x: x["zone_name"] == zone_name_, zones_), {})

    # by master
    request = {"zone_info": "updated zone info 1"}
    data = assert_200(
        client.put(
            f"/gteams/{gteam1.gteam_id}/zones/{ZONE1['zone_name']}",
            headers=headers(USER1),
            json=request,
        )
    )
    assert data["zone_info"] == request["zone_info"]
    data = assert_200(
        client.get(f"/gteams/{gteam1.gteam_id}/zones/{ZONE1['zone_name']}", headers=headers(USER1))
    )
    assert data["zone_name"] == ZONE1["zone_name"]
    assert data["zone_info"] == request["zone_info"]
    data = assert_200(client.get("/zones", headers=headers(USER1)))
    assert len(data) == 1
    assert (zone1 := _pick_zone(data, ZONE1["zone_name"]))
    assert zone1["zone_info"] == request["zone_info"]

    # by not a member
    request = {"zone_info": "updated zone info 2"}
    with pytest.raises(HTTPError, match=r"403: Forbidden: You do not have related zone"):
        assert_200(
            client.put(
                f"/gteams/{gteam1.gteam_id}/zones/{ZONE1['zone_name']}",
                headers=headers(USER2),
                json=request,
            )
        )

    # be a member
    g_invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, g_invitation.invitation_id)

    # by a member
    data = assert_200(
        client.put(
            f"/gteams/{gteam1.gteam_id}/zones/{ZONE1['zone_name']}",
            headers=headers(USER2),
            json=request,
        )
    )
    assert data["zone_info"] == request["zone_info"]
    data = assert_200(
        client.get(f"/gteams/{gteam1.gteam_id}/zones/{ZONE1['zone_name']}", headers=headers(USER2))
    )
    assert data["zone_name"] == ZONE1["zone_name"]
    assert data["zone_info"] == request["zone_info"]
    data = assert_200(client.get("/zones", headers=headers(USER2)))
    assert len(data) == 1
    assert (zone1 := _pick_zone(data, ZONE1["zone_name"]))
    assert zone1["zone_info"] == request["zone_info"]


def test_delete_zone():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)

    data = assert_200(client.get("/zones", headers=headers(USER1)))
    assert len(data) == 1

    assert_204(
        client.delete(f"/gteams/{gteam1.gteam_id}/zones/{zone1.zone_name}", headers=headers(USER1))
    )
    data = assert_200(client.get("/zones", headers=headers(USER1)))
    assert len(data) == 0
    with pytest.raises(HTTPError, match=r"404: Not Found: No such zone"):
        assert_200(
            client.get(
                f"/gteams/{gteam1.gteam_id}/zones/{ZONE1['zone_name']}", headers=headers(USER1)
            )
        )


def test_delete_zone__in_use():
    create_user(USER1)
    gteam1 = create_gteam(USER1, GTEAM1)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    create_topic(USER1, TOPIC1, zone_names=[zone1.zone_name])

    with pytest.raises(HTTPError, match="400: Bad Request: Requested zone is in use"):
        assert_204(
            client.delete(
                f"/gteams/{gteam1.gteam_id}/zones/{zone1.zone_name}", headers=headers(USER1)
            )
        )


def test_zoned_teams():
    create_user(USER1)

    def _sorted_teams(teams: List[Union[schemas.PTeamEntry, schemas.ATeamEntry]]) -> list:
        if len(teams) == 0:
            return []
        return sorted(
            teams, key=lambda x: x.pteam_name if isinstance(x, schemas.PTeamEntry) else x.ateam_name
        )

    # before creating zone
    with pytest.raises(HTTPError, match="404: Not Found: No such zone"):
        assert_200(client.get(f"/zones/{ZONE1['zone_name']}/teams", headers=headers(USER1)))

    # create zone1 (and zone2)
    gteam1 = create_gteam(USER1, GTEAM1)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    create_zone(USER1, gteam1.gteam_id, ZONE2)  # noise

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/teams", headers=headers(USER1)))
    resp = schemas.ZonedTeamsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.pteams == []
    assert resp.ateams == []

    # create pteam1 with zone1
    pteam1 = create_pteam(USER1, {**PTEAM1, "zone_names": [zone1.zone_name]})

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/teams", headers=headers(USER1)))
    resp = schemas.ZonedTeamsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.pteams == [schemas.PTeamEntry(**x.model_dump()) for x in [pteam1]]
    assert resp.ateams == []

    # create ateam1 and watch pteam1
    ateam1 = create_ateam(USER1, ATEAM1)
    watch_req = create_watching_request(USER1, ateam1.ateam_id)
    accept_watching_request(USER1, watch_req.request_id, pteam1.pteam_id)

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/teams", headers=headers(USER1)))
    resp = schemas.ZonedTeamsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.pteams == [schemas.PTeamEntry(**x.model_dump()) for x in [pteam1]]
    assert resp.ateams == [schemas.ATeamEntry(**x.model_dump()) for x in [ateam1]]

    # create pteam2 (without zone)
    pteam2 = create_pteam(USER1, PTEAM2)

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/teams", headers=headers(USER1)))
    resp = schemas.ZonedTeamsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.pteams == [schemas.PTeamEntry(**x.model_dump()) for x in [pteam1]]
    assert resp.ateams == [schemas.ATeamEntry(**x.model_dump()) for x in [ateam1]]

    # add zone1 to pteam2
    request = {"zone_names": [zone1.zone_name]}
    assert_200(client.put(f"/pteams/{pteam2.pteam_id}", headers=headers(USER1), json=request))

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/teams", headers=headers(USER1)))
    resp = schemas.ZonedTeamsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert _sorted_teams(resp.pteams) == _sorted_teams(
        [schemas.PTeamEntry(**x.model_dump()) for x in [pteam1, pteam2]]
    )
    assert resp.ateams == [schemas.ATeamEntry(**x.model_dump()) for x in [ateam1]]

    # remove zone1 from pteam1
    request = {"zone_names": []}
    assert_200(client.put(f"/pteams/{pteam1.pteam_id}", headers=headers(USER1), json=request))

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/teams", headers=headers(USER1)))
    resp = schemas.ZonedTeamsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.pteams == [schemas.PTeamEntry(**x.model_dump()) for x in [pteam2]]
    assert resp.ateams == []

    create_user(USER2)

    # by not pteam member nor gteam member
    with pytest.raises(HTTPError, match="403: Forbidden: You do not have related zone"):
        assert_200(client.get(f"/zones/{ZONE1['zone_name']}/teams", headers=headers(USER2)))

    # by a pteam member but not a gteam member
    p_invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, p_invitation.invitation_id)

    with pytest.raises(HTTPError, match="403: Forbidden: You do not have related zone"):
        assert_200(client.get(f"/zones/{ZONE1['zone_name']}/teams", headers=headers(USER2)))

    # by a gteam member (not a member of pteam2)
    g_invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, g_invitation.invitation_id)

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/teams", headers=headers(USER2)))
    resp = schemas.ZonedTeamsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.pteams == [schemas.PTeamEntry(**x.model_dump()) for x in [pteam2]]
    assert resp.ateams == []


def test_zoned_topics():
    create_user(USER1)

    def _sorted_topics(topics: List[schemas.TopicEntry]) -> List[schemas.TopicEntry]:
        return sorted(
            [
                schemas.TopicEntry(
                    topic_id=topic.topic_id,
                    title=topic.title,
                    # fix not-comparable params - content_fingerprint & updated_at
                    content_fingerprint="",
                    updated_at=datetime.fromtimestamp(0),
                )
                for topic in topics
            ],
            key=lambda x: x.topic_id,
        )

    # before creating zone
    with pytest.raises(HTTPError, match="404: Not Found: No such zone"):
        assert_200(client.get(f"/zones/{ZONE1['zone_name']}/topics", headers=headers(USER1)))

    # create zone1 (and zone2)
    gteam1 = create_gteam(USER1, GTEAM1)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    zone2 = create_zone(USER1, gteam1.gteam_id, ZONE2)

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/topics", headers=headers(USER1)))
    resp = schemas.ZonedTopicsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.topics == []

    # topic1 with zone1
    topic1 = create_topic(USER1, TOPIC1, zone_names=[zone1.zone_name])

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/topics", headers=headers(USER1)))
    resp = schemas.ZonedTopicsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.topics == [schemas.TopicEntry(**x.model_dump()) for x in [topic1]]

    # topic2 with zone2
    topic2 = create_topic(USER1, TOPIC2, zone_names=[zone2.zone_name])

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/topics", headers=headers(USER1)))
    resp = schemas.ZonedTopicsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.topics == [schemas.TopicEntry(**x.model_dump()) for x in [topic1]]

    # topic3 without zone
    topic3 = create_topic(USER1, TOPIC3, zone_names=[])

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/topics", headers=headers(USER1)))
    resp = schemas.ZonedTopicsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.topics == [schemas.TopicEntry(**x.model_dump()) for x in [topic1]]

    # set topic3: [] -> [zone1]
    request = {"zone_names": [zone1.zone_name]}
    assert_200(client.put(f"/topics/{topic3.topic_id}", headers=headers(USER1), json=request))

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/topics", headers=headers(USER1)))
    resp = schemas.ZonedTopicsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert _sorted_topics(resp.topics) == _sorted_topics(
        [schemas.TopicEntry(**x.model_dump()) for x in [topic1, topic3]]
    )

    # set topic2: [zone2] -> [zone1, zone2]
    request = {"zone_names": [zone1.zone_name, zone2.zone_name]}
    assert_200(client.put(f"/topics/{topic2.topic_id}", headers=headers(USER1), json=request))

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/topics", headers=headers(USER1)))
    resp = schemas.ZonedTopicsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert _sorted_topics(resp.topics) == _sorted_topics(
        [schemas.TopicEntry(**x.model_dump()) for x in [topic1, topic2, topic3]]
    )

    # set topic1: [zone1] -> [zone2]
    request = {"zone_names": [zone2.zone_name]}
    assert_200(client.put(f"/topics/{topic1.topic_id}", headers=headers(USER1), json=request))

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/topics", headers=headers(USER1)))
    resp = schemas.ZonedTopicsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert _sorted_topics(resp.topics) == _sorted_topics(
        [schemas.TopicEntry(**x.model_dump()) for x in [topic2, topic3]]
    )

    create_user(USER2)

    # by not a gteam member
    with pytest.raises(HTTPError, match="403: Forbidden: You do not have related zone"):
        assert_200(client.get(f"/zones/{ZONE1['zone_name']}/topics", headers=headers(USER2)))

    # by a gteam member
    g_invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, g_invitation.invitation_id)

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/topics", headers=headers(USER2)))
    resp = schemas.ZonedTopicsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert _sorted_topics(resp.topics) == _sorted_topics(
        [schemas.TopicEntry(**x.model_dump()) for x in [topic2, topic3]]
    )


def test_zoned_actions():
    create_user(USER1)

    def _fix_action_request(req: dict) -> dict:
        for key in {"action_id", "topic_id", "zones", "created_by", "created_at"}:
            req.pop(key, None)
        return req

    def _sorted_actions(actions: List[dict]) -> List[dict]:
        return sorted(actions, key=lambda x: x["action"])

    # before creating zone
    with pytest.raises(HTTPError, match="404: Not Found: No such zone"):
        assert_200(client.get(f"/zones/{ZONE1['zone_name']}/actions", headers=headers(USER1)))

    # create zone1 (and zone2)
    gteam1 = create_gteam(USER1, GTEAM1)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    zone2 = create_zone(USER1, gteam1.gteam_id, ZONE2)

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/actions", headers=headers(USER1)))
    resp = schemas.ZonedActionsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.actions == []

    # action1 with zone1
    topic1 = create_topic(USER1, TOPIC1, actions=[{**ACTION1, "zone_names": [zone1.zone_name]}])
    assert len(topic1.actions) == 1
    action1 = topic1.actions[0]

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/actions", headers=headers(USER1)))
    resp = schemas.ZonedActionsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert len(resp.actions) == 1
    assert resp.actions[0].model_dump() == {**action1.model_dump(), "topic_title": topic1.title}

    # does not affect zoned topics
    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/topics", headers=headers(USER1)))
    resp = schemas.ZonedTopicsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.topics == []

    # action2 with zone2
    topic2 = create_topic(USER1, TOPIC2, actions=[{**ACTION2, "zone_names": [zone2.zone_name]}])
    action2 = topic2.actions[0]

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/actions", headers=headers(USER1)))
    resp = schemas.ZonedActionsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert len(resp.actions) == 1
    assert resp.actions[0].model_dump() == {**action1.model_dump(), "topic_title": topic1.title}

    # action3 without zone
    topic3 = create_topic(USER1, TOPIC3, actions=[{**ACTION3, "zone_names": []}])
    action3 = topic3.actions[0]

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/actions", headers=headers(USER1)))
    resp = schemas.ZonedActionsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert len(resp.actions) == 1
    assert resp.actions[0].model_dump() == {**action1.model_dump(), "topic_title": topic1.title}

    # action4 without zone on topic4 with zone1
    create_topic(
        USER1, TOPIC4, zone_names=[zone1.zone_name], actions=[{**ACTION3, "zone_names": []}]
    )

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/actions", headers=headers(USER1)))
    resp = schemas.ZonedActionsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert len(resp.actions) == 1
    assert resp.actions[0].model_dump() == {**action1.model_dump(), "topic_title": topic1.title}

    # set topic3 actions: [] -> [zone1]
    request = _fix_action_request({**action3.model_dump(), "zone_names": [zone1.zone_name]})
    data = assert_200(
        client.put(f"/actions/{action3.action_id}", headers=headers(USER1), json=request)
    )
    action3_1 = schemas.ActionResponse(**data)

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/actions", headers=headers(USER1)))
    resp = schemas.ZonedActionsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert len(resp.actions) == 2
    assert _sorted_actions([x.model_dump() for x in resp.actions]) == _sorted_actions(
        [
            {**action1.model_dump(), "topic_title": topic1.title},
            {**action3_1.model_dump(), "topic_title": topic3.title},
        ]
    )

    # set action2 [zone2] -> [zone1]
    request = _fix_action_request({**action2.model_dump(), "zone_names": [zone1.zone_name]})
    data = assert_200(
        client.put(f"/actions/{action2.action_id}", headers=headers(USER1), json=request)
    )
    action2_1 = schemas.ActionResponse(**data)

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/actions", headers=headers(USER1)))
    resp = schemas.ZonedActionsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert len(resp.actions) == 3
    assert _sorted_actions([x.model_dump() for x in resp.actions]) == _sorted_actions(
        [
            {**action1.model_dump(), "topic_title": topic1.title},
            {**action2_1.model_dump(), "topic_title": topic2.title},
            {**action3_1.model_dump(), "topic_title": topic3.title},
        ]
    )

    # set action1 [zone1] -> []
    request = _fix_action_request({**action1.model_dump(), "zone_names": []})
    with pytest.raises(HTTPError, match=r"400: Bad Request: Once a topic action has been zoned,"):
        assert_200(
            client.put(f"/actions/{action1.action_id}", headers=headers(USER1), json=request)
        )

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/actions", headers=headers(USER1)))
    resp = schemas.ZonedActionsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert len(resp.actions) == 3
    assert _sorted_actions([x.model_dump() for x in resp.actions]) == _sorted_actions(
        [
            {**action1.model_dump(), "topic_title": topic1.title},
            {**action2_1.model_dump(), "topic_title": topic2.title},
            {**action3_1.model_dump(), "topic_title": topic3.title},
        ]
    )

    # remove action1
    assert_204(client.delete(f"/actions/{action1.action_id}", headers=headers(USER1)))

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/actions", headers=headers(USER1)))
    resp = schemas.ZonedActionsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert len(resp.actions) == 2
    assert _sorted_actions([x.model_dump() for x in resp.actions]) == _sorted_actions(
        [
            {**action2_1.model_dump(), "topic_title": topic2.title},
            {**action3_1.model_dump(), "topic_title": topic3.title},
        ]
    )

    create_user(USER2)

    # by not a gteam member
    with pytest.raises(HTTPError, match="403: Forbidden: You do not have related zone"):
        assert_200(client.get(f"/zones/{ZONE1['zone_name']}/actions", headers=headers(USER2)))

    # by a gteam member
    g_invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, g_invitation.invitation_id)

    data = assert_200(client.get(f"/zones/{ZONE1['zone_name']}/actions", headers=headers(USER2)))
    resp = schemas.ZonedActionsResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert len(resp.actions) == 2
    assert _sorted_actions([x.model_dump() for x in resp.actions]) == _sorted_actions(
        [
            {**action2_1.model_dump(), "topic_title": topic2.title},
            {**action3_1.model_dump(), "topic_title": topic3.title},
        ]
    )


def test_zoned_latest_topic():
    create_user(USER1)

    # before creating zone
    with pytest.raises(HTTPError, match="404: Not Found: No such zone"):
        assert_200(client.get(f"/zones/{ZONE1['zone_name']}/topics", headers=headers(USER1)))

    # create zone1 (and zone2)
    gteam1 = create_gteam(USER1, GTEAM1)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)

    data = assert_200(
        client.get(f"/zones/{ZONE1['zone_name']}/latest_topic", headers=headers(USER1))
    )
    resp = schemas.ZonedLatestTopicResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.latest_topic is None

    # topic1, topic2 with zone1
    topic1 = create_topic(USER1, TOPIC1, zone_names=[zone1.zone_name])
    topic2 = create_topic(USER1, TOPIC2, zone_names=[zone1.zone_name])
    assert topic1.updated_at < topic2.updated_at
    data = assert_200(
        client.get(f"/zones/{ZONE1['zone_name']}/latest_topic", headers=headers(USER1))
    )
    resp = schemas.ZonedLatestTopicResponse(**data)
    assert resp.zone.model_dump() == zone1.model_dump()
    assert resp.gteam.model_dump() == gteam1.model_dump()
    assert resp.latest_topic.topic_id == topic2.topic_id


def test_archived_zones():
    create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    assert zone1.archived is False

    # archived zone1
    data = assert_200(
        client.put(
            f"/gteams/{gteam1.gteam_id}/zones/{zone1.zone_name}/archived",
            headers=headers(USER1),
            json={"archived": True},
        )
    )
    assert data["archived"] is True
    data = assert_200(
        client.get(f"/gteams/{gteam1.gteam_id}/zones/{zone1.zone_name}", headers=headers(USER1))
    )
    assert data["zone_name"] == zone1.zone_name
    assert data["archived"] is True

    with pytest.raises(HTTPError, match=r"400: Bad Request: Cannot apply archived zone"):
        create_pteam(USER1, {**PTEAM1, "zone_names": [zone1.zone_name]})

    with pytest.raises(HTTPError, match=r"400: Bad Request: Cannot apply archived zone"):
        create_topic(USER1, {**TOPIC1, "zone_names": [zone1.zone_name]})

    with pytest.raises(HTTPError, match=r"400: Bad Request: Cannot apply archived zone"):
        create_topic(
            USER1,
            {**TOPIC2, "zone_names": [], "actions": [{**ACTION1, "zone_names": [zone1.zone_name]}]},
        )

    # un-archived zone1
    data = assert_200(
        client.put(
            f"/gteams/{gteam1.gteam_id}/zones/{zone1.zone_name}/archived",
            headers=headers(USER1),
            json={"archived": False},
        )
    )
    assert data["archived"] is False
    data = assert_200(
        client.get(f"/gteams/{gteam1.gteam_id}/zones/{zone1.zone_name}", headers=headers(USER1))
    )
    assert data["zone_name"] == zone1.zone_name
    assert data["archived"] is False

    assert (pteam1 := create_pteam(USER1, {**PTEAM1, "zone_names": [zone1.zone_name]}))
    assert (topic1 := create_topic(USER1, {**TOPIC1, "zone_names": [zone1.zone_name]}))
    assert (
        topic2 := create_topic(
            USER1,
            {**TOPIC2, "zone_names": [], "actions": [{**ACTION1, "zone_names": [zone1.zone_name]}]},
        )
    )

    # zone1 effective
    assert_200(client.get(f"/topics/{topic1.topic_id}", headers=headers(USER1)))
    with pytest.raises(HTTPError, match=r"404: Not Found: You do not have related zone"):
        assert_200(client.get(f"/topics/{topic1.topic_id}", headers=headers(USER2)))
    data = assert_200(
        client.get(
            f"/topics/{topic2.topic_id}/actions/pteam/{pteam1.pteam_id}", headers=headers(USER1)
        )
    )
    assert len(data["actions"]) == 1
    assert data["actions"][0]["action"] == ACTION1["action"]

    # re-archived zone1
    data = assert_200(
        client.put(
            f"/gteams/{gteam1.gteam_id}/zones/{zone1.zone_name}/archived",
            headers=headers(USER1),
            json={"archived": True},
        )
    )
    assert data["archived"] is True
    data = assert_200(
        client.get(f"/gteams/{gteam1.gteam_id}/zones/{zone1.zone_name}", headers=headers(USER1))
    )
    assert data["zone_name"] == zone1.zone_name
    assert data["archived"] is True

    # add pteam member
    assert_200(client.get(f"/topics/{topic1.topic_id}", headers=headers(USER1)))
    with pytest.raises(HTTPError, match=r"404: Not Found: You do not have related zone"):
        assert_200(client.get(f"/topics/{topic1.topic_id}", headers=headers(USER2)))
    p_invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, p_invitation.invitation_id)
    assert_200(client.get(f"/topics/{topic1.topic_id}", headers=headers(USER2)))

    # archived zone1 still effective
    assert_200(
        client.put(f"/pteams/{pteam1.pteam_id}", headers=headers(USER1), json={"zone_names": []})
    )
    with pytest.raises(HTTPError, match=r"404: Not Found: You do not have related zone"):
        assert_200(client.get(f"/topics/{topic1.topic_id}", headers=headers(USER2)))
    data = assert_200(
        client.get(
            f"/topics/{topic2.topic_id}/actions/pteam/{pteam1.pteam_id}", headers=headers(USER1)
        )
    )
    assert len(data["actions"]) == 0


def test_update_pteam_zones():
    create_user(USER1)
    create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    gteam2 = create_gteam(USER2, GTEAM2)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    zone2 = create_zone(USER2, gteam2.gteam_id, ZONE2)
    pteam1 = create_pteam(USER1, {**PTEAM1, "zone_names": [zone1.zone_name]})
    p_invitation = invite_to_pteam(USER1, pteam1.pteam_id, auth=["admin"])
    accept_pteam_invitation(USER2, p_invitation.invitation_id)

    # user2 can apply zone2
    data = assert_200(
        client.put(
            f"/pteams/{pteam1.pteam_id}",
            headers=headers(USER2),
            json={"zone_names": [zone1.zone_name, zone2.zone_name]},
        )
    )
    assert UUID(data["pteam_id"]) == pteam1.pteam_id
    assert {x["zone_name"] for x in data["zones"]} == {zone1.zone_name, zone2.zone_name}

    # user2 also can remove zone2
    data = assert_200(
        client.put(
            f"/pteams/{pteam1.pteam_id}",
            headers=headers(USER2),
            json={"zone_names": [zone1.zone_name]},
        )
    )
    assert UUID(data["pteam_id"]) == pteam1.pteam_id
    assert {x["zone_name"] for x in data["zones"]} == {zone1.zone_name}

    # user1 cannot apply zone2
    with pytest.raises(HTTPError, match=r"400: Bad Request: You do not have related zone"):
        assert_200(
            client.put(
                f"/pteams/{pteam1.pteam_id}",
                headers=headers(USER1),
                json={"zone_names": [zone1.zone_name, zone2.zone_name]},
            )
        )

    # user2 can remove zone1 by ADMIN authority
    data = assert_200(
        client.put(
            f"/pteams/{pteam1.pteam_id}",
            headers=headers(USER2),
            json={"zone_names": []},
        )
    )
    assert UUID(data["pteam_id"]) == pteam1.pteam_id
    assert {x["zone_name"] for x in data["zones"]} == set()


def test_update_topic_zones():
    create_user(USER1)
    user2 = create_user(USER2)
    gteam1 = create_gteam(USER1, GTEAM1)
    gteam2 = create_gteam(USER2, GTEAM2)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    zone2 = create_zone(USER2, gteam2.gteam_id, ZONE2)
    pteam1 = create_pteam(USER1, {**PTEAM1, "zone_names": [zone1.zone_name]})
    p_invitation = invite_to_pteam(USER1, pteam1.pteam_id)
    accept_pteam_invitation(USER2, p_invitation.invitation_id)
    g_invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, g_invitation.invitation_id)
    topic1 = create_topic(USER2, {**TOPIC1, "zone_names": [zone1.zone_name]})  # created by user2
    # user2 leave gteam
    assert_204(
        client.delete(f"/gteams/{gteam1.gteam_id}/members/{user2.user_id}", headers=headers(USER2))
    )
    # user2 has zone1 via pteam1, zone2 via gteam2
    # user2 can apply zone2
    data = assert_200(
        client.put(
            f"/topics/{topic1.topic_id}",
            headers=headers(USER2),
            json={"zone_names": [zone1.zone_name, zone2.zone_name]},
        )
    )
    assert UUID(data["topic_id"]) == topic1.topic_id
    assert {x["zone_name"] for x in data["zones"]} == {zone1.zone_name, zone2.zone_name}

    # user2 can remove zone2
    data = assert_200(
        client.put(
            f"/topics/{topic1.topic_id}",
            headers=headers(USER2),
            json={"zone_names": [zone1.zone_name]},
        )
    )
    assert UUID(data["topic_id"]) == topic1.topic_id
    assert {x["zone_name"] for x in data["zones"]} == {zone1.zone_name}

    # user2 cannot remove zone1, but it does not cause error
    data = assert_200(
        client.put(
            f"/topics/{topic1.topic_id}",
            headers=headers(USER2),
            json={"zone_names": []},  # remove zone1?
        )
    )
    assert UUID(data["topic_id"]) == topic1.topic_id
    assert {x["zone_name"] for x in data["zones"]} == {zone1.zone_name}  # zone1 is uncontrollable

    # for user2, zone1 is out of control
    data = assert_200(
        client.put(
            f"/topics/{topic1.topic_id}",
            headers=headers(USER2),
            json={"zone_names": [zone2.zone_name]},
        )
    )
    assert UUID(data["topic_id"]) == topic1.topic_id
    assert {x["zone_name"] for x in data["zones"]} == {zone1.zone_name, zone2.zone_name}

    # keeping uncontrollable zones is ok
    data = assert_200(
        client.put(
            f"/topics/{topic1.topic_id}",
            headers=headers(USER2),
            json={
                "zone_names": [zone1.zone_name]
            },  # keeping uncontrollable zone1 (and remove zone2)
        )
    )
    assert UUID(data["topic_id"]) == topic1.topic_id
    assert {x["zone_name"] for x in data["zones"]} == {zone1.zone_name}


def test_get_authorized():
    def _dict2infos(dict_zones: List[dict]) -> List[schemas.ZoneInfo]:
        return [schemas.ZoneInfo(**x) for x in dict_zones]

    def _dict2entries(dict_zones: List[dict]) -> List[schemas.ZoneEntry]:
        return [schemas.ZoneEntry(**x) for x in dict_zones]

    def _info2entry(zone_info: schemas.ZoneInfo) -> schemas.ZoneEntry:
        return schemas.ZoneEntry(**zone_info.model_dump())

    create_user(USER1)
    data = assert_200(client.get("/zones/authorized_for_me", headers=headers(USER1)))
    assert data["admin"] == []
    assert data["apply"] == []
    assert data["read"] == []

    gteam1 = create_gteam(USER1, GTEAM1)
    zone1 = create_zone(USER1, gteam1.gteam_id, ZONE1)
    data = assert_200(client.get("/zones/authorized_for_me", headers=headers(USER1)))
    assert _dict2infos(data["admin"]) == [zone1]
    assert _dict2entries(data["apply"]) == [_info2entry(zone1)]
    assert _dict2entries(data["read"]) == [_info2entry(zone1)]

    create_user(USER2)
    data = assert_200(client.get("/zones/authorized_for_me", headers=headers(USER2)))
    assert data["admin"] == []
    assert data["apply"] == []
    assert data["read"] == []

    g_invitation = invite_to_gteam(USER1, gteam1.gteam_id)
    accept_gteam_invitation(USER2, g_invitation.invitation_id)
    data = assert_200(client.get("/zones/authorized_for_me", headers=headers(USER2)))
    assert _dict2infos(data["admin"]) == [zone1]
    assert _dict2entries(data["apply"]) == [_info2entry(zone1)]
    assert _dict2entries(data["read"]) == [_info2entry(zone1)]
