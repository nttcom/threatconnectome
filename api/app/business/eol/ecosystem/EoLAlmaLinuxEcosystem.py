from .EoLBaseEcosystem import EoLBaseEcosystem


class EoLAlmaLinuxEcosystem(EoLBaseEcosystem):
    def __init__(self, product: str):
        self.product = product

    def match_ecosystem(self, ecosystem: str, eol_version: str) -> bool:
        matching_ecosystem = EoLAlmaLinuxEcosystem._get_matching_ecosystem(ecosystem)
        return f"alma-{eol_version}" == matching_ecosystem

    @staticmethod
    def _get_matching_ecosystem(ecosystem: str) -> str:
        parts = ecosystem.split("-")
        if len(parts) == 2:
            version = parts[1].split(".")
            if len(version) >= 1:
                return f"alma-{version[0]}"
        return ecosystem
