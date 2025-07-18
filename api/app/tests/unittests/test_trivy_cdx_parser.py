from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.trivy_cdx_parser import TrivyCDXParser


class TestTrivyCDXParser:
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
                        {"name": "aquasecurity:trivy:Type", "value": "npm"},
                        {"name": "aquasecurity:trivy:Class", "value": "lang-pkgs"},
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
                        {"name": "aquasecurity:trivy:PkgID", "value": "@babel/code-frame@7.0.0"},
                        {"name": "aquasecurity:trivy:Type", "value": "npm"},
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
            tool_name="trivy",
            tool_version="0.52.0",
        )
        parser = TrivyCDXParser()
        artifacts = parser.parse_sbom(sbom, sbom_info)
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
                        {"name": "aquasecurity:trivy:Type", "value": "pipenv"},
                        {"name": "aquasecurity:trivy:Class", "value": "lang-pkgs"},
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
            tool_name="trivy",
            tool_version="0.52.0",
        )
        parser = TrivyCDXParser()
        artifacts = parser.parse_sbom(sbom, sbom_info)
        assert len(artifacts) == 1
        artifact = artifacts[0]
        # package name and ecosystem name are lowercased
        assert artifact.package_name == "pyjwt"
        assert artifact.ecosystem == "pypi"

    def test_it_should_create_target_without_metadata(self):
        sbom = {
            "$schema": "http://cyclonedx.org/schema/bom-1.5.schema.json",
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": "urn:uuid:5bf250f0-d1be-4c1a-96dc-5f6e62c28cb2",
            "version": 1,
            "metadata": {
                "timestamp": "2024-07-01T00:00:00+09:00",
                "tools": [{"vendor": "aquasecurity", "name": "trivy", "version": "0.52.0"}],
                "component": {
                    "bom-ref": "73c936da-ca45-4ffd-a64b-2a78409d6b07",
                    "type": "application",
                    "name": "sample target1",
                    "properties": [{"name": "aquasecurity:trivy:SchemaVersion", "value": "2"}],
                },
            },
            "components": [
                {
                    "name": "ubuntu",
                    "type": "operating-system",
                    "properties": [
                        {"name": "aquasecurity:trivy:Type", "value": "ubuntu"},
                        {"name": "aquasecurity:trivy:Class", "value": "os-pkgs"},
                    ],
                    "bom-ref": "aa04ac83-6d82-4ccc-9fb9-2dfe8545ca41",
                },
                {
                    "bom-ref": "pkg:deb/ubuntu/libcrypt1@1:4.4.10-10ubuntu4?distro=ubuntu-20.04",
                    "purl": "pkg:deb/ubuntu/libcrypt1@1:4.4.10-10ubuntu4?distro=ubuntu-20.04",
                    "name": "libcrypt1",
                    "version": "1:4.4.10-10ubuntu4",
                    "type": "library",
                    "properties": [{"name": "aquasecurity:trivy:SrcName", "value": "libxcrypt"}],
                },
            ],
            "dependencies": [
                {
                    "ref": "aa04ac83-6d82-4ccc-9fb9-2dfe8545ca41",
                    "dependsOn": [
                        "pkg:deb/ubuntu/libcrypt1@1:4.4.10-10ubuntu4?distro=ubuntu-20.04"
                    ],
                },
                {
                    "ref": "73c936da-ca45-4ffd-a64b-2a78409d6b07",
                    "dependsOn": ["aa04ac83-6d82-4ccc-9fb9-2dfe8545ca41"],
                },
            ],
        }
        sbom_info = SBOMInfo(
            spec_name="CycloneDX",
            spec_version="1.5",
            tool_name="trivy",
            tool_version="0.52.0",
        )
        parser = TrivyCDXParser()
        artifacts = parser.parse_sbom(sbom, sbom_info)
        assert len(artifacts) == 1
        artifact = artifacts[0]
        assert artifact.package_name == "libcrypt1"
        assert artifact.package_manager == ""
        assert len(artifact.targets) == 1
        assert list(artifact.targets)[0] == ("ubuntu", "1:4.4.10-10ubuntu4")
