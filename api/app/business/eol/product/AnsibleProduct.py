from .EoLBaseProduct import EoLBaseProduct


class AnsibleProduct(EoLBaseProduct):
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem

    def match_package(self, package_name: str, package_version: str) -> bool:
        return package_name == "ansible"
