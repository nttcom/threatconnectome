from operator import ge, gt, le, lt

import pytest
from fastapi import HTTPException, status

from app.common import (
    ExtDebianVersion,
    InvalidVersion,  # from univers
    PackageFamily,
    SemverVersion,  # from univers
    VulnerableRange,
    check_topic_action_tags_integrity,
    gen_version_instance,
)


class TestCheckTopicActionTagsIntegrity:
    @property
    def test_func(self):
        return check_topic_action_tags_integrity

    def test_return_true_on_empty_action_tags(self) -> None:
        assert self.test_func([], None)
        assert self.test_func([], [])
        assert self.test_func(["alpha"], [])

    def test_return_true_on_exact_match_tags(self) -> None:
        assert self.test_func(["alpha:bravo:"], ["alpha:bravo:"])  # parent
        assert self.test_func(["alpha:bravo:charlie"], ["alpha:bravo:charlie"])  # child
        assert self.test_func(["alpha"], ["alpha"])  # neither

    def test_return_true_on_match_with_parent(self) -> None:
        assert self.test_func(["alpha:bravo:"], ["alpha:bravo:charlie"])

    def test_return_false_on_mismatch_tags(self) -> None:
        assert not self.test_func(["alpha"], ["bravo"])
        assert not self.test_func(["alpha:bravo:charlie"], ["alpha:bravo:delta"])
        assert not self.test_func(["alpha:bravo:charlie"], ["alpha:bravo:"])

    def test_raise_httpexception_on_error_if_specified(self) -> None:
        with pytest.raises(HTTPException) as error:
            self.test_func([], ["bravo"], on_error=status.HTTP_400_BAD_REQUEST)
        assert error.value.status_code == status.HTTP_400_BAD_REQUEST
        assert error.value.detail == "Action Tag mismatch with Topic Tag"


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
            # expected: Union[Tuple[int, str, str], str] -- (epoch, upstream, revision) or exception
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
                with pytest.raises(InvalidVersion, match=expected):
                    gen_version_instance(PackageFamily.DEBIAN, version_string)
                return
            version_obj = gen_version_instance(PackageFamily.DEBIAN, version_string)
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
                ("1:1.2", "1.2.0", "==", "Cannot compare with different epochs"),
                ("1:1.2", "1.2.0", "<", "Cannot compare with different epochs"),
                ("1:1.2", "1.2.0", "<=", "Cannot compare with different epochs"),
                ("1:1.2", "1.2.0", ">", "Cannot compare with different epochs"),
                ("1:1.2", "1.2.0", ">=", "Cannot compare with different epochs"),
                ("1.2", "1:1.2.0", "==", "Cannot compare with different epochs"),
                ("1.2", "1:1.2.0", "<", "Cannot compare with different epochs"),
                ("1.2", "1:1.2.0", "<=", "Cannot compare with different epochs"),
                ("1.2", "1:1.2.0", ">", "Cannot compare with different epochs"),
                ("1.2", "1:1.2.0", ">=", "Cannot compare with different epochs"),
                ("0:2.3", "2.3", "==", True),
                ("2.3", "0:2.3", "==", True),
            ],
        )
        def test_compare(self, left, right, operator, expected):
            left_obj = gen_version_instance(PackageFamily.DEBIAN, left)
            right_obj = gen_version_instance(PackageFamily.DEBIAN, right)
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
            debian_obj = gen_version_instance(PackageFamily.DEBIAN, "1.2.3")
            target_obj = gen_version_instance(package_family, version_string)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    assert debian_obj >= target_obj
                return
            assert (debian_obj >= target_obj and debian_obj <= target_obj) == expected

    class TestSemverVersion(_TestVersion):
        @pytest.mark.parametrize(
            "version_string, expected",
            # expected: Union[Tuple[int, int, int, tuple], str]
            #           -- (major, minor, patch, prerelease) or exception
            [
                # might be tested in univers.
                # for details, see https://semver.org/#semantic-versioning-specification-semver
                ("", " is not a valid "),
                ("a", " is not a valid "),
                ("a.1", " is not a valid "),
                (".", " is not a valid "),
                (".2", " is not a valid "),
                ("-1.2", " is not a valid "),
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
                with pytest.raises(InvalidVersion, match=expected):
                    gen_version_instance(PackageFamily.UNKNOWN, version_string)
                return
            sem_obj = gen_version_instance(PackageFamily.UNKNOWN, version_string)
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
            left_obj = gen_version_instance(PackageFamily.UNKNOWN, left)
            right_obj = gen_version_instance(PackageFamily.UNKNOWN, right)
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
            semver_obj = gen_version_instance(PackageFamily.UNKNOWN, "1.2.3")
            target_obj = gen_version_instance(package_family, version_string)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    assert semver_obj >= target_obj
                return
            assert (semver_obj >= target_obj and semver_obj <= target_obj) == expected


class TestVulnerableRange:
    @pytest.fixture(scope="function", name="gen_preset_versions")
    def gen_preset_versions(self):
        self.semver_version1 = gen_version_instance(PackageFamily.UNKNOWN, "1.0")
        self.debian_version1 = gen_version_instance(PackageFamily.DEBIAN, "1.0")

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

    class TestExtDebianVersion:
        @pytest.mark.parametrize(
            "references, vulnerable, expected",
            [
                (["9.50~dfsg-5ubuntu4.6"], "=9.50~dfsg-5ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], "=9.50~dfsg-6ubuntu4.6", False),
                (["9.50~dfsg-5ubuntu4.6"], "<=9.50~dfsg-5ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], "<=9.50~dfsg-4ubuntu4.6", False),
                (["9.50~dfsg-5ubuntu4.6"], "<9.50~dfsg-6ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], "<9.50~dfsg-5ubuntu4.6", False),
                (["9.50~dfsg-5ubuntu4.6"], ">=9.50~dfsg-5ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], ">=9.50~dfsg-6ubuntu4.6", False),
                (["9.50~dfsg-5ubuntu4.6"], ">9.50~dfsg-4ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], ">9.50~dfsg-5ubuntu4.6", False),
                (["0:9.50~dfsg-5ubuntu4.6"], "=9.50~dfsg-5ubuntu4.6", True),
                (["9.50~dfsg-5ubuntu4.6"], "=0:9.50~dfsg-5ubuntu4.6", True),
                (["0:9.50~dfsg-5ubuntu4.6"], "=0:9.50~dfsg-5ubuntu4.6", True),
                (
                    ["1:9.50~dfsg-5ubuntu4.6"],
                    "=9.50~dfsg-5ubuntu4.6",
                    "Cannot compare with different epochs",
                ),
                (
                    ["1:9.50~dfsg-5ubuntu4.6"],
                    "=2:9.50~dfsg-5ubuntu4.6",
                    "Cannot compare with different epochs",
                ),
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
            reference_objs = [gen_version_instance(PackageFamily.DEBIAN, ref) for ref in references]
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
                (PackageFamily.UNKNOWN, "1.2.3", "'==' not supported between instances of "),
            ],
        )
        def test_with_different_family(self, package_family, version_string, expected):
            vulnerable = VulnerableRange.from_string(PackageFamily.DEBIAN, "=1.2.3")
            target_obj = gen_version_instance(package_family, version_string)
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
                gen_version_instance(PackageFamily.UNKNOWN, ref) for ref in references
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
                (PackageFamily.UNKNOWN, "1.2.3", True),
            ],
        )
        def test_with_different_family(self, package_family, version_string, expected):
            vulnerable = VulnerableRange.from_string(PackageFamily.UNKNOWN, "=1.2.3")
            target_obj = gen_version_instance(package_family, version_string)
            if isinstance(expected, str):
                with pytest.raises(ValueError, match=expected):
                    assert vulnerable.detect_matched([target_obj])
                return
            assert vulnerable.detect_matched([target_obj]) == expected
