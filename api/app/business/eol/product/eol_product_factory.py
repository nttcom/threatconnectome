from app import models

from .amazon_corretto_product import AmazonCorrettoProduct
from .apache_http_server_product import ApacheHttpServerProduct
from .containerd_product import ContainerdProduct
from .django_product import DjangoProduct
from .eol_base_product import EoLBaseProduct
from .log4j_product import Log4jProduct
from .numpy_product import NumpyProduct
from .php_product import PhpProduct
from .postgresql_product import PostgresqlProduct
from .python_product import PythonProduct
from .redis_product import RedisProduct
from .ruby_product import RubyProduct
from .sqlite_product import SqliteProduct


def gen_product_instance_for_eol(
    eol_product: models.EoLProduct,
    ecosystem: str,
) -> EoLBaseProduct:
    match eol_product.name:
        case "apache-http-server":
            return ApacheHttpServerProduct(ecosystem)
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
        case "log4j":
            return Log4jProduct(ecosystem)
        case "containerd":
            return ContainerdProduct(ecosystem)
        case _:
            return EoLBaseProduct(eol_product.name)
