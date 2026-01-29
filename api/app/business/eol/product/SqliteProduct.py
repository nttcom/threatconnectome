from .EoLBaseProduct import EoLBaseProduct


class SqliteProduct(EoLBaseProduct):
    def get_packages(self) -> list[str]:
        return ["sqlite-libs", "libsqlite3-0", "libsqlite3-dev"]
