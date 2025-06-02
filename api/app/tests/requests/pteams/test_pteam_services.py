import io
import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageChops

from app import models, persistence
from app.main import app
from app.tests.medium.constants import (
    PTEAM1,
    PTEAM2,
    USER1,
    USER2,
)
from app.tests.medium.exceptions import HTTPError
from app.tests.medium.utils import (
    assert_200,
    calc_file_sha256,
    compare_references,
    create_pteam,
    create_user,
    file_upload_headers,
    get_pteam_services,
    get_service_by_service_name,
    headers,
    upload_pteam_packages,
)

client = TestClient(app)


def test_get_pteam_services_register_multiple_services():
    create_user(USER1)
    create_user(USER2)
    pteam1 = create_pteam(USER1, PTEAM1)
    pteam2 = create_pteam(USER1, PTEAM2)

    # no services at created pteam
    services1 = get_pteam_services(USER1, pteam1.pteam_id)
    services2 = get_pteam_services(USER1, pteam2.pteam_id)
    assert services1 == services2 == []

    # add service x to pteam1
    service_x = "service_x"
    ext_packages = [
        {
            "package_name": "test_package_name1",
            "ecosystem": "test_ecosystem1",
            "package_manager": "test_package_manager1",
            "references": [{"target": "target1", "version": "1.0"}],
        }
    ]
    upload_pteam_packages(USER1, pteam1.pteam_id, service_x, ext_packages)

    services1a = get_pteam_services(USER1, pteam1.pteam_id)
    services2a = get_pteam_services(USER1, pteam2.pteam_id)
    assert services1a[0].service_name == service_x
    assert services2a == []

    # add grserviceoup y to pteam2
    service_y = "service_y"
    upload_pteam_packages(USER1, pteam2.pteam_id, service_y, ext_packages)

    services1b = get_pteam_services(USER1, pteam1.pteam_id)
    services2b = get_pteam_services(USER1, pteam2.pteam_id)
    assert services1b[0].service_name == service_x
    assert services2b[0].service_name == service_y

    # add service y to pteam1
    upload_pteam_packages(USER1, pteam1.pteam_id, service_y, ext_packages)

    services1c = get_pteam_services(USER1, pteam1.pteam_id)
    services2c = get_pteam_services(USER1, pteam2.pteam_id)

    assert services1c[0].service_name == service_x or service_y
    assert services1c[1].service_name == service_x or service_y
    assert services2c[0].service_name == service_y

    # only members get services
    with pytest.raises(HTTPError, match=r"403: Forbidden: Not a pteam member"):
        get_pteam_services(USER2, pteam1.pteam_id)


@pytest.mark.parametrize(
    "service_request, expected",
    [
        (
            {
                "keywords": ["test_keywords"],
                "description": "test_description",
                "system_exposure": models.SystemExposureEnum.SMALL.value,
                "service_mission_impact": models.MissionImpactEnum.DEGRADED.value,
                "service_safety_impact": models.SafetyImpactEnum.NEGLIGIBLE.value,
            },
            {
                "keywords": ["test_keywords"],
                "description": "test_description",
                "system_exposure": models.SystemExposureEnum.SMALL.value,
                "service_mission_impact": models.MissionImpactEnum.DEGRADED.value,
                "service_safety_impact": models.SafetyImpactEnum.NEGLIGIBLE.value,
            },
        ),
        (
            {
                "keywords": ["test_keywords"],
                "description": "test_description",
            },
            {
                "keywords": ["test_keywords"],
                "description": "test_description",
                "system_exposure": models.SystemExposureEnum.OPEN.value,
                "service_mission_impact": models.MissionImpactEnum.MISSION_FAILURE.value,
                "service_safety_impact": models.SafetyImpactEnum.NEGLIGIBLE.value,
            },
        ),
    ],
)
def test_get_pteam_services_verify_if_all_responses_are_filled(service_request, expected):
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)

    service_name = "service_x"
    ext_packages = [
        {
            "package_name": "test_package_name1",
            "ecosystem": "test_ecosystem1",
            "package_manager": "test_package_manager1",
            "references": [{"target": "fake target", "version": "fake version"}],
        }
    ]
    upload_pteam_packages(USER1, pteam1.pteam_id, service_name, ext_packages)

    service_id1 = get_service_by_service_name(USER1, pteam1.pteam_id, service_name)["service_id"]

    client.put(
        f"/pteams/{pteam1.pteam_id}/services/{service_id1}",
        headers=headers(USER1),
        json=service_request,
    )

    response = client.get(
        f"/pteams/{pteam1.pteam_id}/services",
        headers=headers(USER1),
    )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["service_name"] == service_name
    assert data[0]["service_id"] == service_id1
    assert data[0]["description"] == expected["description"]
    assert data[0]["keywords"] == expected["keywords"]
    assert data[0]["system_exposure"] == expected["system_exposure"]
    assert data[0]["service_mission_impact"] == expected["service_mission_impact"]
    assert data[0]["service_safety_impact"] == expected["service_safety_impact"]


