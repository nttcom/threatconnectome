from .EoLBaseEcosystem import EoLBaseEcosystem


class EoLAlpineEcosystem(EoLBaseEcosystem):
    def __init__(self, product: str):
        self.product = product

    def match_ecosystem(self, ecosystem: str, eol_version: str) -> bool:
        matching_ecosystem = EoLAlpineEcosystem._get_matching_ecosystem(ecosystem)
        return f"alpine-{eol_version}" == matching_ecosystem

    @staticmethod
    def _get_matching_ecosystem(ecosystem: str) -> str:
        parts = ecosystem.split("-")
        if len(parts) == 2:
            version = parts[1].split(".")
            if len(version) >= 2:
                return f"alpine-{version[0]}.{version[1]}"
        return ecosystem
