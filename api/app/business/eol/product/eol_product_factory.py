from app import models

from .EoLBaseProduct import EoLBaseProduct
from .PostgresqlProduct import PostgresqlProduct
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
        case _:
            return EoLBaseProduct(eol_product.matching_name)
