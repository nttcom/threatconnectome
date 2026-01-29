class EoLBaseProduct:
    def __init__(self, product: str):
        self.product = product

    def get_packages(self) -> list[str]:
        return [self.product]
