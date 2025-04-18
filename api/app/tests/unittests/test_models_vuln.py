from app import models


class TestModels:
    class TestVuln:
        def test_equals_fingerprints_when_affect_order_is_different(self):
            # When
            vuln1 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="npm"),
                        affected_versions=["1.0.0", "1.1.0"],
                        fixed_versions=["2.0.0"],
                    ),
                    models.Affect(
                        package=models.Package(name="test-package-2", ecosystem="npm"),
                        affected_versions=["1.0.0", "1.1.0"],
                        fixed_versions=["2.0.0"],
                    ),
                ],
            )
            vuln2 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-2", ecosystem="npm"),
                        affected_versions=["1.0.0", "1.1.0"],
                        fixed_versions=["2.0.0"],
                    ),
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="npm"),
                        affected_versions=["1.0.0", "1.1.0"],
                        fixed_versions=["2.0.0"],
                    ),
                ],
            )
            # Then
            assert vuln1.content_fingerprint == vuln2.content_fingerprint

        def test_equals_fingerprints_when_affected_versions_order_is_different(self):
            # When
            vuln1 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="npm"),
                        affected_versions=["1.0.0", "1.1.0"],
                        fixed_versions=["2.0.0"],
                    ),
                ],
            )
            vuln2 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="npm"),
                        affected_versions=["1.1.0", "1.0.0"],
                        fixed_versions=["2.0.0"],
                    ),
                ],
            )
            # Then
            assert vuln1.content_fingerprint == vuln2.content_fingerprint

        def test_equals_fingerprints_when_fixed_versions_order_is_different(self):
            # When
            vuln1 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="npm"),
                        affected_versions=["1.0.0"],
                        fixed_versions=["2.0.0", "2.1.0"],
                    ),
                ],
            )
            vuln2 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="npm"),
                        affected_versions=["1.0.0"],
                        fixed_versions=["2.1.0", "2.0.0"],
                    ),
                ],
            )
            # Then
            assert vuln1.content_fingerprint == vuln2.content_fingerprint

        def test_not_equals_fingerprints_when_title_is_different(self):
            # When
            vuln1 = models.Vuln(
                title="Test Vulnerability A",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[],
            )
            vuln2 = models.Vuln(
                title="Test Vulnerability B",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[],
            )
            # Then
            assert vuln1.content_fingerprint != vuln2.content_fingerprint

        def test_not_equals_fingerprints_when_detail_is_different(self):
            # When
            vuln1 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability A.",
                cvss_v3_score=7.5,
                affects=[],
            )
            vuln2 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability B.",
                cvss_v3_score=7.5,
                affects=[],
            )
            # Then
            assert vuln1.content_fingerprint != vuln2.content_fingerprint

        def test_not_equals_fingerprints_when_cvss_is_different(self):
            # When
            vuln1 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[],
            )
            vuln2 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=10,
                affects=[],
            )
            # Then
            assert vuln1.content_fingerprint != vuln2.content_fingerprint

        def test_not_equals_fingerprints_when_package_name_is_different(self):
            # When
            vuln1 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="npm"),
                        affected_versions=["1.0.0"],
                        fixed_versions=["2.0.0"],
                    ),
                ],
            )
            vuln2 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-2", ecosystem="npm"),
                        affected_versions=["1.0.0"],
                        fixed_versions=["2.0.0"],
                    ),
                ],
            )
            # Then
            assert vuln1.content_fingerprint != vuln2.content_fingerprint

        def test_not_equals_fingerprints_when_ecosystem_is_different(self):
            # When
            vuln1 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="npm"),
                        affected_versions=["1.0.0"],
                        fixed_versions=["2.0.0"],
                    ),
                ],
            )
            vuln2 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="pypi"),
                        affected_versions=["1.0.0"],
                        fixed_versions=["2.0.0"],
                    ),
                ],
            )
            # Then
            assert vuln1.content_fingerprint != vuln2.content_fingerprint

        def test_not_equals_fingerprints_when_affected_versions_is_different(self):
            # When
            vuln1 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="npm"),
                        affected_versions=["1.0.0"],
                        fixed_versions=["2.0.0"],
                    ),
                ],
            )
            vuln2 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="npm"),
                        affected_versions=["1.2.0"],
                        fixed_versions=["2.0.0"],
                    ),
                ],
            )
            # Then
            assert vuln1.content_fingerprint != vuln2.content_fingerprint

        def test_not_equals_fingerprints_when_fixed_versions_is_different(self):
            # When
            vuln1 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="npm"),
                        affected_versions=["1.0.0"],
                        fixed_versions=["2.0.0"],
                    ),
                ],
            )
            vuln2 = models.Vuln(
                title="Test Vulnerability",
                detail="This is a test vulnerability.",
                cvss_v3_score=7.5,
                affects=[
                    models.Affect(
                        package=models.Package(name="test-package-1", ecosystem="npm"),
                        affected_versions=["1.0.0"],
                        fixed_versions=["2.2.0"],
                    ),
                ],
            )
            # Then
            assert vuln1.content_fingerprint != vuln2.content_fingerprint
