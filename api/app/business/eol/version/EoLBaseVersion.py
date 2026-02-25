class EoLBaseVersion:
    def __init__(self, version: str):
        self.version = version

    def get_versions(self) -> list[str]:
        return [self.version]
