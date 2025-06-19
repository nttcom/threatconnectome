from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Artifact:
    package_name: str
    ecosystem: str
    package_manager: str
    source_name: Optional[str] = None
    targets: set[tuple[str, str]] = field(init=False, repr=False, default_factory=set)
    versions: set[str] = field(init=False, repr=False, default_factory=set)  # for missing targets

    def to_json(self) -> dict:
        targets = self.targets if self.targets else {("", version) for version in self.versions}
        return {
            "package_name": self.package_name,
            "ecosystem": self.ecosystem,
            "package_manager": self.package_manager,
            "source_name": self.source_name,
            "references": sorted(
                [
                    {
                        "version": version,
                        "target": target,
                    }
                    for (target, version) in targets
                ],
                key=lambda x: (x["version"], x["target"]),
            ),
        }
