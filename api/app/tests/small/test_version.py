from operator import ge, gt, le, lt

import pytest
from univers.versions import GolangVersion, SemverVersion

from app.detector.package_family import PackageFamily
from app.detector.version import version_factory
from app.detector.version.ext_debian_version import ExtDebianVersion
from app.detector.version.ext_pypi_version import ExtPypiVersion
from app.detector.vulnerable_range import VulnerableRange


class TestComparableVersion:
    class _TestVersion:
        @staticmethod
        def eval_operator(left, right, operator):
            if operator == "==":
                return left >= right and left <= right
            actual_operator = {">=": ge, ">": gt, "<=": le, "<": lt}[operator]
            return actual_operator(left, right)

    class TestExtDebianVersion(_TestVersion):
        @pytest.mark.parametrize(
            "version_string, expected",
            # expected: Union[tuple[int, str, str], str] -- (epoch, upstream, revision) or exception
            [
                # might be tested in univers.
                # for details, see https://manpages.debian.org/jessie/dpkg-dev/deb-version.5.en.html
                ("", "Invalid version string"),
                ("a", "Invalid version string"),
                ("a.1", "Invalid version string"),
                ("1", (0, "1", "0")),
                ("1.2", (0, "1.2", "0")),
                (":", "Invalid version string"),
                (":2", "Invalid version string"),
                ("-1:2", "Invalid version string"),
                ("a:1.2", "Invalid version string"),
                ("1a:1.2", "Invalid version string"),
                ("1:", "Invalid version string"),
                ("1:2", (1, "2", "0")),
                ("1:2.3", (1, "2.3", "0")),
                ("0:2", (0, "2", "0")),
                ("1.2:3", "Invalid version string"),
                ("1.2-3.4", (0, "1.2", "3.4")),
                ("1.2-3-4", (0, "1.2-3", "4")),
            ],
        )
        def test_gen_instance(self, version_string, expected):
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    version_factory.gen_version_instance(PackageFamily.DEBIAN, version_string)
                return
            version_obj = version_factory.gen_version_instance(PackageFamily.DEBIAN, version_string)
            assert isinstance(version_obj, ExtDebianVersion)
            assert (version_obj.epoch, version_obj.upstream, version_obj.revision) == expected

        @pytest.mark.parametrize(
            "left, right, operator, expected",
            # left, right: version_strings to compare
            # operator: one of "==", ">=", ">", "<=", "<".
            # expected: Union[bool, str] -- expected result or exception
            [
                ("1.2", "1.2", "==", True),
                ("1.2", "1.2", "<=", True),
                ("1.2", "1.2", "<", False),
                ("1.2", "1.2", ">=", True),
                ("1.2", "1.2", ">", False),
                ("1.2", "1.2~0", ">", True),  # CAUTION!
                ("1.2", "1.2.0", "==", False),  # CAUTION!
                ("1.2", "1.2.0", "<", True),  # CAUTION!
                ("1.2", "1.2.0", "<=", True),
                ("1.2", "1.2.0", ">", False),
                ("1.2", "1.2.0", ">=", False),
                ("1.3", "1.2.3", "==", False),
                ("1.3", "1.2.3", ">=", True),
                ("1.3", "1.2.3", ">", True),
                ("1.3", "1.2.3", "<=", False),
                ("1.3", "1.2.3", "<", False),
                ("1:1.2", "1.2", "==", True),  # epoch should be ignored
                ("1:1.2", "1.2.0", "==", False),  # epoch should be ignored
                ("1:1.2", "1.2.0", "<", True),  # epoch should be ignored
                ("1:1.2", "1.2.0", "<=", True),  # epoch should be ignored
                ("1:1.2", "1.2.0", ">", False),  # epoch should be ignored
                ("1:1.2", "1.2.0", ">=", False),  # epoch should be ignored
                ("1.2", "1:1.2", "==", True),  # epoch should be ignored
                ("1.2", "1:1.2.0", "==", False),  # epoch should be ignored
                ("1.2", "1:1.2.0", "<", True),  # epoch should be ignored
                ("1.2", "1:1.2.0", "<=", True),  # epoch should be ignored
                ("1.2", "1:1.2.0", ">", False),  # epoch should be ignored
                ("1.2", "1:1.2.0", ">=", False),  # epoch should be ignored
                ("0:2.3", "2.3", "==", True),
                ("2.3", "0:2.3", "==", True),
                ("1.2-5ubuntu4.6", "1.2", "==", True),  # revision should be ignored
                ("1.2-5ubuntu4.6", "1.2", "<", False),  # revision should be ignored
                ("1.2-5ubuntu4.6", "1.2", "<=", True),  # revision should be ignored
                ("1.2-5ubuntu4.6", "1.2", ">", False),  # revision should be ignored
                ("1.2-5ubuntu4.6", "1.2", ">=", True),  # revision should be ignored
                ("1.2-5ubuntu4.6", "1.2-5ubuntu4.6", "==", True),  # revision should be ignored
                ("1.2-5ubuntu4.6", "1.2-5ubuntu4.6", "<", False),  # revision should be ignored
                ("1.2-5ubuntu4.6", "1.2-5ubuntu4.6", "<=", True),  # revision should be ignored
                ("1.2-5ubuntu4.6", "1.2-5ubuntu4.6", ">", False),  # revision should be ignored
                ("1.2-5ubuntu4.6", "1.2-5ubuntu4.6", ">=", True),  # revision should be ignored
                ("1.2-6", "1.2-5ubuntu4.6", "==", True),  # revision should be ignored
                ("1.2-6", "1.2-5ubuntu4.6", "<", False),  # revision should be ignored
                ("1.2-6", "1.2-5ubuntu4.6", "<=", True),  # revision should be ignored
                ("1.2-6", "1.2-5ubuntu4.6", ">", False),  # revision should be ignored
                ("1.2-6", "1.2-5ubuntu4.6", ">=", True),  # revision should be ignored
                ("3:1.2-6", "4:1.2-5", "==", True),  # epoch & revision should be ignored
                ("3:1.2-6", "4:1.2-5", "<", False),  # epoch & revision should be ignored
                ("3:1.2-6", "4:1.2-5", "<=", True),  # epoch & revision should be ignored
                ("3:1.2-6", "4:1.2-5", ">", False),  # epoch & revision should be ignored
                ("3:1.2-6", "4:1.2-5", ">=", True),  # epoch & revision should be ignored
                ("1.2-3-4", "1.2-3", "==", False),
                ("1.2-3-4", "1.2-3-", "==", True),
                ("1.2-3-4", "1.2-3-5", "==", True),
            ],
        )
        def test_compare(self, left, right, operator, expected):
            left_obj = version_factory.gen_version_instance(PackageFamily.DEBIAN, left)
            right_obj = version_factory.gen_version_instance(PackageFamily.DEBIAN, right)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    self.eval_operator(left_obj, right_obj, operator)
                return
            assert self.eval_operator(left_obj, right_obj, operator) == expected

        @pytest.mark.parametrize(
            "package_family, version_string, expected",
            [
                (PackageFamily.DEBIAN, "1.2.3", True),
                (PackageFamily.UNKNOWN, "1.2.3", " not supported between instances of "),
            ],
        )
        def test_compare_with_different_family(self, package_family, version_string, expected):
            debian_obj = version_factory.gen_version_instance(PackageFamily.DEBIAN, "1.2.3")
            target_obj = version_factory.gen_version_instance(package_family, version_string)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    assert debian_obj >= target_obj
                return
            assert (debian_obj >= target_obj and debian_obj <= target_obj) == expected

    class TestPypiVersion(_TestVersion):
        @pytest.mark.parametrize(
            "version_string, expected",
            # expected: Union[tuple[int, int, int, tuple], str]
            #           -- (epoch,release,pre,post,dev,local) or exception
            [
                # might be tested in packaging version.
                ("", "Invalid version: "),
                ("a", "Invalid version: "),
                ("a.1", "Invalid version: "),
                (".", "Invalid version: "),
                (".2", "Invalid version: "),
                ("-1.2", "Invalid version: "),
                ("1", (0, (1,), None, None, None, None)),
                ("1.", "Invalid version: "),  # different from semver behavior
                ("1.2", (0, (1, 2), None, None, None, None)),
                ("1.2.", "Invalid version: "),  # different from semver behavior
                ("1.2.3", (0, (1, 2, 3), None, None, None, None)),
                ("1.2.3.", "Invalid version: "),  # different from semver behavior
                ("1.2.3.4", (0, (1, 2, 3, 4), None, None, None, None)),  # CAUTION!
                ("1.2.3-4", (0, (1, 2, 3), None, 4, None, None)),
                ("1.2.3-4.5", "Invalid version: "),  # different from semver behavior
                ("1.2.3-4-5", "Invalid version: "),  # different from semver behavior
                ("1.2.3-rc4.alpha5", "Invalid version: "),
                ("1.2.3-rc4+build5", (0, (1, 2, 3), ("rc", 4), None, None, "build5")),
                ("2!1.2.3b4post6dev31+build5", (2, (1, 2, 3), ("b", 4), 6, 31, "build5")),
                ("2021.06", (0, (2021, 6), None, None, None, None)),
                ("0.5.0b3.dev31", (0, (0, 5, 0), ("b", 3), None, 31, None)),
                ("2.0.0a1", (0, (2, 0, 0), ("a", 1), None, None, None)),
                ("1!2.0.0", (1, (2, 0, 0), None, None, None, None)),
            ],
        )
        def test_gen_instance(self, version_string, expected):
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    version_factory.gen_version_instance(PackageFamily.PYPI, version_string)
                return
            pypi_obj = version_factory.gen_version_instance(PackageFamily.PYPI, version_string)
            assert isinstance(pypi_obj, ExtPypiVersion)
            assert (
                pypi_obj.epoch,
                pypi_obj.release,
                pypi_obj.pre,
                pypi_obj.post,
                pypi_obj.dev,
                pypi_obj.local,
            ) == expected

        @pytest.mark.parametrize(
            "left, right, operator, expected",
            # left, right: version_strings to compare
            # operator: one of "==", ">=", ">", "<=", "<".
            # expected: Union[bool, str] -- expected result or exception
            [
                ("1.2", "1.2", "==", True),
                ("1.2", "1.2", "<=", True),
                ("1.2", "1.2", "<", False),
                ("1.2", "1.2", ">=", True),
                ("1.2", "1.2", ">", False),
                ("1.2", "1.2.0", "==", True),  # different from debian
                ("1.2", "1.2.0", "<", False),  # different from debian
                ("1.2", "1.2.0", "<=", True),
                ("1.2", "1.2.0", ">", False),
                ("1.2", "1.2.0", ">=", True),
                ("1.3", "1.2.3", "==", False),
                ("1.3", "1.2.3", ">=", True),
                ("1.3", "1.2.3", ">", True),
                ("1.3", "1.2.3", "<=", False),
                ("1.3", "1.2.3", "<", False),
                ("1!1.2", "1.2", "==", True),  # epoch should be ignored
                ("1!1.2", "1.2.0", "==", True),  # epoch should be ignored, different from debian
                ("1!1.2", "1.2.0", "<", False),  # epoch should be ignored, different from debian
                ("1!1.2", "1.2.0", "<=", True),  # epoch should be ignored
                ("1!1.2", "1.2.0", ">", False),  # epoch should be ignored
                ("1!1.2", "1.2.0", ">=", True),  # epoch should be ignored
                ("1.2", "1!1.2", "==", True),  # epoch should be ignored
                ("1.2", "1!1.2.0", "==", True),  # epoch should be ignored
                ("1.2", "1!1.2.0", "<", False),  # epoch should be ignored
                ("1.2", "1!1.2.0", "<=", True),  # epoch should be ignored
                ("1.2", "1!1.2.0", ">", False),  # epoch should be ignored
                ("1.2", "1!1.2.0", ">=", True),  # epoch should be ignored
                ("0!2.3", "2.3", "==", True),
                ("2.3", "0!2.3", "==", True),
                ("1.2+abc", "1.2", "==", True),  # local should be ignored
                ("1.2+abc", "1.2", "<", False),  # local should be ignored
                ("1.2+abc", "1.2", "<=", True),  # local should be ignored
                ("1.2+abc", "1.2", ">", False),  # local should be ignored
                ("1.2+abc", "1.2", ">=", True),  # local should be ignored
                ("1.2+abc", "1.2+xyz", "==", True),  # local should be ignored
                ("1.2+abc", "1.2+xyz", "<", False),  # local should be ignored
                ("1.2+abc", "1.2+xyz", "<=", True),  # local should be ignored
                ("1.2+abc", "1.2+xyz", ">", False),  # local should be ignored
                ("1.2+abc", "1.2+xyz", ">=", True),  # local should be ignored
                ("3!1.2+abc", "4!1.2+xyz", "==", True),  # epoch & local should be ignored
                ("3!1.2+abc", "4!1.2+xyz", "<", False),  # epoch & local should be ignored
                ("3!1.2+abc", "4!1.2+xyz", "<=", True),  # epoch & local should be ignored
                ("3!1.2+abc", "4!1.2+xyz", ">", False),  # epoch & local should be ignored
                ("3!1.2+abc", "4!1.2+xyz", ">=", True),  # epoch & local should be ignored
            ],
        )
        def test_compare(self, left, right, operator, expected):
            left_obj = version_factory.gen_version_instance(PackageFamily.PYPI, left)
            right_obj = version_factory.gen_version_instance(PackageFamily.PYPI, right)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    self.eval_operator(left_obj, right_obj, operator)
                return
            assert self.eval_operator(left_obj, right_obj, operator) == expected

    class TestSemverVersion(_TestVersion):
        @pytest.mark.parametrize(
            "version_string, expected",
            # expected: Union[tuple[int, int, int, tuple], str]
            #           -- (major, minor, patch, prerelease) or exception
            [
                # might be tested in univers.
                # for details, see https://semver.org/#semantic-versioning-specification-semver
                ("", "Invalid version string"),
                ("a", "Invalid version string"),
                ("a.1", "Invalid version string"),
                (".", "Invalid version string"),
                (".2", "Invalid version string"),
                ("-1.2", "Invalid version string"),
                ("1", (1, 0, 0, ())),
                ("1.", (1, 0, 0, ())),
                ("1.2", (1, 2, 0, ())),
                ("1.2.", (1, 2, 0, ())),
                ("1.2.3", (1, 2, 3, ())),
                ("1.2.3.", (1, 2, 3, ())),
                ("1.2.3.4", (1, 2, 3, ())),  # CAUTION!
                ("1.2.3-4", (1, 2, 3, ("4",))),
                ("1.2.3-4.5", (1, 2, 3, ("4", "5"))),
                ("1.2.3-4-5", (1, 2, 3, ("4-5",))),
                ("1.2.3-rc4.alpha5", (1, 2, 3, ("rc4", "alpha5"))),
                ("1.2.3-rc4+build5", (1, 2, 3, ("rc4",))),  # build5 is in sem_obj.build
            ],
        )
        def test_gen_instance(self, version_string, expected):
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    version_factory.gen_version_instance(PackageFamily.UNKNOWN, version_string)
                return
            sem_obj = version_factory.gen_version_instance(PackageFamily.UNKNOWN, version_string)
            assert isinstance(sem_obj, SemverVersion)
            assert (sem_obj.major, sem_obj.minor, sem_obj.patch, sem_obj.prerelease) == expected

        @pytest.mark.parametrize(
            "left, right, operator, expected",
            # left, right: version_strings to compare
            # operator: one of "==", ">=", ">", "<=", "<".
            # expected: Union[bool, str] -- expected result or exception
            [
                ("2", "2.0.0", "==", True),
                ("1.2", "1.2.0", "==", True),
                ("1.3", "1.2.3", "==", False),
                ("1.3", "1.2.3", ">=", True),
                ("1.3", "1.2.3", ">", True),
                ("1.3", "1.2.3", "<=", False),
                ("1.3", "1.2.3", "<", False),
                ("1.2.3.4", "1.2.3.5", "==", True),  # CAUTION!
                ("1.2.3.4", "1.2.3.5", "<", False),  # CAUTION!
                ("1.2.3-rc1", "1.2.3", "==", False),
                ("1.2.3-rc1", "1.2.3", "<", True),
                ("1.2.3-rc1", "1.2.3-rc1", "==", True),
                ("1.2.3-rc1", "1.2.3-rc2", ">", False),
                ("1.2.3-rc1", "1.2.3-rc2", "<", True),
                ("1.2.3-rc1+build1", "1.2.3-rc1", "==", True),
                ("1.2.3-rc1+build1", "1.2.3-rc1", ">=", True),
                ("1.2.3-rc1+build1", "1.2.3-rc1", ">", False),
                ("1.2.3-rc1+build1", "1.2.3-rc1", "<=", True),
                ("1.2.3-rc1+build1", "1.2.3-rc1", "<", False),
                ("1.2.3-rc1+build1", "1.2.3-rc1+build2", "==", True),
            ],
        )
        def test_compare(self, left, right, operator, expected):
            left_obj = version_factory.gen_version_instance(PackageFamily.UNKNOWN, left)
            right_obj = version_factory.gen_version_instance(PackageFamily.UNKNOWN, right)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    self.eval_operator(left_obj, right_obj, operator)
                return
            assert self.eval_operator(left_obj, right_obj, operator) == expected

        @pytest.mark.parametrize(
            "package_family, version_string, expected",
            [
                (PackageFamily.DEBIAN, "1.2.3", " not supported between instances of "),
                (PackageFamily.UNKNOWN, "1.2.3", True),
            ],
        )
        def test_compare_with_different_family(self, package_family, version_string, expected):
            semver_obj = version_factory.gen_version_instance(PackageFamily.UNKNOWN, "1.2.3")
            target_obj = version_factory.gen_version_instance(package_family, version_string)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    assert semver_obj >= target_obj
                return
            assert (semver_obj >= target_obj and semver_obj <= target_obj) == expected

    class TestNpmVersion(_TestVersion):
        @pytest.mark.parametrize(
            "version_string, expected",
            # expected: Union[tuple[int, int, int, tuple], str]
            #           -- (major, minor, patch, prerelease) or exception
            [
                # other cases are tested in TestSemverVersion
                ("1.2.3", (1, 2, 3, ())),
                ("1.2.x", (1, 2, 0, ())),
                ("99.999.99999", (99, 999, 99999, ())),
                ("2.1.0-M1", (2, 1, 0, ("M1",))),
            ],
        )
        def test_gen_instance(self, version_string, expected):
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    version_factory.gen_version_instance(PackageFamily.NPM, version_string)
                return
            sem_obj = version_factory.gen_version_instance(PackageFamily.NPM, version_string)
            assert isinstance(sem_obj, SemverVersion)
            assert (sem_obj.major, sem_obj.minor, sem_obj.patch, sem_obj.prerelease) == expected

    class TestGoVersion(_TestVersion):
        @pytest.mark.parametrize(
            "version_string, expected",
            [
                ("1.2.3", (1, 2, 3, ())),
                ("0.0.0-20180523222229-09b5706aa936", (0, 0, 0, ("20180523222229-09b5706aa936",))),
                (
                    "0.15.0-rc.1",
                    (
                        0,
                        15,
                        0,
                        (
                            "rc",
                            "1",
                        ),
                    ),
                ),
                (
                    "0.5.0-alpha.5.0.20190108173120-83c051b701d3",
                    (
                        0,
                        5,
                        0,
                        (
                            "alpha",
                            "5",
                            "0",
                            "20190108173120-83c051b701d3",
                        ),
                    ),
                ),
                ("0.15.4-beta", (0, 15, 4, ("beta",))),
                ("0.0.1-alpha-1", (0, 0, 1, ("alpha-1",))),
                ("2.0.0-dev", (2, 0, 0, ("dev",))),
                ("1.12.1-stable", (1, 12, 1, ("stable",))),
                ("4.0.0-preview1", (4, 0, 0, ("preview1",))),
            ],
        )
        def test_gen_instance(self, version_string, expected):
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    version_factory.gen_version_instance(PackageFamily.GO, version_string)
                return
            sem_obj = version_factory.gen_version_instance(PackageFamily.GO, version_string)
            assert isinstance(sem_obj, GolangVersion)
            assert (sem_obj.major, sem_obj.minor, sem_obj.patch, sem_obj.prerelease) == expected


