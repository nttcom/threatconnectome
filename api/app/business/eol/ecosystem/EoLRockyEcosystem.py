from .EoLBaseEcosystem import EoLBaseEcosystem


class EoLRockyEcosystem(EoLBaseEcosystem):
    def __init__(self, product: str):
        self.product = product

    def match_ecosystem(self, ecosystem: str, eol_version: str) -> bool:
        matching_ecosystem = EoLRockyEcosystem._get_matching_ecosystem(ecosystem)
        return f"rocky-{eol_version}" == matching_ecosystem

    @staticmethod
    def _get_matching_ecosystem(ecosystem: str) -> str:
        parts = ecosystem.split("-")
        if len(parts) == 2:
            version = parts[1].split(".")
            if len(version) >= 1:
                return f"rocky-{version[0]}"
        return ecosystem