def test_success_upload_service_thumbnail():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    service_x = "service_x"
    ext_packages = [
        {
            "package_name": "test_package_name1",
            "ecosystem": "test_ecosystem1",
            "package_manager": "test_package_manager1",
            "references": [{"target": "fake target", "version": "fake version"}],
        }
    ]
    upload_pteam_packages(USER1, pteam1.pteam_id, service_x, ext_packages)
    service1 = get_pteam_services(USER1, pteam1.pteam_id)[0]

    image_filepath = (
        Path(__file__).resolve().parent.parent / "upload_test" / "image" / "yes_image.png"
    )
    with open(image_filepath, "rb") as image_file:
        response = client.post(
            f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
            headers=file_upload_headers(USER1),
            files={"uploaded": image_file},
        )

    assert response.status_code == 200
    assert response.reason_phrase == "OK"


def test_failed_upload_service_thumbnail_when_wrong_image_size():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    service_x = "service_x"
    ext_packages = [
        {
            "package_name": "test_package_name1",
            "ecosystem": "test_ecosystem1",
            "package_manager": "test_package_manager1",
            "references": [{"target": "fake target", "version": "fake version"}],
        }
    ]
    upload_pteam_packages(USER1, pteam1.pteam_id, service_x, ext_packages)
    service1 = get_pteam_services(USER1, pteam1.pteam_id)[0]

    image_filepath = (
        Path(__file__).resolve().parent.parent / "upload_test" / "image" / "error_image.png"
    )
    with open(image_filepath, "rb") as image_file:
        response = client.post(
            f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
            headers=file_upload_headers(USER1),
            files={"uploaded": image_file},
        )

    assert response.status_code == 400
    assert response.reason_phrase == "Bad Request"
    assert response.json()["detail"] == "Dimensions must be 720 x 480 px"


