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
        artifacts = SyftCDXParser.parse_sbom(sbom, sbom_info)
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
        artifacts = SyftCDXParser.parse_sbom(sbom, sbom_info)
        assert len(artifacts) == 1
        artifact = artifacts[0]
        # package name and ecosystem name are lowercased
        assert artifact.package_name == "pyjwt"
        assert artifact.ecosystem == "pypi"

    def test_it_should_parse_sbom_with_spec_version_1_6(self):
        sbom = self.make_sbom_pyjwt()
        sbom_info = SBOMInfo(
            spec_name="CycloneDX",
            spec_version="1.6",
            tool_name="syft",
            tool_version="1.0.0",
        )
        artifacts = SyftCDXParser.parse_sbom(sbom, sbom_info)
        assert len(artifacts) == 1
        artifact = artifacts[0]
        assert artifact.package_name == "pyjwt"
        assert artifact.ecosystem == "pypi"
