from typing import Any

from univers.debian import Version as DebianVersion


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
