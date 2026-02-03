from app import models

from .DjangoProduct import DjangoProduct
from .EoLBaseProduct import EoLBaseProduct
from .NumpyProduct import NumpyProduct
from .PostgresqlProduct import PostgresqlProduct
from .RedisProduct import RedisProduct
from .SqliteProduct import SqliteProduct


def gen_product_instance_for_eol(
    eol_product: models.EoLProduct,
    ecosystem: str,
) -> EoLBaseProduct:
    match eol_product.name:
        case "sqlite":
            return SqliteProduct(ecosystem)
        case "postgresql":
            return PostgresqlProduct(ecosystem)
        case "numpy":
            return NumpyProduct(ecosystem)
        case "django":
            return DjangoProduct(ecosystem)
        case "redis":
            return RedisProduct(ecosystem)
        case _:
            return EoLBaseProduct(eol_product.matching_name)
