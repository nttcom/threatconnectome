from typing import Any, Type

import pytest
from fastapi.testclient import TestClient

from app import schemas
from app.main import app
from app.tests.medium.constants import (
    PTEAM1,
    TAG1,
    TAG2,
    TOPIC1,
    USER1,
)
from app.tests.medium.utils import (
    create_pteam,
    create_tag,
    create_topic,
    create_user,
    upload_pteam_tags,
)

client = TestClient(app)


class TestAutoClose:
    class _Util:
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
                upload_pteam_tags(USER1, self.pteam1.pteam_id, "service1", refs0)
                self.topic1 = create_topic(
                    USER1,
                    {
                        **TOPIC1,
                        "tags": [TAG1, TAG2],
                        "actions": [],
                    },
                )

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
                upload_pteam_tags(USER1, self.pteam1.pteam_id, "service1", refs0)
                self.topic1 = create_topic(
                    USER1,
                    {
                        **TOPIC1,
                        "tags": [TAG1, TAG2],
                        "actions": [],
                    },
                )

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
