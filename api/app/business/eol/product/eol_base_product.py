class EoLBaseProduct:
    def __init__(self, product: str):
        self.product = product

    def match_package(self, package_name: str, package_version: str) -> bool:
        return self.product == package_name
