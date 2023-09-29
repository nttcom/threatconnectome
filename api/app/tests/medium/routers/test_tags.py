import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.tests.medium.constants import USER1
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    assert_200,
    assert_204,
    create_tag,
    create_user,
    headers,
    schema_to_dict,
)

client = TestClient(app)


def test_create_tag():
    create_user(USER1)

    # creating new child
    str1 = "a1:a2:a3"
    tag1 = create_tag(USER1, str1)
    assert tag1.tag_name == str1
    assert tag1.parent_name == "a1:a2:"
    assert tag1.parent_id != tag1.tag_id

    # creating new parent
    str2 = "b1:b2:"
    tag2 = create_tag(USER1, str2)
    assert tag2.tag_name == str2
    assert tag2.parent_name == tag2.tag_name
    assert tag2.parent_id == tag2.tag_id

    # creating child under existing parent
    str3 = "a1:a2:a3-2"
    tag3 = create_tag(USER1, str3)
    assert tag3.tag_name == str3
    assert tag3.parent_name == tag1.parent_name == "a1:a2:"
    assert tag3.parent_id != tag3.tag_id
    assert tag3.parent_id == tag1.parent_id

    # creating with 4 fields
    str4 = "a1:a2:a3:a4"
    tag4 = create_tag(USER1, str4)
    assert tag4.tag_name == str4
    assert tag4.parent_name == "a1:a2:a3:"
    assert tag4.parent_id != tag4.tag_id

    # another child with 4 fields
    str5 = "a1:a2:a3:a4-2"
    tag5 = create_tag(USER1, str5)
    assert tag5.tag_name == str5
    assert tag5.parent_name == tag4.parent_name == "a1:a2:a3:"
    assert tag5.parent_id == tag4.parent_id

    # create with less than 3 fields
    str6 = "a1:a2"
    tag6 = create_tag(USER1, str6)
    assert tag6.tag_name == str6
    assert tag6.parent_name is None
    assert tag6.parent_id is None

    # create with no separator
    str7 = "a1"
    tag7 = create_tag(USER1, str7)
    assert tag7.tag_name == str7
    assert tag7.parent_name is None
    assert tag7.parent_id is None


def test_get_tags():
    create_user(USER1)

    # add a parent
    str1 = "a1:a2:"
    tag1 = create_tag(USER1, str1)
    data = assert_200(client.get("/tags", headers=headers(USER1)))
    assert len(data) == 1
    assert schema_to_dict(tag1) in data

    # add a child
    str2 = "a1:a2:a3"
    tag2 = create_tag(USER1, str2)
    data = assert_200(client.get("/tags", headers=headers(USER1)))
    assert len(data) == 2
    assert schema_to_dict(tag1) in data
    assert schema_to_dict(tag2) in data

    # add a child with auto-creating parent
    str3 = "b1:b2:b3"
    tag3 = create_tag(USER1, str3)
    data = assert_200(client.get("/tags", headers=headers(USER1)))
    assert len(data) == 4
    assert schema_to_dict(tag1) in data
    data.remove(schema_to_dict(tag1))
    assert schema_to_dict(tag2) in data
    data.remove(schema_to_dict(tag2))
    assert schema_to_dict(tag3) in data
    data.remove(schema_to_dict(tag3))
    # left one is parent of tag3
    assert data[0]["tag_name"] == data[0]["parent_name"] == tag3.parent_name == "b1:b2:"
    assert data[0]["tag_id"] == str(tag3.parent_id)

    # add a short tag without parent
    str4 = "a1:a2"
    tag4 = create_tag(USER1, str4)
    data = assert_200(client.get("/tags", headers=headers(USER1)))
    assert len(data) == 5
    assert schema_to_dict(tag1) in data
    data.remove(schema_to_dict(tag1))
    assert schema_to_dict(tag2) in data
    data.remove(schema_to_dict(tag2))
    assert schema_to_dict(tag3) in data
    data.remove(schema_to_dict(tag3))
    assert schema_to_dict(tag4) in data
    data.remove(schema_to_dict(tag4))
    # left one is parent of tag3
    assert data[0]["tag_name"] == data[0]["parent_name"] == tag3.parent_name == "b1:b2:"
    assert data[0]["tag_id"] == str(tag3.parent_id)


def test_delete_tag():
    create_user(USER1)

    tag1 = create_tag(USER1, "a1:a2:a3")
    assert_204(client.delete(f"/tags/{tag1.tag_id}", headers=headers(USER1)))
    assert_204(client.delete(f"/tags/{tag1.parent_id}", headers=headers(USER1)))

    tag2 = create_tag(USER1, "b1:b2:b3")
    with pytest.raises(
        HTTPError, match=r"400: Bad Request: Cannot delete parent tag while having child tags"
    ):
        assert_204(client.delete(f"/tags/{tag2.parent_id}", headers=headers(USER1)))
    assert_204(client.delete(f"/tags/{tag2.tag_id}", headers=headers(USER1)))
    assert_204(client.delete(f"/tags/{tag2.parent_id}", headers=headers(USER1)))

    tag3 = create_tag(USER1, "xxx")
    assert_204(client.delete(f"/tags/{tag3.tag_id}", headers=headers(USER1)))

    data = assert_200(client.get("/tags", headers=headers(USER1)))
    assert len(data) == 0


@pytest.mark.skip(reason='TODO: need fix syntax error in query at searching with ":"')
def test_search_tag():
    create_user(USER1)

    # tag_1 = create_tag(USER1, 'a1:a2:')
    # tag_11 = create_tag(USER1, 'a1:a2:a3-1')
    # tag_12 = create_tag(USER1, 'a1:a2:a3-2')
    # tag_1 = create_tag(USER1, 'b1:b2:')
    # tag_11 = create_tag(USER1, 'b1:b2:b3-1')
    # tag_12 = create_tag(USER1, 'b1:b2:b3-2')
    # tag_x = create_tag(USER1, 'a2')

    # params = {"words": ["a1:a2:a3-1"]}
    # data = assert_200(client.get("/tags/search", headers=headers(USER1), params=params))
    # assert len(data) == 1
    # assert data[0] == schema_to_dict(tag_11)
    # # TODO: check more
