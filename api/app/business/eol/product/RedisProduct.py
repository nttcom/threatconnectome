from .EoLBaseProduct import EoLBaseProduct


class RedisProduct(EoLBaseProduct):
    def get_packages(self) -> list[str]:
        return ["redis", "redis-server"]
