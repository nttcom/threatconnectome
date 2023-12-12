import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Set, TypeAlias, Union

from packaging.version import Version as PypiVersion
from univers.debian import Version as DebianVersion
from univers.versions import SemverVersion


class PackageFamily(Enum):
    UNKNOWN = 0
    DEBIAN = 1
    PYPI = 2

    @classmethod
    def from_registry(cls, registry: str) -> "PackageFamily":
        fixed_registry = registry.lower()
        if re.match(r"^(debian|ubuntu)", fixed_registry):  # TODO: need maintenance
            return cls.DEBIAN
        if re.match(r"^(pypi)", fixed_registry):
            return cls.PYPI
        return cls.UNKNOWN

    @classmethod
    def from_tag_name(cls, tag_name: str) -> "PackageFamily":
        if len(tag_name.split(":", 2)) < 3:
            return cls.UNKNOWN
        registry = tag_name.split(":", 1)[1].rsplit(":", 1)[0]  # trim left most & right most
        return cls.from_registry(registry)


class ExtDebianVersion(DebianVersion):
    def _check_comparable(self, other: Any, operator: str):
        if not isinstance(other, self.__class__):
            raise ValueError(
                f"'{operator}' not supported between instances of '{self.__class__}' "
                f"and '{other.__class__}'"
            )

    # ignore epoch & revision to compare.

    def __lt__(self, other):
        self._check_comparable(other, "<")
        return DebianVersion.from_string(self.upstream) < DebianVersion.from_string(other.upstream)

    def __gt__(self, other):
        self._check_comparable(other, ">")
        return DebianVersion.from_string(self.upstream) > DebianVersion.from_string(other.upstream)

    def __le__(self, other):
        self._check_comparable(other, "<=")
        return DebianVersion.from_string(self.upstream) <= DebianVersion.from_string(other.upstream)

    def __ge__(self, other):
        self._check_comparable(other, ">=")
        return DebianVersion.from_string(self.upstream) >= DebianVersion.from_string(other.upstream)


class ExtPypiVersion(PypiVersion):
    def _check_comparable(self, other: Any, operator: str):
        if not isinstance(other, self.__class__):
            raise ValueError(
                f"'{operator}' not supported between instances of '{self.__class__}' "
                f"and '{other.__class__}'"
            )

    def _remove_epoch(self, version_str: str):
        return re.sub("[0-9]+!", "", version_str)

    # ignore epoch & local to compare.
    # PypiVersion.public is version string without `local`

    def __lt__(self, other):
        self._check_comparable(other, "<")
        return PypiVersion(self._remove_epoch(self.public)) < PypiVersion(
            self._remove_epoch(other.public)
        )

    def __gt__(self, other):
        self._check_comparable(other, ">")
        return PypiVersion(self._remove_epoch(self.public)) > PypiVersion(
            self._remove_epoch(other.public)
        )

    def __le__(self, other):
        self._check_comparable(other, "<=")
        return PypiVersion(self._remove_epoch(self.public)) <= PypiVersion(
            self._remove_epoch(other.public)
        )

    def __ge__(self, other):
        self._check_comparable(other, ">=")
        return PypiVersion(self._remove_epoch(self.public)) >= PypiVersion(
            self._remove_epoch(other.public)
        )


# supported version classes:
#   - should be hashable.
#   - required implemented __gt__, __ge__, __lt__, __le__.
#     Note: __eq__ cannot be used to compare versions. use >= and <= instead.
#   - may raise ValueError on errors.
ComparableVersion: TypeAlias = Union[ExtDebianVersion, ExtPypiVersion, SemverVersion]


def gen_version_instance(
    package_family: PackageFamily,
    version_string: str,
) -> ComparableVersion:
    if package_family == PackageFamily.DEBIAN:
        return ExtDebianVersion.from_string(version_string)
    if package_family == PackageFamily.PYPI:
        return ExtPypiVersion(version_string)
    return SemverVersion(version_string)


@dataclass(frozen=True, kw_only=True)
class VulnerableRange:
    eq: Optional[ComparableVersion] = None
    ge: Optional[ComparableVersion] = None
    gt: Optional[ComparableVersion] = None
    le: Optional[ComparableVersion] = None
    lt: Optional[ComparableVersion] = None

    def __post_init__(self):
        classes = {attr.__class__ for attr in [self.eq, self.ge, self.gt, self.le, self.lt] if attr}
        if (
            len(classes) != 1
            or not any([self.eq, self.ge, self.gt, self.le, self.lt])
            or (self.ge and self.gt)
            or (self.le and self.lt)
            or (self.eq and any([self.ge, self.gt, self.le, self.lt]))
        ):
            raise ValueError(f"Ambiguous {self}")

    @classmethod
    def from_string(
        cls,
        package_family: PackageFamily,
        vulnerable_string: str,
    ) -> "VulnerableRange":
        def _pick_heading_version(string: str) -> str:
            found_string = re.split(r"[<>= ,]", string, maxsplit=1)[0].strip()
            if not found_string:
                raise ValueError("Invalid version string: (empty)")
            return found_string

        kwargs: Dict[str, ComparableVersion] = {}
        if len(tmp := re.split(r">= *", vulnerable_string, maxsplit=1)) > 1:
            kwargs["ge"] = gen_version_instance(package_family, _pick_heading_version(tmp[1]))
        if len(tmp := re.split(r">(?![=]) *", vulnerable_string, maxsplit=1)) > 1:
            kwargs["gt"] = gen_version_instance(package_family, _pick_heading_version(tmp[1]))
        if len(tmp := re.split(r"<= *", vulnerable_string, maxsplit=1)) > 1:
            kwargs["le"] = gen_version_instance(package_family, _pick_heading_version(tmp[1]))
        if len(tmp := re.split(r"<(?![=]) *", vulnerable_string, maxsplit=1)) > 1:
            kwargs["lt"] = gen_version_instance(package_family, _pick_heading_version(tmp[1]))
        if len(tmp := re.split(r"(?<![<>])= *", vulnerable_string, maxsplit=1)) > 1:
            kwargs["eq"] = gen_version_instance(package_family, _pick_heading_version(tmp[1]))
        return VulnerableRange(**kwargs)

    def detect_matched(self, references: Set[ComparableVersion]) -> bool:
        """
        returns True if at least 1 reference matched with me, False otherwise.
        ValueError will be raised when failed to compare.
        """
        if self.eq:
            ret = False
            for reference in references:
                if self.eq.__class__ != reference.__class__:
                    # oops, __eq__ in univers does not raise TypeError even if classes mismatched
                    raise ValueError(
                        f"'==' not supported between instances of '{self.eq.__class__}' "
                        f"and '{reference.__class__}'"
                    )
                # Note:
                #   operator '==' is not reliable to compare versions.
                #   e.g.) SemverVersion.__eq__ returns False if .build are different.
                if self.eq >= reference and self.eq <= reference:
                    ret = True  # found result, but keep on checking to detect ValueError
            return ret

        def _detect_outrange(other) -> bool:
            try:
                return any(
                    [  # Note: TypeError may be raised if classes mismatched
                        (self.lt and self.lt <= other),
                        (self.le and self.le < other),
                        (self.gt and self.gt >= other),
                        (self.ge and self.ge > other),
                    ]
                )
            except TypeError as err:
                raise ValueError(err)

        if all(_detect_outrange(reference) for reference in references):
            return False  # each reference has at least 1 outranged
        return True
