import pytest
from fastapi import HTTPException, status

from app.common import VulnerableVersion, check_topic_action_tags_integrity


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


class TestVulnerableVersion:
    class TestFromStrings:
        @pytest.mark.parametrize(
            "strings",
            [
                ["=2.0"],
                ["= 2.0"],
                [" =2.0"],
                [" = 2.0"],
                ["=2.0 xxx"],  # garbage separated with space
                ["xxx =2.0"],
                ["=2.0", " = 2.0"],  # duplicated
            ],
        )
        def test_from_strings_eq(self, strings):
            assert VulnerableVersion.from_strings(strings) == [VulnerableVersion(eq="2.0")]

        @pytest.mark.parametrize(
            "strings",
            [
                [">=2.0"],
                [">= 2.0"],
                [" >=2.0"],
                [" >= 2.0"],
                [">=2.0 xxx"],
                ["xxx >=2.0"],
                [">=2.0", " >= 2.0"],
            ],
        )
        def test_from_strings_ge(self, strings):
            assert VulnerableVersion.from_strings(strings) == [VulnerableVersion(ge="2.0")]

        @pytest.mark.parametrize(
            "strings",
            [
                [">2.0"],
                ["> 2.0"],
                [" >2.0"],
                [" > 2.0"],
                [">2.0 xxx"],
                ["xxx >2.0"],
                [">2.0", " > 2.0"],
            ],
        )
        def test_from_strings_gt(self, strings):
            assert VulnerableVersion.from_strings(strings) == [VulnerableVersion(gt="2.0")]

        @pytest.mark.parametrize(
            "strings",
            [
                ["<=2.0"],
                ["<= 2.0"],
                [" <=2.0"],
                [" <= 2.0"],
                ["<=2.0 xxx"],
                ["xxx <=2.0"],
                ["<=2.0", " <= 2.0"],
            ],
        )
        def test_from_strings_le(self, strings):
            assert VulnerableVersion.from_strings(strings) == [VulnerableVersion(le="2.0")]

        @pytest.mark.parametrize(
            "strings",
            [
                ["<2.0"],
                ["< 2.0"],
                [" <2.0"],
                [" < 2.0"],
                ["<2.0 xxx"],
                ["xxx <2.0"],
                ["<2.0", " < 2.0"],
            ],
        )
        def test_from_strings_lt(self, strings):
            assert VulnerableVersion.from_strings(strings) == [VulnerableVersion(lt="2.0")]

        @pytest.mark.parametrize(
            "strings",
            [
                [">=2.0 <3.0"],
                [">=2.0,<3.0"],
                [">=2.0, <3.0"],
                [">=2.0 ,<3.0"],
                [">=2.0 , <3.0"],
                [">=2.0,,,<3.0"],
                [">=2.0 <3.0", ">=2.0,<3.0"],
            ],
        )
        def test_from_strings_complex1(self, strings):
            assert VulnerableVersion.from_strings(strings) == [
                VulnerableVersion(ge="2.0", lt="3.0")
            ]

        @pytest.mark.parametrize(
            "strings",
            [
                [""],  # empty
                ["=2.0 <2.0"],  # eq with others
                ["=2.0 <=2.0"],
                ["=2.0 >2.0"],
                ["=2.0 >=2.0"],
                [">2.0 >=2.0"],  # ge with gt
                ["<2.0 <=2.0"],  # le with lt
            ],
        )
        def test_from_strings_ambiguous(self, strings):
            with pytest.raises(ValueError, match=r"Ambiguous VulnerableVersion\("):
                VulnerableVersion.from_strings(strings)

        @pytest.mark.parametrize(
            "strings",
            [
                [">=2.0 <2.1", ">=3.3 <3.3.3"],
                [">=2.0 <2.1 || >=3.3 <3.3.3"],
                [">=2.0 <2.1|| >=3.3 <3.3.3"],
                [">=2.0 <2.1 ||>=3.3 <3.3.3"],
                [">=2.0 <2.1||>=3.3 <3.3.3"],
            ],
        )
        def test_from_strings_multiple(self, strings):
            assert set(VulnerableVersion.from_strings(strings)) == {
                VulnerableVersion(ge="2.0", lt="2.1"),
                VulnerableVersion(ge="3.3", lt="3.3.3"),
            }

    class TestCompareVersions:
        @pytest.mark.parametrize(
            "ver_a, ver_b",
            [
                # starts with number
                ("1", "1"),
                ("1", "1."),
                ("1", "1.0"),
                ("1", "1.0."),
                ("1", "1.0.0"),
                ("1.0", "1.0"),
                ("1.0", "1.0."),
                ("1.0", "1.0.0"),
                ("1.0.0", "1.0.0"),
                # starts with not number
                ("v1", "v1"),
                ("v1", "v1."),
                ("v1", "v1.0"),
                ("v1", "v1.0."),
                ("v1", "v1.0.0"),
                ("v1.0", "v1.0"),
                ("v1.0", "v1.0."),
                ("v1.0", "v1.0.0"),
                ("v1.0.0", "v1.0.0"),
            ],
        )
        def test_eq(self, ver_a, ver_b):
            assert VulnerableVersion._compare_versions(ver_a, ver_b) == 0

        @pytest.mark.parametrize(
            "ver_a, ver_b",
            [
                # starts with number
                ("2", "1"),
                ("1.1", "1"),
                ("1.1.", "1"),
                ("1.0.1", "1"),
                ("1.1", "1.0"),
                ("1.1.", "1.0"),
                ("1.0.1", "1.0"),
                ("1.0.1", "1.0.0"),
                ("2.1", "1.0"),
                ("2.1", "1.1"),
                ("2.1", "1.2"),
                # starts with not number
                ("v2", "v1"),
                ("v1.1", "v1"),
                ("v1.1.", "v1"),
                ("v1.0.1", "v1"),
                ("v1.1", "v1.0"),
                ("v1.1.", "v1.0"),
                ("v1.0.1", "v1.0"),
                ("v1.0.1", "v1.0.0"),
                ("v2.1", "v1.0"),
                ("v2.1", "v1.1"),
                ("v2.1", "v1.2"),
            ],
        )
        def test_gt(self, ver_a, ver_b):
            assert VulnerableVersion._compare_versions(ver_a, ver_b) > 0

        @pytest.mark.parametrize(
            "ver_a, ver_b",
            [
                # starts with number
                ("1", "2"),
                ("1", "1.1"),
                ("1", "1.1."),
                ("1", "1.0.1"),
                ("1.0", "1.1"),
                ("1.0", "1.1."),
                ("1.0", "1.0.1"),
                ("1.0.0", "1.0.1"),
                ("1.0", "2.1"),
                ("1.1", "2.1"),
                ("1.2", "2.1"),
                # starts with not number
                ("v1", "v2"),
                ("v1", "v1.1"),
                ("v1", "v1.1."),
                ("v1", "v1.0.1"),
                ("v1.0", "v1.1"),
                ("v1.0", "v1.1."),
                ("v1.0", "v1.0.1"),
                ("v1.0.0", "v1.0.1"),
                ("v1.0", "v2.1"),
                ("v1.1", "v2.1"),
                ("v1.2", "v2.1"),
            ],
        )
        def test_lt(self, ver_a, ver_b):
            assert VulnerableVersion._compare_versions(ver_a, ver_b) < 0

        @pytest.mark.parametrize(
            "ver_a, ver_b",
            [
                # empty
                ("0", None),
                ("0", ""),
                (None, None),
                ("", ""),
                # delimiter mismatch (any of not number are delimiter)
                ("0.0", "0-0"),
                ("0.0x86_64", "0.0noarch"),
                ("a", "b"),
                ("0", "v0"),
                ("x0", "v0"),
                ("1.1x0", "2.0.0"),
                ("2.1x0", "1.0.0"),
            ],
        )
        def test_uncomparable(self, ver_a, ver_b):
            with pytest.raises(ValueError, match=r"Cannot compare "):
                VulnerableVersion._compare_versions(ver_a, ver_b)

    class TestMatch:
        @staticmethod
        def _test_sequence(reference_versions, strings, expected):
            vuln_vers = VulnerableVersion.from_strings(strings)
            if expected is None:
                with pytest.raises(ValueError, match="Cannot compare "):
                    for vuln_ver in vuln_vers:
                        vuln_ver.match(reference_versions)
            else:
                assert any(vuln_ver.match(reference_versions) for vuln_ver in vuln_vers) == expected

        @pytest.mark.parametrize(
            "reference_versions, strings, expected",  # expected: None for Exception
            [
                (["2.0"], ["=2"], True),
                (["2.0"], [">=2"], True),
                (["2.0"], [">2"], False),
                (["2.0"], ["<=2"], True),
                (["2.0"], ["<2"], False),
                (["2.0"], ["=v2"], None),
                (["2.1"], [">=2.0 <3"], True),
                (["2.1"], [">=2.0 <2.0.9"], False),
                (["2.1"], [">=2.0 <2.2 || >=3.1 <3.3"], True),
                (["2.1"], [">=2.0 <2.1 || >2.1 <2.9"], False),
                (["2.1"], [">=2.0 <2.1 || >v2.1 <v2.9"], None),
            ],
        )
        def test_single_reference_version(self, reference_versions, strings, expected):
            self._test_sequence(reference_versions, strings, expected)

        @pytest.mark.parametrize(
            "reference_versions, strings, expected",  # expected: None for Exception
            [
                (["1.0", "2.0"], ["=2"], True),
                (["1.0", "3.0"], ["=2"], False),
                (["1.0", "v3.0"], ["=2"], None),
                (["1.0", "2.0"], [">=2"], True),
                (["1.0", "1.5"], [">=2"], False),
                (["1.0", "1.5"], [">=2r0"], None),
                (["1.0", "3.0"], [">2"], True),
                (["1.0", "2.0"], [">2"], False),
                (["3.0", "2.0"], ["<=2"], True),
                (["3.0", "2.5"], ["<=2"], False),
                (["1.0", "3.0"], ["<2"], True),
                (["3.0", "2.0"], ["<2"], False),
                (["2.1", "2.9"], [">=2.1 <2.3"], True),
                (["2.1", "2.9"], [">=2.2 <2.3"], False),
                (["2.1", "v2.9"], [">=2.2 <2.3"], None),
                (["2.1", "2.9"], [">=v2.2 <v2.3"], None),
                (["2.1", "2.9"], [">1.0 <2.0 || >=2.1 <2.3"], True),
                (["2.1", "2.9"], [">1.0 <2.0 || >=2.2 <2.3"], False),
                (["2.1", "v2.9"], [">1.0 <2.0 || >=2.1 <2.3"], None),
                (["2.1", "2.9"], [">v1.0 <v2.0 || >=2.1 <2.3"], None),
                (["2.1", "1.9"], [">1.0 <2.0 || >=2.1 <2.3"], True),
            ],
        )
        def test_multiple_reference_versions(self, reference_versions, strings, expected):
            self._test_sequence(reference_versions, strings, expected)

        @pytest.mark.parametrize(
            "reference_versions, strings, expected",  # expected: None for Exception
            [  # see https://semver.org/lang/ja/
                (["1.0.0-alpha"], ["<1.0.0"], False),
                (["1.0.0-alpha"], ["<=1.0.0"], True),
                (["1.0.0-alpha"], ["=1.0.0"], True),
                (["1.0.0-alpha"], [">1.0.0"], False),
                (["1.0.0-alpha"], ["<1.0.1"], True),
                (["1.0.0-alpha"], ["=1.0.0-beta"], None),  # "-alpha" != "-beta"
                (["1.0.0-alpha"], ["<1.0.0-beta"], None),
                (["1.0.0-beta"], ["<1.0.0-alpha"], None),
                (["1.0.0-beta"], ["<=1.0.0-alpha"], None),
                (["1.0.0-alpha"], ["<=1.0.1-beta"], None),
                (["1.0.0-alpha.1"], ["<1.0.0-alpha"], None),  # "-alpha." != "-alpha"
                (["1.0.0-alpha.1"], ["<=1.0.0-alpha"], None),
                (["1.0.0-alpha.1"], ["<=1.0.1-alpha"], None),
                (["1.0.0-alpha.1+001"], ["=1.0.0-alpha.1+100"], False),
                (["1.0.0-alpha.1+001"], ["<1.0.0-alpha.1+005"], True),
                (["1.0.0-alpha.1+001"], ["<1.0.1-alpha.1+001"], True),
            ],
        )
        def test_common_semver(self, reference_versions, strings, expected):
            self._test_sequence(reference_versions, strings, expected)
