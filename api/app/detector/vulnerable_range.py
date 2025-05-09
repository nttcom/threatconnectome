import re
from dataclasses import dataclass

from app.detector.package_family import PackageFamily
from app.detector.version import version_factory
from app.detector.version.version_factory import ComparableVersion


@dataclass(frozen=True, kw_only=True)
class VulnerableRange:
    eq: ComparableVersion | None = None
    ge: ComparableVersion | None = None
    gt: ComparableVersion | None = None
    le: ComparableVersion | None = None
    lt: ComparableVersion | None = None

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

        kwargs: dict[str, ComparableVersion] = {}
        if len(tmp := re.split(r">= *", vulnerable_string, maxsplit=1)) > 1:
            kwargs["ge"] = version_factory.gen_version_instance(
                package_family, _pick_heading_version(tmp[1])
            )
        if len(tmp := re.split(r">(?![=]) *", vulnerable_string, maxsplit=1)) > 1:
            kwargs["gt"] = version_factory.gen_version_instance(
                package_family, _pick_heading_version(tmp[1])
            )
        if len(tmp := re.split(r"<= *", vulnerable_string, maxsplit=1)) > 1:
            kwargs["le"] = version_factory.gen_version_instance(
                package_family, _pick_heading_version(tmp[1])
            )
        if len(tmp := re.split(r"<(?![=]) *", vulnerable_string, maxsplit=1)) > 1:
            kwargs["lt"] = version_factory.gen_version_instance(
                package_family, _pick_heading_version(tmp[1])
            )
        if len(tmp := re.split(r"(?<![<>])= *", vulnerable_string, maxsplit=1)) > 1:
            kwargs["eq"] = version_factory.gen_version_instance(
                package_family, _pick_heading_version(tmp[1])
            )
        return VulnerableRange(**kwargs)

    def detect_matched(self, references: set[ComparableVersion]) -> bool:
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
