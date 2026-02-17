from app import models

from .AmazonCorrettoProduct import AmazonCorrettoProduct
from .DjangoProduct import DjangoProduct
from .EoLBaseProduct import EoLBaseProduct
from .NumpyProduct import NumpyProduct
from .PhpProduct import PhpProduct
from .PostgresqlProduct import PostgresqlProduct
from .PythonProduct import PythonProduct
from .RedisProduct import RedisProduct
from .RubyProduct import RubyProduct
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
        case "redis":
            return RedisProduct(ecosystem)
        case "django":
            return DjangoProduct(ecosystem)
        case "php":
            return PhpProduct(ecosystem)
        case "python":
            return PythonProduct(ecosystem)
        case "ruby":
            return RubyProduct(ecosystem)
        case "amazon-corretto":
            return AmazonCorrettoProduct(ecosystem)
        case _:
            return EoLBaseProduct(eol_product.matching_name)
