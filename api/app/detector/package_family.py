import re
from enum import Enum


class PackageFamily(Enum):
    UNKNOWN = 0
    DEBIAN = 1
    PYPI = 2
    NPM = 3
    GO = 4
    RPM = 5

    @classmethod
    def from_registry(cls, registry: str) -> "PackageFamily":
        fixed_registry = registry.lower()
        if re.match(r"^(debian|ubuntu)", fixed_registry):  # TODO: need maintenance
            return cls.DEBIAN
        if re.match(r"^(pypi)", fixed_registry):
            return cls.PYPI
        if re.match(r"^(npm)", fixed_registry):
            return cls.NPM
        if re.match(r"^(golang)", fixed_registry):
            return cls.GO
        if re.match(r"^(rpm)", fixed_registry):
            return cls.RPM
        return cls.UNKNOWN
