from cyclonedx.model.bom import Bom

from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.syft_cdx_parser import SyftCDXParser


class TestSyftCDXParser:
    def test_it_should_unescape_purl_and_extract_correct_package_name_and_ecosystem(self):
        sbom = {
            "metadata": {
                "component": {
                    "bom-ref": "root-app",
                    "type": "application",
                    "name": "sample target1",
                }
            },
            "components": [
                {
                    "bom-ref": "root-app",
                    "type": "application",
                    "name": "sample target1",
                    "properties": [
                        {"name": "syft:package:type", "value": "npm"},
                        {"name": "syft:package:class", "value": "lang-pkgs"},
                    ],
                },
                {
                    "bom-ref": "pkg:npm/%40babel/code-frame@7.0.0",
                    "type": "library",
                    "name": "@babel/code-frame",
                    "version": "7.0.0",
                    "purl": "pkg:npm/%40babel/code-frame@7.0.0",
                    "group": "",
                    "properties": [
                        {"name": "syft:package:id", "value": "@babel/code-frame@7.0.0"},
                        {"name": "syft:package:type", "value": "npm"},
                    ],
                },
            ],
            "dependencies": [
                {
                    "ref": "root-app",
                    "dependsOn": ["pkg:npm/%40babel/code-frame@7.0.0"],
                }
            ],
        }
        sbom_info = SBOMInfo(
            spec_name="CycloneDX",
            spec_version="1.5",
            tool_name="syft",
            tool_version="1.0.0",
        )
        deserialized_bom = Bom.from_json(sbom)
        artifacts = SyftCDXParser.parse_sbom(deserialized_bom, sbom_info, sbom)
        assert len(artifacts) == 1
        artifact = artifacts[0]
        assert artifact.package_name == "@babel/code-frame"

    def make_sbom_pyjwt(self):
        return {
            "metadata": {
                "component": {
                    "bom-ref": "root-app",
                    "type": "application",
                    "name": "sample target1",
                }
            },
            "components": [
                {
                    "bom-ref": "app1",
                    "type": "application",
                    "name": "APP1",
                    "properties": [
                        {"name": "syft:package:type", "value": "pipenv"},
                        {"name": "syft:package:class", "value": "lang-pkgs"},
                    ],
                },
                {
                    "bom-ref": "lib1",
                    "type": "library",
                    "name": "PyJWT",
                    "version": "1.5.3",
                    "purl": "pkg:pypi/PyJWT@1.5.3",
                },
            ],
            "dependencies": [
                {"ref": "root-app", "dependsOn": ["app1"]},
                {"ref": "app1", "dependsOn": ["lib1"]},
            ],
        }

    def test_it_should_lowercase_package_name_and_ecosystem_from_sbom_pyjwt(self):
        sbom = self.make_sbom_pyjwt()
        sbom_info = SBOMInfo(
            spec_name="CycloneDX",
            spec_version="1.5",
            tool_name="syft",
            tool_version="1.0.0",
        )
        deserialized_bom = Bom.from_json(sbom)
        artifacts = SyftCDXParser.parse_sbom(deserialized_bom, sbom_info, sbom)
        assert len(artifacts) == 1
        artifact = artifacts[0]
        # package name and ecosystem name are lowercased
        assert artifact.package_name == "pyjwt"
        assert artifact.ecosystem == "pypi"

    def test_it_should_contain_source_name(self):
        # Given
        sbom = {
            "metadata": {
                "component": {
                    "bom-ref": "root-app",
                    "type": "application",
                    "name": "sample target1",
                }
            },
            "components": [
                {
                    "bom-ref": "root-app",
                    "type": "application",
                    "name": "sample target1",
                    "properties": [
                        {"name": "syft:package:type", "value": "deb"},
                    ],
                },
                {
                    "bom-ref": (
                        "pkg:deb/ubuntu/libblkid1@2.34-0.1ubuntu9.6?arch=arm64&distro=ubuntu-20.04&package-id=b294debbb354b902&upstream=util-linux"
                    ),
                    "type": "library",
                    "name": "libblkid1",
                    "version": "2.34-0.1ubuntu9.6",
                    "purl": (
                        "pkg:deb/ubuntu/libblkid1@2.34-0.1ubuntu9.6?arch=arm64&distro=ubuntu-20.04&upstream=util-linux"
                    ),
                    "group": "",
                    "properties": [
                        {"name": "syft:package:type", "value": "deb"},
                        {"name": "syft:metadata:source", "value": "util-linux"},
                    ],
                },
            ],
            "dependencies": [
                {
                    "ref": "root-app",
                    "dependsOn": [
                        "pkg:deb/ubuntu/libblkid1@2.34-0.1ubuntu9.6?arch=arm64&distro=ubuntu-20.04&package-id=b294debbb354b902&upstream=util-linux"
                    ],
                }
            ],
        }
        sbom_info = SBOMInfo(
            spec_name="CycloneDX",
            spec_version="1.5",
            tool_name="syft",
            tool_version="1.0.0",
        )

        # When
        deserialized_bom = Bom.from_json(sbom)
        artifacts = SyftCDXParser.parse_sbom(deserialized_bom, sbom_info, sbom)

        # Then
        assert len(artifacts) == 1
        artifact = artifacts[0]
        assert artifact.package_name == "libblkid1"
        assert artifact.source_name == "util-linux"
        assert artifact.ecosystem == "ubuntu-20.04"

    def test_it_should_contain_upstream_without_source_name(self):
        # Given
        sbom = {
            "metadata": {
                "component": {
                    "bom-ref": "root-app",
                    "type": "application",
                    "name": "sample target1",
                }
            },
            "components": [
                {
                    "bom-ref": "root-app",
                    "type": "application",
                    "name": "sample target1",
                    "properties": [
                        {"name": "syft:package:type", "value": "apk"},
                    ],
                },
                {
                    "bom-ref": (
                        "pkg:apk/alpine/libcrypto3@3.5.0-r0?arch=aarch64&distro=alpine-3.22.0&package-id=3849f7871790bde3&upstream=openssl"
                    ),
                    "type": "library",
                    "name": "libcrypto3",
                    "version": "3.5.0-r0",
                    "purl": (
                        "pkg:apk/alpine/libcrypto3@3.5.0-r0?arch=aarch64&distro=alpine-3.22.0&upstream=openssl"
                    ),
                    "group": "",
                    "properties": [
                        {"name": "syft:package:type", "value": "apk"},
                    ],
                },
            ],
            "dependencies": [
                {
                    "ref": "root-app",
                    "dependsOn": [
                        "pkg:apk/alpine/libcrypto3@3.5.0-r0?arch=aarch64&distro=alpine-3.22.0&package-id=3849f7871790bde3&upstream=openssl"
                    ],
                }
            ],
        }
        sbom_info = SBOMInfo(
            spec_name="CycloneDX",
            spec_version="1.5",
            tool_name="syft",
            tool_version="1.0.0",
        )

        # When
        deserialized_bom = Bom.from_json(sbom)
        artifacts = SyftCDXParser.parse_sbom(deserialized_bom, sbom_info, sbom)

        # Then
        assert len(artifacts) == 1
        artifact = artifacts[0]
        assert artifact.package_name == "libcrypto3"
        assert artifact.source_name == "openssl"
        assert artifact.ecosystem == "alpine-3.22.0"

    def test_it_should_contain_sourceRpm(self):
        # Given
        sbom = {
            "metadata": {
                "component": {
                    "bom-ref": "root-app",
                    "type": "application",
                    "name": "sample target1",
                }
            },
            "components": [
                {
                    "bom-ref": "root-app",
                    "type": "application",
                    "name": "sample target1",
                    "properties": [
                        {"name": "syft:package:type", "value": "rpm"},
                    ],
                },
                {
                    "bom-ref": (
                        "pkg:rpm/rocky/audit-libs@3.0.7-104.el9?arch=x86_64&distro=rocky-9.3&package-id=80083a9ab47023ba&upstream=audit-3.0.7-104.el9.src.rpm"
                    ),
                    "type": "library",
                    "name": "audit-libs",
                    "version": "3.0.7-104.el9",
                    "purl": (
                        "pkg:rpm/rocky/audit-libs@3.0.7-104.el9?arch=x86_64&distro=rocky-9.3&upstream=audit-3.0.7-104.el9.src.rpm"
                    ),
                    "group": "",
                    "properties": [
                        {"name": "syft:package:type", "value": "rpm"},
                        {"name": "syft:metadata:sourceRpm", "value": "audit-3.0.7-104.el9.src.rpm"},
                    ],
                },
            ],
            "dependencies": [
                {
                    "ref": "root-app",
                    "dependsOn": [
                        "pkg:rpm/rocky/audit-libs@3.0.7-104.el9?arch=x86_64&distro=rocky-9.3&package-id=80083a9ab47023ba&upstream=audit-3.0.7-104.el9.src.rpm"
                    ],
                }
            ],
        }
        sbom_info = SBOMInfo(
            spec_name="CycloneDX",
            spec_version="1.5",
            tool_name="syft",
            tool_version="1.0.0",
        )

        # When
        deserialized_bom = Bom.from_json(sbom)
        artifacts = SyftCDXParser.parse_sbom(deserialized_bom, sbom_info, sbom)

        # Then
        assert len(artifacts) == 1
        artifact = artifacts[0]
        assert artifact.package_name == "audit-libs"
        assert artifact.source_name == "audit"
        assert artifact.ecosystem == "rocky-9.3"

    def test_it_should_parse_sbom_with_spec_version_1_6(self):
        sbom = self.make_sbom_pyjwt()
        sbom_info = SBOMInfo(
            spec_name="CycloneDX",
            spec_version="1.6",
            tool_name="syft",
            tool_version="1.0.0",
        )
        deserialized_bom = Bom.from_json(sbom)
        artifacts = SyftCDXParser.parse_sbom(deserialized_bom, sbom_info, sbom)
        assert len(artifacts) == 1
        artifact = artifacts[0]
        assert artifact.package_name == "pyjwt"
        assert artifact.ecosystem == "pypi"
