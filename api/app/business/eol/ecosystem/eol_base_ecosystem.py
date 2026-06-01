class EoLBaseEcosystem:
    def __init__(self, product: str):
        self.product = product

    def match_ecosystem(self, ecosystem: str, eol_version: str) -> bool:
        return f"{self.product}-{eol_version}" == ecosystem
