from app import models

from .EoLBaseProduct import EoLBaseProduct
from .RedisProduct import RedisProduct
from .SqliteProduct import SqliteProduct


def gen_product_instance_for_eol(
    eol_product: models.EoLProduct,
) -> EoLBaseProduct:
    match eol_product.name:
        case "sqlite":
            return SqliteProduct(eol_product.matching_name)
        case "redis":
            return RedisProduct(eol_product.matching_name)
        case _:
            return EoLBaseProduct(eol_product.matching_name)