class TestVulnerableRange:
    @pytest.fixture(scope="function", name="gen_preset_versions")
    def gen_preset_versions(self):
        self.semver_version1 = version_factory.gen_version_instance(PackageFamily.UNKNOWN, "1.0")
        self.debian_version1 = version_factory.gen_version_instance(PackageFamily.DEBIAN, "1.0")
        self.pypi_version1 = version_factory.gen_version_instance(PackageFamily.PYPI, "1.0")

    @pytest.mark.parametrize(
        "attrs",
        [
            ([]),
            (["eq", "ge"]),
            (["eq", "gt"]),
            (["eq", "le"]),
            (["eq", "lt"]),
            (["ge", "gt"]),
            (["le", "lt"]),
        ],
    )
    def test_ambiguous(self, gen_preset_versions, attrs):
        kwargs = {attr: self.semver_version1 for attr in attrs}
        with pytest.raises(ValueError, match=r"Ambiguous "):
            VulnerableRange(**kwargs)

    def test_ambiguous_with_different_classes(self, gen_preset_versions):
        assert VulnerableRange(ge=self.debian_version1, lt=self.debian_version1)
        with pytest.raises(ValueError, match=r"Ambiguous "):
            VulnerableRange(ge=self.semver_version1, lt=self.debian_version1)
        with pytest.raises(ValueError, match=r"Ambiguous "):
            VulnerableRange(ge=self.pypi_version1, lt=self.debian_version1)

    class TestExtDebianVersion:
        @pytest.mark.parametrize(
            "references, vulnerable, expected",
            [
                (["9.50~dfsg-5ubuntu4.6"], "=9.50~dfsg-5ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], "=9.50~dfsg-6ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], "<=9.50~dfsg-5ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], "<=9.50~dfsg-4ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], "<9.50~dfsg-6ubuntu4.6", False),
                (["9.50~dfsg-5ubuntu4.6"], "<9.50~dfsg-5ubuntu4.6", False),
                (["9.50~dfsg-5ubuntu4.6"], ">=9.50~dfsg-5ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], ">=9.50~dfsg-6ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], ">9.50~dfsg-4ubuntu4.6", False),
                (["9.50~dfsg-5ubuntu4.6"], ">9.50~dfsg-5ubuntu4.6", False),
                (["0:9.50~dfsg-5ubuntu4.6"], "=9.50~dfsg-5ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], "=1:9.50~dfsg-5ubuntu4.6", True),
                (["1:9.50~dfsg-5ubuntu4.6"], "=9.50~dfsg-5ubuntu4.6", True),
                (["1:9.50~dfsg-5ubuntu4.6"], "=2:9.50~dfsg-5ubuntu4.6", True),
                (["1:9.50~dfsg-5ubuntu4.6"], "=1:9.50~dfsg-5ubuntu4.6", True),
                (["2.3.4"], ">=2.0.0 <2.3.4", False),
                (["2.3.4"], ">=2.0.0 <2.3.5", True),
                (["2.3.4"], ">=2.0.0 <=2.3.3", False),
                (["2.3.4"], ">=2.0.0 <=2.3.4", True),
                (["2.3.4"], ">=2.0.0 <2.3.4~dfsg", False),  # CAUTION!
                (["2.3.4~dsfg"], ">=2.0.0 <2.3.4", True),  # CAUTION!
                (["2.3.4~dsfg5-ubuntu4.6"], ">=2.0.0 <2.3.4~sdfg5", True),  # CAUTION!
            ],
        )
        def test_detect_matched(self, references, vulnerable, expected):
            reference_objs = [
                version_factory.gen_version_instance(PackageFamily.DEBIAN, ref)
                for ref in references
            ]
            vulnerable_range = VulnerableRange.from_string(PackageFamily.DEBIAN, vulnerable)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    vulnerable_range.detect_matched(reference_objs)
                return
            assert vulnerable_range.detect_matched(reference_objs) == expected

        @pytest.mark.parametrize(
            "package_family, version_string, expected",
            [
                (PackageFamily.DEBIAN, "1.2.3", True),
                (PackageFamily.PYPI, "1.2.3", "'==' not supported between instances of "),
                (PackageFamily.UNKNOWN, "1.2.3", "'==' not supported between instances of "),
            ],
        )
        def test_with_different_family(self, package_family, version_string, expected):
            vulnerable = VulnerableRange.from_string(PackageFamily.DEBIAN, "=1.2.3")
            target_obj = version_factory.gen_version_instance(package_family, version_string)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    assert vulnerable.detect_matched([target_obj])
                return
            assert vulnerable.detect_matched([target_obj]) == expected

    class TestPypiVersion:
        @pytest.mark.parametrize(
            "references, vulnerable, expected",
            [
                (["9.50+build1"], "=9.50+build1", True),
                (["9.50+build1"], "=9.50+build1", True),
                (["9.50+build1"], "<=9.50+build1", True),
                (["9.50+build1"], "<=9.50+build1", True),
                (["9.50+build1"], "<9.50+build1", False),
                (["9.50+build1"], "<9.50+build1", False),
                (["9.50+build1"], ">=9.50+build1", True),
                (["9.50+build1"], ">=9.50+build1", True),
                (["9.50+build1"], ">9.50+build1", False),
                (["9.50+build1"], ">9.50+build1", False),
                (["0!9.50+build1"], "=9.50+5build1", True),
                (["9.50+5build1"], "=1!9.50+5build1", True),
                (["1!9.50+5build1"], "=9.50+5build1", True),
                (["1!9.50+5build1"], "=2!9.50+5build1", True),
                (["1!9.50+5build1"], "=1!9.50+5build1", True),
                (["2.3.4"], ">=2.0.0 <2.3.4", False),
                (["2.3.4"], ">=2.0.0 <2.3.5", True),
                (["2.3.4"], ">=2.0.0 <=2.3.3", False),
                (["2.3.4"], ">=2.0.0 <=2.3.4", True),
                (["2.3.4"], ">=2.0.0 <2.3.4post1", True),  # CAUTION!
                (["2.3.4"], ">=2.0.0 <2.3.4dev1", False),  # CAUTION!
                (["2.3.4"], ">=2.0.0 <2.3.4pre1", False),  # CAUTION!
                (["2.3.4post1"], ">=2.0.0 <2.3.4", False),  # CAUTION!
                (["2.3.4pre1"], ">=2.0.0 <2.3.4", True),  # CAUTION!
                (["2.3.4dev1+build1"], ">=2.0.0 <2.3.4dev1", False),
            ],
        )
        def test_detect_matched(self, references, vulnerable, expected):
            reference_objs = [
                version_factory.gen_version_instance(PackageFamily.PYPI, ref) for ref in references
            ]
            vulnerable_range = VulnerableRange.from_string(PackageFamily.PYPI, vulnerable)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    vulnerable_range.detect_matched(reference_objs)
                return
            assert vulnerable_range.detect_matched(reference_objs) == expected

        @pytest.mark.parametrize(
            "package_family, version_string, expected",
            [
                (PackageFamily.DEBIAN, "1.2.3", "'==' not supported between instances of "),
                (PackageFamily.PYPI, "1.2.3", True),
                (PackageFamily.UNKNOWN, "1.2.3", "'==' not supported between instances of "),
            ],
        )
        def test_with_different_family(self, package_family, version_string, expected):
            vulnerable = VulnerableRange.from_string(PackageFamily.PYPI, "=1.2.3")
            target_obj = version_factory.gen_version_instance(package_family, version_string)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    assert vulnerable.detect_matched([target_obj])
                return
            assert vulnerable.detect_matched([target_obj]) == expected

    class TestSemverVersion:
        @pytest.mark.parametrize(
            "references, vulnerable, expected",
            [
                (["2.3.4"], "=2.3.4", True),
                (["2.3.4"], "=2.3.5", False),
                (["2.3.4"], "<=2.3.4", True),
                (["2.3.4"], "<=2.3.3", False),
                (["2.3.4"], "<2.3.5", True),
                (["2.3.4"], "<2.3.4", False),
                (["2.3.4"], ">=2.3.4", True),
                (["2.3.4"], ">=2.3.5", False),
                (["2.3.4"], ">2.3.3", True),
                (["2.3.4"], ">2.3.4", False),
                (["2.3.4.5"], "=2.3.4.6", True),  # CAUTION!
                (["2.3.4"], ">2.3.4-rc0", True),
                (["2.3.4-rc1"], ">2.3.4-rc0", True),
                (["2.3.4+build1"], "=2.3.4", True),
                (["2.3.4+build1"], "=2.3.4+build2", True),
            ],
        )
        def test_detect_matched(self, references, vulnerable, expected):
            reference_objs = [
                version_factory.gen_version_instance(PackageFamily.UNKNOWN, ref)
                for ref in references
            ]
            vulnerable_range = VulnerableRange.from_string(PackageFamily.UNKNOWN, vulnerable)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    vulnerable_range.detect_matched(reference_objs)
                return
            assert vulnerable_range.detect_matched(reference_objs) == expected

        @pytest.mark.parametrize(
            "package_family, version_string, expected",
            [
                (PackageFamily.DEBIAN, "1.2.3", "'==' not supported between instances of "),
                (PackageFamily.PYPI, "1.2.3", "'==' not supported between instances of "),
                (PackageFamily.UNKNOWN, "1.2.3", True),
            ],
        )
        def test_with_different_family(self, package_family, version_string, expected):
            vulnerable = VulnerableRange.from_string(PackageFamily.UNKNOWN, "=1.2.3")
            target_obj = version_factory.gen_version_instance(package_family, version_string)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    assert vulnerable.detect_matched([target_obj])
                return
            assert vulnerable.detect_matched([target_obj]) == expected
