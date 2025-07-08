from app.sbom.parser.sbom_info import SBOMInfo
from app.sbom.parser.trivy_cdx_parser import TrivyCDXParser


class TestTrivyCDXParser:
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
                    "name": "PyJWT",  # uppercase
                    "properties": [
                        {"name": "aquasecurity:trivy:Type", "value": "pypi"},
                        {"name": "aquasecurity:trivy:Class", "value": "lang-pkgs"},
                    ],
                },
                {
                    "bom-ref": "lib1",
                    "type": "library",
                    "name": "PyJWT",
                    "version": "1.5.3",
                    "purl": "pkg:pypi/pyjwt@1.5.3",  # lowercase
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
        # target name is also correctly included
        targets = {t[0] for t in artifact.targets}
        assert "PyJWT" in targets
        assert "sample target1" in targets
