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
        artifacts = TrivyCDXParser.parse_sbom(sbom, sbom_info)
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
                    "name": "pyjwt",
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
        artifacts = TrivyCDXParser.parse_sbom(sbom, sbom_info)
        assert len(artifacts) == 1
        artifact = artifacts[0]
        # package name and ecosystem name are lowercased
        assert artifact.package_name == "pyjwt"
        assert artifact.ecosystem == "pypi"
