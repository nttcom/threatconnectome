from dataclasses import dataclass, field


@dataclass
class Artifact:
    tag: str
    targets: set[tuple[str, str]] = field(init=False, repr=False, default_factory=set)
    versions: set[str] = field(init=False, repr=False, default_factory=set)  # for missing targets

    def to_json(self) -> dict:
        targets = self.targets if self.targets else {("", version) for version in self.versions}
        return {
            "tag_name": self.tag,
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
