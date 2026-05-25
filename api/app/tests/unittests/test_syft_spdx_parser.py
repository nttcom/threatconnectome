import json

import pytest

from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.syft_spdx_parser import SyftSPDXParser
from app.sbom.sbom_analyzer import sbom_json_to_artifact_json_lines
from app.utility.progress_logger import TimeBasedProgressLogger


@pytest.fixture(scope="function")
def progress():
    progress = TimeBasedProgressLogger(
        title="test", pteam_id="test_pteam", service_name="test_service"
    )
    yield progress
    progress.stop()


class TestSyftSPDXParser:
    def _make_sbom(self) -> dict:
        return {
            "spdxVersion": "SPDX-2.3",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "sample-spdx",
            "dataLicense": "CC0-1.0",
            "documentNamespace": "https://example.com/spdxdocs/sample",
            "creationInfo": {
                "created": "2026-05-07T00:00:00Z",
                "creators": ["Tool: syft-1.22.0"],
            },
            "packages": [
                {
                    "SPDXID": "SPDXRef-ContainerImage-sample",
                    "name": "root-image",
                    "versionInfo": "sha256:abc",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                    "primaryPackagePurpose": "CONTAINER",
                },
                {
                    "SPDXID": "SPDXRef-Package-libcrypto3",
                    "name": "libcrypto3",
                    "versionInfo": "3.5.0-r0",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                    "packageFileName": "/lib/apk/db/installed",
                    "externalRefs": [
                        {
                            "referenceCategory": "PACKAGE_MANAGER",
                            "referenceType": "purl",
                            "referenceLocator": (
                                "pkg:apk/alpine/libcrypto3@3.5.0-r0?arch=aarch64"
                                "&distro=alpine-3.22.0&upstream=openssl"
                            ),
                        }
                    ],
                },
                {
                    "SPDXID": "SPDXRef-Package-PyJWT",
                    "name": "PyJWT",
                    "versionInfo": "1.5.3",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                    "packageFileName": "requirements.txt",
                    "externalRefs": [
                        {
                            "referenceCategory": "PACKAGE_MANAGER",
                            "referenceType": "purl",
                            "referenceLocator": "pkg:pypi/PyJWT@1.5.3",
                        }
                    ],
                },
                {
                    "SPDXID": "SPDXRef-Package-attrs",
                    "name": "attrs",
                    "versionInfo": "25.4.0",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                    "externalRefs": [
                        {
                            "referenceCategory": "PACKAGE-MANAGER",
                            "referenceType": "purl",
                            "referenceLocator": "pkg:pypi/attrs@25.4.0",
                        }
                    ],
                },
            ],
            "files": [
                {
                    "SPDXID": "SPDXRef-File-Pipfile.lock",
                    "fileName": "Pipfile.lock",
                },
            ],
            "relationships": [
                {
                    "spdxElementId": "SPDXRef-DOCUMENT",
                    "relationshipType": "DESCRIBES",
                    "relatedSpdxElement": "SPDXRef-ContainerImage-sample",
                },
                {
                    "spdxElementId": "SPDXRef-ContainerImage-sample",
                    "relationshipType": "CONTAINS",
                    "relatedSpdxElement": "SPDXRef-Package-libcrypto3",
                },
                {
                    "spdxElementId": "SPDXRef-ContainerImage-sample",
                    "relationshipType": "DEPENDS_ON",
                    "relatedSpdxElement": "SPDXRef-Package-PyJWT",
                },
                {
                    "spdxElementId": "SPDXRef-DocumentRoot-File-Pipfile.lock",
                    "relationshipType": "CONTAINS",
                    "relatedSpdxElement": "SPDXRef-Package-attrs",
                },
                {
                    "spdxElementId": "SPDXRef-Package-attrs",
                    "relationshipType": "OTHER",
                    "relatedSpdxElement": "SPDXRef-File-Pipfile.lock",
                    "comment": (
                        "evident-by: indicates the package's existence is evident by "
                        "the given file"
                    ),
                },
            ],
        }

    def _make_syft_snapshot_like_sbom(self) -> dict:
        return {
            "spdxVersion": "SPDX-2.3",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": "user-image-input",
            "dataLicense": "CC0-1.0",
            "documentNamespace": "https://example.com/spdxdocs/user-image-input",
            "creationInfo": {
                "created": "2026-05-07T00:00:00Z",
                "creators": [
                    "Organization: Anchore, Inc",
                    "Tool: syft-v0.42.0-bogus",
                ],
            },
            "packages": [
                {
                    "SPDXID": "SPDXRef-Package-deb-package-2-4b756c6f6fb127a3",
                    "name": "package-2",
                    "versionInfo": "2.0.1",
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                    "externalRefs": [
                        {
                            "referenceCategory": "SECURITY",
                            "referenceType": "cpe23Type",
                            "referenceLocator": "cpe:2.3:*:some:package:2:*:*:*:*:*:*:*",
                        },
                        {
                            "referenceCategory": "PACKAGE-MANAGER",
                            "referenceType": "purl",
                            "referenceLocator": "pkg:deb/debian/package-2@2.0.1",
                        },
                    ],
                },
                {
                    "SPDXID": "SPDXRef-DocumentRoot-Image-user-image-input",
                    "name": "user-image-input",
                    "versionInfo": (
                        "sha256:2731251dc34951c0e50fcc643b4c5f74922dad1a5d98f302"
                        "b504cf46cd5d9368"
                    ),
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                    "externalRefs": [
                        {
                            "referenceCategory": "PACKAGE-MANAGER",
                            "referenceType": "purl",
                            "referenceLocator": (
                                "pkg:oci/user-image-input@sha256%3A2731251dc34951c0e50fcc643b4c5f74922dad1a5d98f302"
                                "b504cf46cd5d9368?arch="
                            ),
                        }
                    ],
                    "primaryPackagePurpose": "CONTAINER",
                },
            ],
            "relationships": [
                {
                    "spdxElementId": "SPDXRef-DocumentRoot-Image-user-image-input",
                    "relationshipType": "CONTAINS",
                    "relatedSpdxElement": "SPDXRef-Package-deb-package-2-4b756c6f6fb127a3",
                },
                {
                    "spdxElementId": "SPDXRef-DOCUMENT",
                    "relationshipType": "DESCRIBES",
                    "relatedSpdxElement": "SPDXRef-DocumentRoot-Image-user-image-input",
                },
            ],
        }

    def test_it_should_extract_artifacts_with_same_format(
        self, progress: TimeBasedProgressLogger
    ):
        # Given
        sbom_info = SBOMInfo(
            spec_name="SPDX",
            spec_version="2.3",
            tool_name="syft",
            tool_version="1.22.0",
        )

        # When
        artifacts = SyftSPDXParser.parse_sbom(self._make_sbom(), sbom_info, progress)

        # Then
        assert len(artifacts) == 3
        artifact_map = {artifact.package_name: artifact for artifact in artifacts}

        assert artifact_map["libcrypto3"].source_name == "openssl"
        assert artifact_map["libcrypto3"].ecosystem == "alpine-3.22.0"
        assert artifact_map["libcrypto3"].package_manager == ""
        assert ("root-image", "3.5.0-r0") in artifact_map["libcrypto3"].targets

        assert artifact_map["pyjwt"].source_name is None
        assert artifact_map["pyjwt"].ecosystem == "pypi"
        assert artifact_map["pyjwt"].package_manager == "pip"
        assert ("root-image", "1.5.3") in artifact_map["pyjwt"].targets

        assert artifact_map["attrs"].source_name is None
        assert artifact_map["attrs"].ecosystem == "pypi"
        assert artifact_map["attrs"].package_manager == "pipenv"
        assert ("Pipfile.lock", "25.4.0") in artifact_map["attrs"].targets

    def test_it_should_parse_through_sbom_analyzer(
        self, progress: TimeBasedProgressLogger
    ):
        # Given
        sbom_str = json.dumps(self._make_sbom())

        # When
        lines = sbom_json_to_artifact_json_lines(sbom_str, progress)

        # Then
        assert len(lines) == 3
        assert set(lines[0].keys()) == {
            "package_name",
            "source_name",
            "ecosystem",
            "package_manager",
            "references",
        }
        assert lines[0]["references"]

    def test_it_should_support_syft_snapshot_style_creator_and_ignore_document_root(
        self, progress: TimeBasedProgressLogger
    ):
        # Given
        sbom_str = json.dumps(self._make_syft_snapshot_like_sbom())

        # When
        lines = sbom_json_to_artifact_json_lines(sbom_str, progress)

        # Then
        assert lines == [
            {
                "package_name": "package-2",
                "source_name": None,
                "ecosystem": "deb",
                "package_manager": "",
                "references": [
                    {
                        "version": "2.0.1",
                        "target": "user-image-input",
                    }
                ],
            }
        ]
