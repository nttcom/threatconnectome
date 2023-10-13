from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app
from app.tests.medium.constants import MISPTAG1, MISPTAG2, USER1
from app.tests.medium.utils import create_misp_tag, create_user, headers

client = TestClient(app)


def test_create_misptag():
    create_user(USER1)
    misptag1 = create_misp_tag(USER1, MISPTAG1)
    assert misptag1.tag_name == MISPTAG1
    assert isinstance(misptag1.tag_id, UUID)


def test_get_misptags():
    create_user(USER1)
    create_misp_tag(USER1, MISPTAG1)
    create_misp_tag(USER1, MISPTAG2)
    response = client.get("/misp_tags", headers=headers(USER1))
    assert response.status_code == 200
    responsed_misptags = response.json()
    assert len(responsed_misptags) == 2
    tag_names = [m["tag_name"] for m in responsed_misptags]
    assert MISPTAG1 in tag_names
    assert MISPTAG2 in tag_names


def test_search_misptag():
    create_user(USER1)
    create_misp_tag(USER1, MISPTAG1)
    create_misp_tag(USER1, MISPTAG2)
    params = {"words": ["amber"]}
    response = client.get("/misp_tags/search", headers=headers(USER1), params=params)
    assert response.status_code == 200
    assert len(response.json()) == 1