def test_get_service_thumbnail():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    service_x = "service_x"
    ext_packages = [
        {
            "package_name": "test_package_name1",
            "ecosystem": "test_ecosystem1",
            "package_manager": "test_package_manager1",
            "references": [{"target": "fake target", "version": "fake version"}],
        }
    ]
    upload_pteam_packages(USER1, pteam1.pteam_id, service_x, ext_packages)
    service1 = get_pteam_services(USER1, pteam1.pteam_id)[0]

    image_filepath = (
        Path(__file__).resolve().parent.parent / "upload_test" / "image" / "yes_image.png"
    )
    with open(image_filepath, "rb") as image_file:
        client.post(
            f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
            headers=file_upload_headers(USER1),
            files={"uploaded": image_file},
        )

        response = client.get(
            f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
            headers=headers(USER1),
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        diff_image = ImageChops.difference(
            Image.open(image_file), Image.open(io.BytesIO(response.content))
        )
        assert diff_image.getbbox() is None


def test_delete_service_thumbnail():
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    service_x = "service_x"
    ext_packages = [
        {
            "package_name": "test_package_name1",
            "ecosystem": "test_ecosystem1",
            "package_manager": "test_package_manager1",
            "references": [{"target": "fake target", "version": "fake version"}],
        }
    ]
    upload_pteam_packages(USER1, pteam1.pteam_id, service_x, ext_packages)
    service1 = get_pteam_services(USER1, pteam1.pteam_id)[0]

    image_filepath = (
        Path(__file__).resolve().parent.parent / "upload_test" / "image" / "yes_image.png"
    )
    with open(image_filepath, "rb") as image_file:
        client.post(
            f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
            headers=file_upload_headers(USER1),
            files={"uploaded": image_file},
        )

    delete_response = client.delete(
        f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
        headers=headers(USER1),
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        f"/pteams/{pteam1.pteam_id}/services/{service1.service_id}/thumbnail",
        headers=headers(USER1),
    )
    assert get_response.status_code == 404


def test_remove_pteam_by_service_id(testdb):
    create_user(USER1)
    pteam1 = create_pteam(USER1, PTEAM1)
    service1 = "threatconnectome"
    service2 = "flashsense"

    ext_packages = [
        {
            "package_name": "test_package_name1",
            "ecosystem": "test_ecosystem1",
            "package_manager": "test_package_manager1",
            "references": [{"target": "fake target", "version": "fake version"}],
        }
    ]
    upload_pteam_packages(USER1, pteam1.pteam_id, service1, ext_packages)
    response2 = upload_pteam_packages(USER1, pteam1.pteam_id, service2, ext_packages)

    for extPackage in response2:
        for reference in extPackage.references:
            assert reference.service in [service1, service2]

    def _get_service_id(testdb, pteam_id, service_name):
        pteam = persistence.get_pteam_by_id(testdb, pteam_id)
        for service in pteam.services:
            if service.service_name == service_name:
                return service.service_id
        return None

    service_id = _get_service_id(testdb, pteam1.pteam_id, service1)
    assert service_id

    response = client.delete(
        f"/pteams/{pteam1.pteam_id}/services/{service_id}", headers=headers(USER1)
    )
    assert response.status_code == 204


class TestPostUploadPTeamSbomFile:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        self.user1 = create_user(USER1)
        self.pteam1 = create_pteam(USER1, PTEAM1)

    def test_upload_pteam_sbom_file_with_syft(self):
        # To avoid multiple rows error, pteam2 is created for test
        create_pteam(USER1, PTEAM2)

        params = {"service": "threatconnectome"}
        sbom_file = (
            Path(__file__).resolve().parent.parent / "upload_test" / "test_syft_cyclonedx.json"
        )
        with open(sbom_file, "rb") as tags:
            response = client.post(
                f"/pteams/{self.pteam1.pteam_id}/upload_sbom_file",
                headers=file_upload_headers(USER1),
                params=params,
                files={"file": tags},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["pteam_id"] == str(self.pteam1.pteam_id)
        assert data["service_name"] == params["service"]
        assert data["sbom_file_sha256"] == calc_file_sha256(sbom_file)

    def test_upload_pteam_sbom_file_with_trivy(self):
        # To avoid multiple rows error, pteam2 is created for test
        create_pteam(USER1, PTEAM2)

        params = {"service": "threatconnectome"}
        sbom_file = (
            Path(__file__).resolve().parent.parent / "upload_test" / "test_trivy_cyclonedx.json"
        )
        with open(sbom_file, "rb") as tags:
            response = client.post(
                f"/pteams/{self.pteam1.pteam_id}/upload_sbom_file",
                headers=file_upload_headers(USER1),
                params=params,
                files={"file": tags},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["pteam_id"] == str(self.pteam1.pteam_id)
        assert data["service_name"] == params["service"]
        assert data["sbom_file_sha256"] == calc_file_sha256(sbom_file)

    def test_upload_pteam_sbom_file_with_empty_file(self):
        params = {"service": "threatconnectome"}
        sbom_file = Path(__file__).resolve().parent.parent / "upload_test" / "empty.json"
        with open(sbom_file, "rb") as tags:
            response = client.post(
                f"/pteams/{self.pteam1.pteam_id}/upload_sbom_file",
                headers=file_upload_headers(USER1),
                params=params,
                files={"file": tags},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Upload file is empty"

    def test_upload_pteam_sbom_file_with_wrong_filename(self):
        params = {"service": "threatconnectome"}
        sbom_file = Path(__file__).resolve().parent.parent / "upload_test" / "package.txt"
        with open(sbom_file, "rb") as tags:
            response = client.post(
                f"/pteams/{self.pteam1.pteam_id}/upload_sbom_file",
                headers=file_upload_headers(USER1),
                params=params,
                files={"file": tags},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Please upload a file with .json as extension"

    def test_it_should_return_422_when_upload_sbom_with_over_255_char_servicename(self):
        # create 256 alphanumeric characters
        service_name = "a" * 256

        params = {"service": service_name}
        sbom_file = (
            Path(__file__).resolve().parent.parent / "upload_test" / "test_trivy_cyclonedx.json"
        )
        with open(sbom_file, "rb") as tags:
            response = client.post(
                f"/pteams/{self.pteam1.pteam_id}/upload_sbom_file",
                headers=file_upload_headers(USER1),
                params=params,
                files={"file": tags},
            )

        assert response.status_code == 422
        data = response.json()
        assert data["detail"] == "Length of Service name exceeds 255 characters"

    @pytest.mark.skip(reason="TODO: need api to get background task status")
    def test_upload_pteam_sbom_file_wrong_content_format(self):
        params = {"service": "threatconnectome"}
        sbom_file = (
            Path(__file__).resolve().parent.parent / "upload_test" / "tag_with_wrong_format.json"
        )
        with open(sbom_file, "rb") as tags:
            with pytest.raises(HTTPError, match=r"400: Bad Request: Not supported file format"):
                assert_200(
                    client.post(
                        f"/pteams/{self.pteam1.pteam_id}/upload_sbom_file",
                        headers=file_upload_headers(USER1),
                        params=params,
                        files={"file": tags},
                    )
                )


class TestPostUploadPackagesFile:
    @pytest.fixture(scope="function", autouse=True)
    def common_setup(self):
        # Given
        create_user(USER1)
        self.pteam1 = create_pteam(USER1, PTEAM1)

    def _eval_upload_packages_file_with_string(self, blines_, params_):
        with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tfile:
            for bline in blines_:
                tfile.writelines(bline + "\n")
            tfile.flush()
            tfile.seek(0)
            with open(tfile.name, "rb") as bfile:
                response = client.post(
                    f"/pteams/{self.pteam1.pteam_id}/upload_packages_file",
                    headers=file_upload_headers(USER1),
                    files={"file": bfile},
                    params=params_,
                )
                return response

    def _eval_upload_packages_file_with_dict(self, lines_, params_):
        with tempfile.NamedTemporaryFile(mode="w+t", suffix=".jsonl") as tfile:
            for line in lines_:
                tfile.writelines(json.dumps(line) + "\n")
            tfile.flush()
            tfile.seek(0)
            with open(tfile.name, "rb") as bfile:
                response = client.post(
                    f"/pteams/{self.pteam1.pteam_id}/upload_packages_file",
                    headers=file_upload_headers(USER1),
                    files={"file": bfile},
                    params=params_,
                )
                return response

    @staticmethod
    def _compare_ext_packages(_package1: dict, _package2: dict) -> bool:
        if not isinstance(_package1, dict) or not isinstance(_package2, dict):
            return False
        _keys = {"package_name", "ecosystem"}
        if any(_package1.get(_key) != _package2.get(_key) for _key in _keys):
            return False
        return compare_references(_package1["references"], _package2["references"])

    def _compare_responsed_packages(self, _packages1: list[dict], _packages2: list[dict]) -> bool:
        if not isinstance(_packages1, list) or not isinstance(_packages2, list):
            return False
        if len(_packages1) != len(_packages2):
            return False
        return all(
            self._compare_ext_packages(_packages1[_idx], _packages2[_idx])
            for _idx in range(len(_packages1))
        )

    def test_it_should_return_200_when_upload_1_line_file(self):
        # Given
        params = {"service": "threatconnectome"}
        # upload a line
        lines = [
            '{"package_name":"test_package_name",'
            '"ecosystem":"test_ecosystem",'
            '"package_manager": "test_package_manager",'
            '"references":[{"target":"api/Pipfile.lock","version":"1.0"}]}'
        ]

        # When
        response = self._eval_upload_packages_file_with_string(lines, params)

        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["package_name"] == "test_package_name"
        assert data[0]["ecosystem"] == "test_ecosystem"
        assert compare_references(
            data[0]["references"],
            [
                {
                    "service": params["service"],
                    "target": "api/Pipfile.lock",
                    "version": "1.0",
                    "package_manager": "test_package_manager",
                }
            ],
        )

    def test_it_should_return_200_when_upload_2_lines_file(self):
        # Given
        params = {"service": "threatconnectome"}
        # upload 2 lines
        lines = [
            '{"package_name":"test_package_name1",'
            '"ecosystem":"test_ecosystem1",'
            '"package_manager": "test_package_manager1",'
            '"references":[{"target":"api/Pipfile.lock","version":"1.0"}]}',
            '{"package_name":"test_package_name2",'
            '"ecosystem":"test_ecosystem2",'
            '"package_manager": "test_package_manager2",'
            '"references":[{"target":"api/Pipfile.lock","version":"1.0"},'
            '{"target":"api3/Pipfile.lock","version":"0.1"}]}',
        ]

        # When
        response = self._eval_upload_packages_file_with_string(lines, params)

        # Then
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2

        package_names = {d["package_name"] for d in data}
        ecosystems = {d["ecosystem"] for d in data}
        assert "test_package_name1" in package_names
        assert "test_package_name2" in package_names
        assert "test_ecosystem1" in ecosystems
        assert "test_ecosystem2" in ecosystems

        data_by_name = {d["package_name"]: d for d in data}
        assert compare_references(
            data_by_name["test_package_name1"]["references"],
            [
                {
                    "service": params["service"],
                    "target": "api/Pipfile.lock",
                    "version": "1.0",
                    "package_manager": "test_package_manager1",
                }
            ],
        )
        assert compare_references(
            data_by_name["test_package_name2"]["references"],
            [
                {
                    "service": params["service"],
                    "target": "api/Pipfile.lock",
                    "version": "1.0",
                    "package_manager": "test_package_manager2",
                },
                {
                    "service": params["service"],
                    "target": "api3/Pipfile.lock",
                    "version": "0.1",
                    "package_manager": "test_package_manager2",
                },
            ],
        )

    def test_it_should_return_200_when_upload_duplicated_lines_file(self):
        # Given
        params = {"service": "threatconnectome"}
        # upload duplicated lines
        lines = [
            '{"package_name":"test_package_name1",'
            '"ecosystem":"test_ecosystem1",'
            '"package_manager": "test_package_manager1",'
            '"references":[{"target":"api/Pipfile.lock","version":"1.0"}]}',
            '{"package_name":"test_package_name2",'
            '"ecosystem":"test_ecosystem2",'
            '"package_manager": "test_package_manager2",'
            '"references":[{"target":"api/Pipfile.lock","version":"1.0"},'
            '{"target":"api3/Pipfile.lock","version":"0.1"}]}',
            '{"package_name":"test_package_name2",'
            '"ecosystem":"test_ecosystem2",'
            '"package_manager": "test_package_manager2",'
            '"references":[{"target":"api/Pipfile.lock","version":"1.0"},'
            '{"target":"api3/Pipfile.lock","version":"0.1"}]}',
        ]

        # When
        response = self._eval_upload_packages_file_with_string(lines, params)

        # Then
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2

        package_names = {d["package_name"] for d in data}
        ecosystems = {d["ecosystem"] for d in data}
        assert "test_package_name1" in package_names
        assert "test_package_name2" in package_names
        assert "test_ecosystem1" in ecosystems
        assert "test_ecosystem2" in ecosystems

        data_by_name = {d["package_name"]: d for d in data}
        assert compare_references(
            data_by_name["test_package_name1"]["references"],
            [
                {
                    "service": params["service"],
                    "target": "api/Pipfile.lock",
                    "version": "1.0",
                    "package_manager": "test_package_manager1",
                }
            ],
        )
        assert compare_references(
            data_by_name["test_package_name2"]["references"],
            [
                {
                    "service": params["service"],
                    "target": "api/Pipfile.lock",
                    "version": "1.0",
                    "package_manager": "test_package_manager2",
                },
                {
                    "service": params["service"],
                    "target": "api3/Pipfile.lock",
                    "version": "0.1",
                    "package_manager": "test_package_manager2",
                },
            ],
        )

    def test_it_should_be_able_to_take_pteam_data_together(self):
        # Given
        service_a = {"service": "service-a"}
        service_b = {"service": "service-b"}

        lines_a = [
            {
                "package_name": "test_package_name1",
                "ecosystem": "test_ecosystem1",
                "package_manager": "test_package_manager1",
                "references": [{"target": "target1", "version": "1.0"}],
            },
        ]
        lines_b = [
            {
                "package_name": "test_package_name2",
                "ecosystem": "test_ecosystem2",
                "package_manager": "test_package_manager2",
                "references": [
                    {"target": "target2", "version": "1.0"},
                    {"target": "target2", "version": "1.1"},  # multiple version in one target
                ],
            }
        ]

        # When
        self._eval_upload_packages_file_with_dict(lines_a, service_a)
        response = self._eval_upload_packages_file_with_dict(lines_b, service_b)

        # Then
        exp_a = {
            "package_name": "test_package_name1",
            "ecosystem": "test_ecosystem1",
            "references": [
                {
                    "target": "target1",
                    "version": "1.0",
                    "service": "service-a",
                    "package_manager": "test_package_manager1",
                },
            ],
        }
        exp_b = {
            "package_name": "test_package_name2",
            "ecosystem": "test_ecosystem2",
            "references": [
                {
                    "target": "target2",
                    "version": "1.0",
                    "service": "service-b",
                    "package_manager": "test_package_manager2",
                },
                {
                    "target": "target2",
                    "version": "1.1",
                    "service": "service-b",
                    "package_manager": "test_package_manager2",
                },
            ],
        }
        assert self._compare_responsed_packages(response.json(), [exp_a, exp_b])

    def test_it_should_update_when_the_same_service_name(self):
        # Given
        service_a = {"service": "service-a"}
        lines_a = [
            {
                "package_name": "test_package_name1",
                "ecosystem": "test_ecosystem1",
                "package_manager": "test_package_manager1",
                "references": [
                    {"target": "target1", "version": "1.2"},
                ],
            }
        ]
        lines_b = [
            {
                "package_name": "test_package_name2",
                "ecosystem": "test_ecosystem2",
                "package_manager": "test_package_manager2",
                "references": [
                    {"target": "target2", "version": "1.5"},
                ],
            }
        ]
        self._eval_upload_packages_file_with_dict(lines_a, service_a)

        # When
        data = self._eval_upload_packages_file_with_dict(lines_b, service_a)

        # Then
        exp = {
            "package_name": "test_package_name2",
            "ecosystem": "test_ecosystem2",
            "references": [
                {
                    "target": "target2",
                    "version": "1.5",
                    "service": "service-a",
                    "package_manager": "test_package_manager2",
                },
            ],
        }
        assert self._compare_responsed_packages(data.json(), [exp])

    def test_it_should_return_400_with_wrong_filename(self):
        # When
        params = {"service": "threatconnectome"}
        package_file = Path(__file__).resolve().parent.parent / "upload_test" / "package.txt"
        with open(package_file, "rb") as packages:
            response = client.post(
                f"/pteams/{self.pteam1.pteam_id}/upload_packages_file",
                headers=file_upload_headers(USER1),
                files={"file": packages},
                params=params,
            )

        # Then
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Please upload a file with .jsonl as extension"

    def test_it_should_return_400_without_package_name(self):
        # Given
        params = {"service": "threatconnectome"}

        lines = [
            '{"p":"test_package_name",'
            '"ecosystem":"test_ecosystem",'
            '"package_manager": "test_package_manager",'
            '"references":[{"target":"api/Pipfile.lock","version":"1.0"}]}'
        ]

        # When
        response = self._eval_upload_packages_file_with_string(lines, params)

        # Then
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Missing package name"

    def test_it_should_return_400_with_wrong_content_format(self):
        # Given
        params = {"service": "threatconnectome"}

        lines = ['{"test":"wrong file"},']

        # When
        response = self._eval_upload_packages_file_with_string(lines, params)

        # Then
        assert response.status_code == 400
        data = response.json()
        assert "Wrong file content" in data["detail"]


class TestUpdatePTeamService:
    class Common:
        @pytest.fixture(scope="function", autouse=True)
        def common_setup(self):
            self.user1 = create_user(USER1)
            self.pteam1 = create_pteam(USER1, PTEAM1)
            test_service = "test_service"
            test_target = "test target"
            test_version = "1.2.3"
            ext_packages = [
                {
                    "package_name": "alpha",
                    "ecosystem": "alpha2",
                    "package_manager": "alpha3",
                    "references": [{"target": test_target, "version": test_version}],
                }
            ]
            upload_pteam_packages(USER1, self.pteam1.pteam_id, test_service, ext_packages)
            self.service_id1 = get_service_by_service_name(
                USER1, self.pteam1.pteam_id, test_service
            )["service_id"]

        @staticmethod
        def _get_access_token(user: dict) -> str:
            body = {
                "username": user["email"],
                "password": user["pass"],
            }
            response = client.post("/auth/token", data=body)
            if response.status_code != 200:
                raise HTTPError(response)
            data = response.json()
            return data["access_token"]

    class TestServiceName(Common):
        error_too_long_service_name = (
            "Too long service name. Max length is 255 in half-width or 127 in full-width"
        )
        chars_255_in_half = "1" * 255
        chars_127_in_full = "１" * 127
        complex_255_in_half = "1１" * 85

        @pytest.mark.parametrize(
            "service_name, expected",
            [
                ("", ""),
                ("   ", ""),
                (chars_255_in_half, chars_255_in_half),
                (chars_255_in_half + "  ", chars_255_in_half),
                (chars_127_in_full, chars_127_in_full),
                (chars_127_in_full + " ", chars_127_in_full),
                (chars_127_in_full + "　", chars_127_in_full),
                (complex_255_in_half, complex_255_in_half),
                (complex_255_in_half + " ", complex_255_in_half),
                (complex_255_in_half + "　", complex_255_in_half),
            ],
        )
        def test_it_should_return_200_when_service_name_within_limits(self, service_name, expected):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"service_name": service_name}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["service_name"] == expected

        @pytest.mark.parametrize(
            "service_name, expected",
            [
                (chars_255_in_half + "x", error_too_long_service_name),
                (chars_127_in_full + "ｘ", error_too_long_service_name),
                (complex_255_in_half + "x", error_too_long_service_name),
                (complex_255_in_half + "ｘ", error_too_long_service_name),
            ],
        )
        def test_it_should_return_400_when_service_name_too_long(self, service_name, expected):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"service_name": service_name}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 400
            assert response.json()["detail"] == expected

        @pytest.mark.parametrize(
            "service_name, expected",
            [
                (None, "Cannot specify None for service_name"),
            ],
        )
        def test_it_should_return_400_when_service_name_is_None(self, service_name, expected):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"service_name": service_name}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 400
            assert response.json()["detail"] == expected

        def test_it_should_return_200_when_service_name_is_not_specify(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"keywords": []}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["service_name"] == "test_service"

        def test_it_should_return_400_when_naming_the_same_service_in_the_same_pteam(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            test_service = "test_service1"
            test_target = "test target"
            test_version = "1.2.3"
            ext_packages = [
                {
                    "package_name": "alpha",
                    "ecosystem": "alpha2",
                    "package_manager": "alpha3",
                    "references": [{"target": test_target, "version": test_version}],
                }
            ]
            upload_pteam_packages(USER1, self.pteam1.pteam_id, test_service, ext_packages)

            request = {"service_name": test_service}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 400
            assert response.json()["detail"] == "Service name already exists in the same team"

    class TestKeywords(Common):
        @pytest.mark.parametrize(
            "keywords, expected",
            [
                (None, "Cannot specify None for keywords"),
                ([], []),
                (["1"], ["1"]),
                (["1", "2"], ["1", "2"]),
                (["3", "1", "2"], ["1", "2", "3"]),
                (["2", "4", "1", "3"], ["1", "2", "3", "4"]),
                (["1", "2", "3", "4", "5"], ["1", "2", "3", "4", "5"]),
                (["1", "2", "3", "4", "5", "6"], "Too many keywords, max number: 5"),
                (["1", "2", "3", "3", "1", "2"], ["1", "2", "3"]),  # duplications are unified
            ],
        )
        def test_number_of_keywords(self, keywords, expected):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"keywords": keywords}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            if isinstance(expected, str):  # error cases
                assert response.status_code == 400
                assert response.json()["detail"] == expected
            else:
                assert response.status_code == 200
                assert response.json()["keywords"] == expected

        error_too_long_keyword = (
            "Too long keyword. Max length is 20 in half-width or 10 in full-width"
        )
        chars_20_in_half = "123456789_123456789_"
        chars_10_in_full = "１２３４５６７８９０"
        complex_20_in_half = "123456789_１２３４５"

        @pytest.mark.parametrize(
            "keyword, expected",
            [
                ("", []),
                ("   ", []),
                (chars_20_in_half, [chars_20_in_half]),
                (" " + chars_20_in_half + " ", [chars_20_in_half]),
                (chars_20_in_half + "x", error_too_long_keyword),
                (chars_10_in_full, [chars_10_in_full]),
                (" " + chars_10_in_full + " ", [chars_10_in_full]),
                ("　" + chars_10_in_full + "　", [chars_10_in_full]),  # \u3000 is also stripped
                (chars_10_in_full + "x", error_too_long_keyword),
                (chars_10_in_full + "ｘ", error_too_long_keyword),
                (complex_20_in_half, [complex_20_in_half]),
                (" " + complex_20_in_half + " ", [complex_20_in_half]),
                ("　" + complex_20_in_half + "　", [complex_20_in_half]),
                (complex_20_in_half + "x", error_too_long_keyword),
                (complex_20_in_half + "ｘ", error_too_long_keyword),
            ],
        )
        def test_length_of_keyword(self, keyword, expected):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"keywords": [keyword]}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            if isinstance(expected, str):  # error cases
                assert response.status_code == 400
                assert response.json()["detail"] == expected
            else:
                assert response.status_code == 200
                assert response.json()["keywords"] == expected

        def test_it_should_return_200_when_keyword_is_not_specify(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"description": "keywords not specify"}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["keywords"] == []

    class TestDescription(Common):

        error_too_long_description = (  # HACK: define as a tuple instead of str
            "Too long description. Max length is 300 in half-width or 150 in full-width",
        )
        chars_300_in_half = "123456789_" * 30
        chars_150_in_full = "１２３４５６７８９＿" * 15
        complex_300_in_half = "123456789_１２３４５６７８９＿" * 10

        @pytest.mark.parametrize(
            "description, expected",
            [
                (None, None),
                ("", None),
                ("   ", None),
                (chars_300_in_half, chars_300_in_half),
                (chars_300_in_half + "  ", chars_300_in_half),
                (chars_300_in_half + "x", error_too_long_description),
                (chars_150_in_full, chars_150_in_full),
                (chars_150_in_full + " ", chars_150_in_full),
                (chars_150_in_full + "　", chars_150_in_full),
                (chars_150_in_full + "ｘ", error_too_long_description),
                (complex_300_in_half, complex_300_in_half),
                (complex_300_in_half + " ", complex_300_in_half),
                (complex_300_in_half + "　", complex_300_in_half),
                (complex_300_in_half + "x", error_too_long_description),
                (complex_300_in_half + "ｘ", error_too_long_description),
            ],
        )
        def test_length_of_description(self, description, expected):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"description": description}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            if isinstance(expected, tuple):  # error case
                assert response.status_code == 400
                assert response.json()["detail"] == expected[0]
            else:
                assert response.status_code == 200
                assert response.json()["description"] == expected

        def test_it_should_return_200_when_description_is_not_specify(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"keywords": []}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["description"] is None

    class TestSystemExposure(Common):
        @pytest.mark.parametrize(
            "system_exposure, expected",
            [
                ("open", models.SystemExposureEnum.OPEN),
                ("controlled", models.SystemExposureEnum.CONTROLLED),
                ("small", models.SystemExposureEnum.SMALL),
            ],
        )
        def test_it_should_return_200_when_system_exposure_is_SystemExposureEnum(
            self, system_exposure, expected
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"system_exposure": system_exposure}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["system_exposure"] == expected

        def test_it_should_return_200_when_system_exposure_is_not_specify(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"description": "system_exposure not specify"}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["system_exposure"] == models.SystemExposureEnum.OPEN

        error_msg_system_exposure = "Input should be 'open', 'controlled' or 'small'"

        def test_it_should_return_400_when_system_exposure_is_None(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"system_exposure": None}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 400
            assert response.json()["detail"] == "Cannot specify None for system_exposure"

        @pytest.mark.parametrize(
            "system_exposure, expected",
            [
                (1, error_msg_system_exposure),
                ("test", error_msg_system_exposure),
            ],
        )
        def test_it_should_return_422_when_system_exposure_is_not_SystemExposureEnum(
            self, system_exposure, expected
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"system_exposure": system_exposure}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 422
            assert response.json()["detail"][0]["msg"] == expected

    class TestMissionImpact(Common):
        @pytest.mark.parametrize(
            "service_mission_impact, expected",
            [
                ("mission_failure", models.MissionImpactEnum.MISSION_FAILURE),
                ("mef_failure", models.MissionImpactEnum.MEF_FAILURE),
                ("mef_support_crippled", models.MissionImpactEnum.MEF_SUPPORT_CRIPPLED),
                ("degraded", models.MissionImpactEnum.DEGRADED),
            ],
        )
        def test_it_should_return_200_when_mission_impact_is_MissionImpactEnum(
            self, service_mission_impact, expected
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"service_mission_impact": service_mission_impact}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["service_mission_impact"] == expected

        def test_it_should_return_200_when_mission_impact_is_not_specify(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"description": "service_mission_impact not specify"}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200
            assert (
                response.json()["service_mission_impact"]
                == models.MissionImpactEnum.MISSION_FAILURE
            )

        error_msg_service_mission_impact = (
            "Input should be 'mission_failure', 'mef_failure', 'mef_support_crippled' or 'degraded'"
        )

        def test_it_should_return_400_when_mission_impact_is_None(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"service_mission_impact": None}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 400
            assert response.json()["detail"] == "Cannot specify None for service_mission_impact"

        @pytest.mark.parametrize(
            "service_mission_impact, expected",
            [
                (
                    1,
                    error_msg_service_mission_impact,
                ),
                (
                    "test",
                    error_msg_service_mission_impact,
                ),
            ],
        )
        def test_it_should_return_422_when_mission_impact_is_not_MissionImpactEnum(
            self, service_mission_impact, expected
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"service_mission_impact": service_mission_impact}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 422
            assert response.json()["detail"][0]["msg"] == expected

    class TestSafetyImpactEnum(Common):
        @pytest.mark.parametrize(
            "safety_impact, expected",
            [
                ("catastrophic", models.SafetyImpactEnum.CATASTROPHIC),
                ("critical", models.SafetyImpactEnum.CRITICAL),
                ("marginal", models.SafetyImpactEnum.MARGINAL),
                ("negligible", models.SafetyImpactEnum.NEGLIGIBLE),
            ],
        )
        def test_it_should_return_200_when_safety_impact_is_SafetyImpactEnum(
            self, safety_impact, expected
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"service_safety_impact": safety_impact}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 200
            assert response.json()["service_safety_impact"] == expected

        def test_it_should_return_200_when_safety_impact_is_not_specify(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"description": "safety_impact not specify"}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )
            assert response.status_code == 200
            assert response.json()["service_safety_impact"] == models.SafetyImpactEnum.NEGLIGIBLE

        def test_it_should_return_400_when_safety_impact_is_None(self):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }
            request = {"service_safety_impact": None}
            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 400
            assert response.json()["detail"] == "Cannot specify None for service_safety_impact"

        error_msg_safety_impact = (
            "Input should be 'catastrophic', 'critical', 'marginal' or 'negligible'"
        )

        @pytest.mark.parametrize(
            "safety_impact, expected",
            [
                (1, error_msg_safety_impact),
                ("test", error_msg_safety_impact),
            ],
        )
        def test_it_should_return_422_when_safety_impact_is_not_SafetyImpactEnum(
            self, safety_impact, expected
        ):
            user1_access_token = self._get_access_token(USER1)
            _headers = {
                "Authorization": f"Bearer {user1_access_token}",
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            request = {"service_safety_impact": safety_impact}

            response = client.put(
                f"/pteams/{self.pteam1.pteam_id}/services/{self.service_id1}",
                headers=_headers,
                json=request,
            )

            assert response.status_code == 422
            assert response.json()["detail"][0]["msg"] == expected
