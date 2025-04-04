import re
from typing import Any

from packaging.version import Version as PypiVersion


class ExtPypiVersion(PypiVersion):
    def _check_comparable(self, other: Any, operator: str):
        if not isinstance(other, self.__class__):
            raise ValueError(
                f"'{operator}' not supported between instances of '{self.__class__}' "
                f"and '{other.__class__}'"
            )

    @staticmethod
    def _remove_epoch(version_str: str):
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
